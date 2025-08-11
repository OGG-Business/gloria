from fastapi import APIRouter, HTTPException
from typing import List
router = APIRouter()
@router.get("/")
def get_auth_info():
    return {"message": "Authentication module", "endpoints": ["/login", "/register", "/refresh"]}
@router.post("/login")
def login():
    return {"message": "Login endpoint", "status": "working"}
@router.post("/register")
def register():
    return {"message": "Register endpoint", "status": "working"}
