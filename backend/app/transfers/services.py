"""
Transfer Service
Handles transfer business logic and operations
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from app.transfers.models import Transfer, TransferEvent, TransferStatus, TransferPriority, TransferType
from app.accounts.models import Account, AccountActivity
from app.auth.models import User
from app.common.exceptions import TransferError, InsufficientFundsError, ValidationError
from app.connectors.swift_connector import create_swift_connector
from app.connectors.mojaloop_connector import create_mojaloop_connector
from app.connectors.iso20022_connector import create_iso20022_connector
from app.common.monitoring import record_transfer

logger = logging.getLogger(__name__)

class TransferService:
    """Service for managing transfers"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_transfer(self, user_id: str, transfer_data: Dict[str, Any]) -> Transfer:
        """Create a new transfer"""
        try:
            # Validate source account
            source_account = self.db.query(Account).filter(
                and_(
                    Account.id == transfer_data['source_account_id'],
                    Account.user_id == user_id,
                    Account.status == 'active'
                )
            ).first()
            
            if not source_account:
                raise ValidationError("Invalid source account")
            
            # Validate amount and limits
            amount = transfer_data['amount']
            if amount <= 0:
                raise ValidationError("Amount must be positive")
            
            if amount > source_account.balance:
                raise InsufficientFundsError(f"Insufficient funds. Available: ${source_account.balance}")
            
            if amount > source_account.daily_limit:
                raise ValidationError(f"Amount exceeds daily limit of ${source_account.daily_limit}")
            
            # Check monthly limit
            monthly_transfers = self.db.query(func.sum(Transfer.amount)).filter(
                and_(
                    Transfer.source_account_id == source_account.id,
                    Transfer.created_at >= datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                )
            ).scalar() or 0
            
            if monthly_transfers + amount > source_account.monthly_limit:
                raise ValidationError(f"Amount would exceed monthly limit of ${source_account.monthly_limit}")
            
            # Generate transfer ID
            transfer_id = f"TRF{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
            
            # Calculate fees
            fees = self._calculate_fees(amount, transfer_data['transfer_type'], transfer_data['priority'])
            
            # Create transfer
            transfer = Transfer(
                id=str(uuid.uuid4()),
                transfer_id=transfer_id,
                amount=amount,
                currency=transfer_data['currency'],
                source_account_id=source_account.id,
                destination_account_id=None,  # Will be set when destination account is found
                beneficiary_name=transfer_data['beneficiary_name'],
                beneficiary_iban=transfer_data['beneficiary_iban'],
                beneficiary_bic=transfer_data['beneficiary_bic'],
                description=transfer_data['description'],
                status=TransferStatus.INITIATED,
                priority=transfer_data['priority'],
                transfer_type=transfer_data['transfer_type'],
                fees=fees,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            
            self.db.add(transfer)
            self.db.flush()  # Get the ID
            
            # Block amount from source account
            source_account.block_amount(amount)
            
            # Create initial event
            event = TransferEvent(
                id=str(uuid.uuid4()),
                transfer_id=transfer.id,
                event_type="transfer_initiated",
                status=TransferStatus.INITIATED,
                message="Transfer initiated",
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "amount": amount,
                    "currency": transfer_data['currency'],
                    "fees": fees
                }
            )
            
            self.db.add(event)
            self.db.commit()
            
            # Record metrics
            record_transfer("created", "success")
            
            # Process transfer asynchronously
            await self._process_transfer(transfer)
            
            return transfer
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create transfer: {e}")
            record_transfer("created", "failed")
            raise
    
    async def _process_transfer(self, transfer: Transfer) -> None:
        """Process transfer based on type"""
        try:
            if transfer.transfer_type == TransferType.SWIFT:
                await self._process_swift_transfer(transfer)
            elif transfer.transfer_type == TransferType.MOJALOOP:
                await self._process_mojaloop_transfer(transfer)
            elif transfer.transfer_type == TransferType.IBAN:
                await self._process_iban_transfer(transfer)
            else:
                raise TransferError(f"Unsupported transfer type: {transfer.transfer_type}")
                
        except Exception as e:
            logger.error(f"Failed to process transfer {transfer.transfer_id}: {e}")
            await self._fail_transfer(transfer, str(e))
    
    async def _process_swift_transfer(self, transfer: Transfer) -> None:
        """Process SWIFT transfer"""
        try:
            # Update status
            transfer.status = TransferStatus.PROCESSING
            transfer.updated_at = datetime.now(timezone.utc)
            
            # Create SWIFT message
            swift_connector = await create_swift_connector()
            async with swift_connector:
                swift_message = swift_connector.create_mt103_message(transfer)
                result = await swift_connector.send_message(swift_message)
                
                transfer.swift_message_id = result.get('message_id')
                transfer.status = TransferStatus.PENDING
                transfer.updated_at = datetime.now(timezone.utc)
                
                # Create event
                event = TransferEvent(
                    id=str(uuid.uuid4()),
                    transfer_id=transfer.id,
                    event_type="swift_message_sent",
                    status=TransferStatus.PENDING,
                    message="SWIFT message sent",
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "swift_message_id": result.get('message_id'),
                        "acknowledgment": result.get('acknowledgment')
                    }
                )
                
                self.db.add(event)
                self.db.commit()
                
        except Exception as e:
            logger.error(f"SWIFT transfer processing failed: {e}")
            raise TransferError(f"SWIFT processing failed: {e}")
    
    async def _process_mojaloop_transfer(self, transfer: Transfer) -> None:
        """Process Mojaloop transfer"""
        try:
            # Update status
            transfer.status = TransferStatus.PROCESSING
            transfer.updated_at = datetime.now(timezone.utc)
            
            # Create Mojaloop transfer
            mojaloop_connector = await create_mojaloop_connector()
            async with mojaloop_connector:
                # Create quote
                quote = await mojaloop_connector.create_quote(transfer)
                
                # Initiate transfer
                result = await mojaloop_connector.initiate_transfer(transfer, quote['quoteId'])
                
                transfer.mojaloop_transfer_id = result.get('transferId')
                transfer.status = TransferStatus.PENDING
                transfer.updated_at = datetime.now(timezone.utc)
                
                # Create event
                event = TransferEvent(
                    id=str(uuid.uuid4()),
                    transfer_id=transfer.id,
                    event_type="mojaloop_transfer_initiated",
                    status=TransferStatus.PENDING,
                    message="Mojaloop transfer initiated",
                    timestamp=datetime.now(timezone.utc),
                    metadata={
                        "mojaloop_transfer_id": result.get('transferId'),
                        "quote_id": quote['quoteId']
                    }
                )
                
                self.db.add(event)
                self.db.commit()
                
        except Exception as e:
            logger.error(f"Mojaloop transfer processing failed: {e}")
            raise TransferError(f"Mojaloop processing failed: {e}")
    
    async def _process_iban_transfer(self, transfer: Transfer) -> None:
        """Process IBAN transfer"""
        try:
            # Update status
            transfer.status = TransferStatus.PROCESSING
            transfer.updated_at = datetime.now(timezone.utc)
            
            # For IBAN transfers, we'll simulate processing
            # In a real implementation, this would connect to the destination bank
            
            # Create ISO 20022 message
            iso_connector = create_iso20022_connector()
            iso_message = iso_connector.create_pacs008_message(transfer)
            
            transfer.status = TransferStatus.PENDING
            transfer.updated_at = datetime.now(timezone.utc)
            
            # Create event
            event = TransferEvent(
                id=str(uuid.uuid4()),
                transfer_id=transfer.id,
                event_type="iban_transfer_initiated",
                status=TransferStatus.PENDING,
                message="IBAN transfer initiated",
                timestamp=datetime.now(timezone.utc),
                metadata={
                    "iso_message_id": iso_message.message_id,
                    "beneficiary_iban": transfer.beneficiary_iban
                }
            )
            
            self.db.add(event)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"IBAN transfer processing failed: {e}")
            raise TransferError(f"IBAN processing failed: {e}")
    
    async def _fail_transfer(self, transfer: Transfer, reason: str) -> None:
        """Mark transfer as failed"""
        try:
            transfer.status = TransferStatus.FAILED
            transfer.updated_at = datetime.now(timezone.utc)
            
            # Unblock amount from source account
            source_account = self.db.query(Account).filter(Account.id == transfer.source_account_id).first()
            if source_account:
                source_account.unblock_amount(transfer.amount)
            
            # Create event
            event = TransferEvent(
                id=str(uuid.uuid4()),
                transfer_id=transfer.id,
                event_type="transfer_failed",
                status=TransferStatus.FAILED,
                message=f"Transfer failed: {reason}",
                timestamp=datetime.now(timezone.utc),
                metadata={"reason": reason}
            )
            
            self.db.add(event)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to mark transfer as failed: {e}")
            self.db.rollback()
    
    def get_transfers(self, user_id: str, page: int = 1, per_page: int = 20, filters: Optional[Dict] = None) -> List[Transfer]:
        """Get user transfers with filtering and pagination"""
        try:
            query = self.db.query(Transfer).join(Account).filter(Account.user_id == user_id)
            
            if filters:
                if filters.get('status'):
                    query = query.filter(Transfer.status == filters['status'])
                if filters.get('transfer_type'):
                    query = query.filter(Transfer.transfer_type == filters['transfer_type'])
                if filters.get('priority'):
                    query = query.filter(Transfer.priority == filters['priority'])
                if filters.get('currency'):
                    query = query.filter(Transfer.currency == filters['currency'])
            
            # Apply pagination
            offset = (page - 1) * per_page
            transfers = query.order_by(desc(Transfer.created_at)).offset(offset).limit(per_page).all()
            
            return transfers
            
        except Exception as e:
            logger.error(f"Failed to get transfers: {e}")
            raise TransferError(f"Failed to retrieve transfers: {e}")
    
    def get_transfer(self, transfer_id: str, user_id: str) -> Optional[Transfer]:
        """Get a specific transfer by ID"""
        try:
            transfer = self.db.query(Transfer).join(Account).filter(
                and_(
                    Transfer.id == transfer_id,
                    Account.user_id == user_id
                )
            ).first()
            
            return transfer
            
        except Exception as e:
            logger.error(f"Failed to get transfer: {e}")
            raise TransferError(f"Failed to retrieve transfer: {e}")
    
    def get_transfer_events(self, transfer_id: str, user_id: str) -> List[TransferEvent]:
        """Get events for a specific transfer"""
        try:
            # Verify user owns the transfer
            transfer = self.get_transfer(transfer_id, user_id)
            if not transfer:
                return []
            
            events = self.db.query(TransferEvent).filter(
                TransferEvent.transfer_id == transfer_id
            ).order_by(TransferEvent.timestamp).all()
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to get transfer events: {e}")
            raise TransferError(f"Failed to retrieve transfer events: {e}")
    
    async def cancel_transfer(self, transfer_id: str, user_id: str, reason: str) -> None:
        """Cancel a transfer"""
        try:
            transfer = self.get_transfer(transfer_id, user_id)
            if not transfer:
                raise ValidationError("Transfer not found")
            
            if transfer.status not in [TransferStatus.INITIATED, TransferStatus.PENDING]:
                raise TransferError("Cannot cancel transfer in current status")
            
            # Update transfer status
            transfer.status = TransferStatus.CANCELLED
            transfer.updated_at = datetime.now(timezone.utc)
            
            # Unblock amount from source account
            source_account = self.db.query(Account).filter(Account.id == transfer.source_account_id).first()
            if source_account:
                source_account.unblock_amount(transfer.amount)
            
            # Create event
            event = TransferEvent(
                id=str(uuid.uuid4()),
                transfer_id=transfer.id,
                event_type="transfer_cancelled",
                status=TransferStatus.CANCELLED,
                message=f"Transfer cancelled: {reason}",
                timestamp=datetime.now(timezone.utc),
                metadata={"reason": reason}
            )
            
            self.db.add(event)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to cancel transfer: {e}")
            self.db.rollback()
            raise TransferError(f"Failed to cancel transfer: {e}")
    
    def _calculate_fees(self, amount: float, transfer_type: TransferType, priority: TransferPriority) -> float:
        """Calculate transfer fees"""
        base_fee = 0.0
        
        if transfer_type == TransferType.SWIFT:
            base_fee = 25.0
        elif transfer_type == TransferType.MOJALOOP:
            base_fee = 2.0
        elif transfer_type == TransferType.IBAN:
            base_fee = 5.0
        
        # Priority fees
        if priority == TransferPriority.URGENT:
            base_fee *= 1.5
        elif priority == TransferPriority.EXPRESS:
            base_fee *= 2.0
        
        # Amount-based fees (0.1% for amounts over $1000)
        if amount > 1000:
            base_fee += amount * 0.001
        
        return round(base_fee, 2)
    
    def get_user_transfer_stats(self, user_id: str) -> Dict[str, Any]:
        """Get transfer statistics for user"""
        try:
            # Get user accounts
            accounts = self.db.query(Account).filter(Account.user_id == user_id).all()
            account_ids = [acc.id for acc in accounts]
            
            if not account_ids:
                return {
                    "total_transfers": 0,
                    "total_amount": 0,
                    "pending_transfers": 0,
                    "completed_transfers": 0,
                    "failed_transfers": 0,
                    "currency": "USD"
                }
            
            # Calculate statistics
            total_transfers = self.db.query(func.count(Transfer.id)).filter(
                Transfer.source_account_id.in_(account_ids)
            ).scalar() or 0
            
            total_amount = self.db.query(func.sum(Transfer.amount)).filter(
                Transfer.source_account_id.in_(account_ids)
            ).scalar() or 0
            
            pending_transfers = self.db.query(func.count(Transfer.id)).filter(
                and_(
                    Transfer.source_account_id.in_(account_ids),
                    Transfer.status.in_([TransferStatus.INITIATED, TransferStatus.PROCESSING, TransferStatus.PENDING])
                )
            ).scalar() or 0
            
            completed_transfers = self.db.query(func.count(Transfer.id)).filter(
                and_(
                    Transfer.source_account_id.in_(account_ids),
                    Transfer.status == TransferStatus.COMPLETED
                )
            ).scalar() or 0
            
            failed_transfers = self.db.query(func.count(Transfer.id)).filter(
                and_(
                    Transfer.source_account_id.in_(account_ids),
                    Transfer.status == TransferStatus.FAILED
                )
            ).scalar() or 0
            
            return {
                "total_transfers": total_transfers,
                "total_amount": total_amount,
                "pending_transfers": pending_transfers,
                "completed_transfers": completed_transfers,
                "failed_transfers": failed_transfers,
                "currency": "USD"
            }
            
        except Exception as e:
            logger.error(f"Failed to get transfer stats: {e}")
            raise TransferError(f"Failed to retrieve transfer statistics: {e}")
    
    def get_transfer_chart_data(self, user_id: str, period: str = "7d") -> List[Dict[str, Any]]:
        """Get transfer chart data for user"""
        try:
            # Get user accounts
            accounts = self.db.query(Account).filter(Account.user_id == user_id).all()
            account_ids = [acc.id for acc in accounts]
            
            if not account_ids:
                return []
            
            # Calculate date range
            from datetime import timedelta
            end_date = datetime.now(timezone.utc)
            
            if period == "1d":
                start_date = end_date - timedelta(days=1)
                group_by = func.date_trunc('hour', Transfer.created_at)
            elif period == "7d":
                start_date = end_date - timedelta(days=7)
                group_by = func.date_trunc('day', Transfer.created_at)
            elif period == "30d":
                start_date = end_date - timedelta(days=30)
                group_by = func.date_trunc('day', Transfer.created_at)
            else:
                start_date = end_date - timedelta(days=7)
                group_by = func.date_trunc('day', Transfer.created_at)
            
            # Query transfer data
            results = self.db.query(
                group_by.label('date'),
                func.count(Transfer.id).label('count'),
                func.sum(Transfer.amount).label('amount')
            ).filter(
                and_(
                    Transfer.source_account_id.in_(account_ids),
                    Transfer.created_at >= start_date,
                    Transfer.created_at <= end_date
                )
            ).group_by(group_by).order_by(group_by).all()
            
            # Format results
            chart_data = []
            for result in results:
                chart_data.append({
                    "date": result.date.isoformat(),
                    "count": result.count,
                    "amount": float(result.amount or 0),
                    "currency": "USD"
                })
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Failed to get transfer chart data: {e}")
            raise TransferError(f"Failed to retrieve transfer chart data: {e}")