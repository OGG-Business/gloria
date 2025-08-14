from fastapi import APIRouter
router = APIRouter()
@router.get("/")
def get_notifications():
    return {"message": "Notifications module", "endpoints": ["/send", "/list", "/settings"]}
@router.post("/send")
def send_notification():
    return {"message": "Notification sent", "status": "delivered"}
