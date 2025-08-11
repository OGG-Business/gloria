"""
Transfer service for Banking Transfer Platform
"""

import uuid
import asyncio
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
import structlog

from app.transfers.models import Transfer, TransferEvent, TransferStatus, TransferType, TransferPriority
from app.accounts.models import Account, AccountActivity
from app.auth.models import User
from app.connectors.swift_connector import create_swift_connector
from app.connectors.mojaloop_connector import create_mojaloop_connector
from app.connectors.iso20022_connector import create_iso20022_connector
from app.common.monitoring import record_transfer

logger = structlog.get_logger()

class TransferService:
    """Service for handling transfer operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_transfer(self, transfer_data: dict, user: User) -> Transfer:
        """Create a new transfer"""
        try:
            # Validate transfer data
            validation_result = await self.validate_transfer(transfer_data, user)
            if not validation_result["valid"]:
                raise ValueError(f"Transfer validation failed: {validation_result['errors']}")
            
            # Get source account
            source_account = self.db.query(Account).filter(
                and_(
                    Account.id == transfer_data["source_account_id"],
                    Account.user_id == user.id,
                    Account.status == "active"
                )
            ).first()
            
            if not source_account:
                raise ValueError("Source account not found or not active")
            
            # Check sufficient funds
            total_amount = transfer_data["amount"] + validation_result["estimated_fees"]
            if source_account.available_balance < total_amount:
                raise ValueError(f"Insufficient funds. Available: {source_account.available_balance}, Required: {total_amount}")
            
            # Create transfer
            transfer_id = f"TRF{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
            
            transfer = Transfer(
                id=str(uuid.uuid4()),
                transfer_id=transfer_id,
                amount=transfer_data["amount"],
                currency=transfer_data["currency"],
                fees=validation_result["estimated_fees"],
                total_amount=total_amount,
                source_account_id=source_account.id,
                destination_account_id=transfer_data.get("destination_account_id"),
                beneficiary_name=transfer_data["beneficiary_name"],
                beneficiary_iban=transfer_data.get("beneficiary_iban"),
                beneficiary_bic=transfer_data.get("beneficiary_bic"),
                beneficiary_bank=transfer_data.get("beneficiary_bank"),
                beneficiary_country=transfer_data.get("beneficiary_country"),
                description=transfer_data.get("description"),
                reference=transfer_data.get("reference"),
                transfer_type=TransferType(transfer_data["transfer_type"]),
                status=TransferStatus.INITIATED,
                priority=TransferPriority(transfer_data.get("priority", "normal")),
                created_at=datetime.now(timezone.utc)
            )
            
            # Block amount from source account
            if not source_account.block_amount(total_amount):
                raise ValueError("Failed to block amount from source account")
            
            # Save transfer
            self.db.add(transfer)
            self.db.commit()
            self.db.refresh(transfer)
            
            # Create initial event
            await self._create_transfer_event(
                transfer.id,
                "initiated",
                TransferStatus.INITIATED,
                "Transfer initiated"
            )
            
            # Record metrics
            record_transfer(
                status=transfer.status.value,
                currency=transfer.currency,
                amount=transfer.amount,
                transfer_type=transfer.transfer_type.value
            )
            
            # Process transfer asynchronously
            asyncio.create_task(self._process_transfer(transfer.id))
            
            logger.info(
                "Transfer created successfully",
                transfer_id=transfer.transfer_id,
                user_id=user.id,
                amount=transfer.amount,
                currency=transfer.currency
            )
            
            return transfer
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create transfer: {e}")
            raise
    
    async def _process_transfer(self, transfer_id: str):
        """Process transfer through appropriate connector"""
        try:
            transfer = self.db.query(Transfer).filter(Transfer.id == transfer_id).first()
            if not transfer:
                logger.error(f"Transfer {transfer_id} not found for processing")
                return
            
            # Update status to processing
            transfer.status = TransferStatus.PROCESSING
            self.db.commit()
            
            await self._create_transfer_event(
                transfer.id,
                "processing",
                TransferStatus.PROCESSING,
                "Transfer processing started"
            )
            
            # Process based on transfer type
            if transfer.transfer_type == TransferType.SWIFT:
                await self._process_swift_transfer(transfer)
            elif transfer.transfer_type == TransferType.MOJALOOP:
                await self._process_mojaloop_transfer(transfer)
            elif transfer.transfer_type == TransferType.IBAN:
                await self._process_iban_transfer(transfer)
            else:
                await self._process_internal_transfer(transfer)
                
        except Exception as e:
            logger.error(f"Failed to process transfer {transfer_id}: {e}")
            await self._fail_transfer(transfer_id, str(e))
    
    async def _process_swift_transfer(self, transfer: Transfer):
        """Process SWIFT transfer"""
        try:
            async with await create_swift_connector() as swift_connector:
                # Create SWIFT message
                swift_message = swift_connector.create_mt103_message(transfer)
                
                # Send message
                result = await swift_connector.send_message(swift_message)
                
                # Update transfer with SWIFT message ID
                transfer.swift_message_id = swift_message.message_id
                transfer.status = TransferStatus.PENDING
                self.db.commit()
                
                await self._create_transfer_event(
                    transfer.id,
                    "swift_sent",
                    TransferStatus.PENDING,
                    f"SWIFT message sent: {swift_message.message_id}"
                )
                
                logger.info(f"SWIFT transfer processed: {transfer.transfer_id}")
                
        except Exception as e:
            logger.error(f"SWIFT transfer processing failed: {e}")
            raise
    
    async def _process_mojaloop_transfer(self, transfer: Transfer):
        """Process Mojaloop transfer"""
        try:
            async with await create_mojaloop_connector() as mojaloop_connector:
                # Create quote
                quote_result = await mojaloop_connector.create_quote(transfer)
                
                # Initiate transfer
                transfer_result = await mojaloop_connector.initiate_transfer(
                    transfer, quote_result["quoteId"]
                )
                
                # Update transfer
                transfer.mojaloop_transfer_id = transfer_result["transferId"]
                transfer.status = TransferStatus.PENDING
                self.db.commit()
                
                await self._create_transfer_event(
                    transfer.id,
                    "mojaloop_initiated",
                    TransferStatus.PENDING,
                    f"Mojaloop transfer initiated: {transfer_result['transferId']}"
                )
                
                logger.info(f"Mojaloop transfer processed: {transfer.transfer_id}")
                
        except Exception as e:
            logger.error(f"Mojaloop transfer processing failed: {e}")
            raise
    
    async def _process_iban_transfer(self, transfer: Transfer):
        """Process IBAN transfer"""
        try:
            # For IBAN transfers, we'll use ISO 20022
            iso20022_connector = create_iso20022_connector()
            
            # Create ISO 20022 message
            iso_message = iso20022_connector.create_pacs008_message(transfer)
            
            # Update transfer
            transfer.iso20022_message_id = iso_message.message_id
            transfer.status = TransferStatus.PENDING
            self.db.commit()
            
            await self._create_transfer_event(
                transfer.id,
                "iso20022_created",
                TransferStatus.PENDING,
                f"ISO 20022 message created: {iso_message.message_id}"
            )
            
            logger.info(f"IBAN transfer processed: {transfer.transfer_id}")
            
        except Exception as e:
            logger.error(f"IBAN transfer processing failed: {e}")
            raise
    
    async def _process_internal_transfer(self, transfer: Transfer):
        """Process internal transfer"""
        try:
            # Get destination account
            destination_account = self.db.query(Account).filter(
                Account.id == transfer.destination_account_id
            ).first()
            
            if not destination_account:
                raise ValueError("Destination account not found")
            
            # Debit source account
            source_account = transfer.source_account
            if not source_account.debit(transfer.total_amount):
                raise ValueError("Failed to debit source account")
            
            # Credit destination account
            destination_account.credit(transfer.amount)
            
            # Update transfer status
            transfer.status = TransferStatus.COMPLETED
            transfer.completed_at = datetime.now(timezone.utc)
            self.db.commit()
            
            # Create account activities
            await self._create_account_activity(
                source_account.id,
                "debit",
                transfer.total_amount,
                transfer.currency,
                f"Transfer to {transfer.beneficiary_name}",
                transfer.transfer_id,
                source_account.balance + transfer.total_amount,
                source_account.balance
            )
            
            await self._create_account_activity(
                destination_account.id,
                "credit",
                transfer.amount,
                transfer.currency,
                f"Transfer from {source_account.holder_name}",
                transfer.transfer_id,
                destination_account.balance - transfer.amount,
                destination_account.balance
            )
            
            await self._create_transfer_event(
                transfer.id,
                "completed",
                TransferStatus.COMPLETED,
                "Internal transfer completed"
            )
            
            logger.info(f"Internal transfer completed: {transfer.transfer_id}")
            
        except Exception as e:
            logger.error(f"Internal transfer processing failed: {e}")
            raise
    
    async def _fail_transfer(self, transfer_id: str, error_message: str):
        """Mark transfer as failed"""
        try:
            transfer = self.db.query(Transfer).filter(Transfer.id == transfer_id).first()
            if not transfer:
                return
            
            # Unblock amount from source account
            source_account = transfer.source_account
            source_account.unblock_amount(transfer.total_amount)
            
            # Update transfer status
            transfer.status = TransferStatus.FAILED
            self.db.commit()
            
            await self._create_transfer_event(
                transfer.id,
                "failed",
                TransferStatus.FAILED,
                f"Transfer failed: {error_message}"
            )
            
            logger.error(f"Transfer failed: {transfer_id} - {error_message}")
            
        except Exception as e:
            logger.error(f"Failed to mark transfer as failed: {e}")
    
    async def _create_transfer_event(self, transfer_id: str, event_type: str, status: TransferStatus, description: str):
        """Create transfer event"""
        try:
            event = TransferEvent(
                id=str(uuid.uuid4()),
                transfer_id=transfer_id,
                event_type=event_type,
                status=status,
                description=description,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(event)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create transfer event: {e}")
    
    async def _create_account_activity(self, account_id: str, activity_type: str, amount: float, currency: str, description: str, reference: str, balance_before: float, balance_after: float):
        """Create account activity"""
        try:
            activity = AccountActivity(
                id=str(uuid.uuid4()),
                account_id=account_id,
                activity_type=activity_type,
                amount=amount,
                currency=currency,
                description=description,
                reference=reference,
                balance_before=balance_before,
                balance_after=balance_after,
                created_at=datetime.now(timezone.utc)
            )
            
            self.db.add(activity)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Failed to create account activity: {e}")
    
    async def get_transfer(self, transfer_id: str, user_id: str) -> Optional[Transfer]:
        """Get transfer by ID for user"""
        return self.db.query(Transfer).join(Account).filter(
            and_(
                Transfer.transfer_id == transfer_id,
                Account.user_id == user_id
            )
        ).first()
    
    async def get_user_transfers(self, user_id: str, page: int = 1, size: int = 20, status: Optional[TransferStatus] = None, transfer_type: Optional[TransferType] = None) -> Tuple[List[Transfer], int]:
        """Get transfers for user with pagination"""
        query = self.db.query(Transfer).join(Account).filter(Account.user_id == user_id)
        
        if status:
            query = query.filter(Transfer.status == status)
        
        if transfer_type:
            query = query.filter(Transfer.transfer_type == transfer_type)
        
        total = query.count()
        transfers = query.order_by(desc(Transfer.created_at)).offset((page - 1) * size).limit(size).all()
        
        return transfers, total
    
    async def cancel_transfer(self, transfer_id: str, user_id: str) -> bool:
        """Cancel transfer"""
        transfer = await self.get_transfer(transfer_id, user_id)
        if not transfer or not transfer.can_cancel:
            return False
        
        try:
            # Unblock amount from source account
            source_account = transfer.source_account
            source_account.unblock_amount(transfer.total_amount)
            
            # Update transfer status
            transfer.status = TransferStatus.CANCELLED
            self.db.commit()
            
            await self._create_transfer_event(
                transfer.id,
                "cancelled",
                TransferStatus.CANCELLED,
                "Transfer cancelled by user"
            )
            
            logger.info(f"Transfer cancelled: {transfer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to cancel transfer: {e}")
            return False
    
    async def validate_transfer(self, transfer_data: dict, user: User) -> Dict[str, Any]:
        """Validate transfer data"""
        errors = []
        warnings = []
        estimated_fees = 0.0
        
        try:
            # Validate required fields
            required_fields = ["source_account_id", "beneficiary_name", "amount", "currency", "transfer_type"]
            for field in required_fields:
                if field not in transfer_data:
                    errors.append(f"Missing required field: {field}")
            
            if errors:
                return {"valid": False, "errors": errors}
            
            # Validate amount
            amount = transfer_data["amount"]
            if amount <= 0:
                errors.append("Amount must be greater than 0")
            
            # Validate currency
            currency = transfer_data["currency"]
            if currency not in ["USD", "EUR", "CDF", "GBP", "CHF"]:
                errors.append("Unsupported currency")
            
            # Validate source account
            source_account = self.db.query(Account).filter(
                and_(
                    Account.id == transfer_data["source_account_id"],
                    Account.user_id == user.id,
                    Account.status == "active"
                )
            ).first()
            
            if not source_account:
                errors.append("Source account not found or not active")
            else:
                # Check available balance
                if source_account.available_balance < amount:
                    errors.append(f"Insufficient funds. Available: {source_account.available_balance}")
                
                # Check daily limit
                if source_account.daily_used + amount > source_account.daily_limit:
                    errors.append(f"Daily limit exceeded. Used: {source_account.daily_used}, Limit: {source_account.daily_limit}")
            
            # Calculate estimated fees
            transfer_type = transfer_data["transfer_type"]
            if transfer_type == "swift":
                estimated_fees = 25.0  # SWIFT fees
            elif transfer_type == "mojaloop":
                estimated_fees = 5.0   # Mojaloop fees
            elif transfer_type == "iban":
                estimated_fees = 15.0  # IBAN fees
            else:
                estimated_fees = 0.0   # Internal transfer
            
            # Add warnings for large amounts
            if amount > 10000:
                warnings.append("Large transfer amount - additional verification may be required")
            
            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings,
                "estimated_fees": estimated_fees
            }
            
        except Exception as e:
            logger.error(f"Transfer validation failed: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"]
            }