from typing import Protocol, Dict

class PaymentConnector(Protocol):
    async def send_credit_transfer(self, transfer: Dict, dry_run: bool = True) -> Dict:
        ...