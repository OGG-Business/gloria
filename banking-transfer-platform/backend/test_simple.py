#!/usr/bin/env python3
print("Testing Banking Transfer Platform...")
from fastapi import FastAPI
print("✅ FastAPI imported")
import structlog
print("✅ structlog imported")
from app.main import app
print("✅ App imported")
print(f"App title: {app.title}")
