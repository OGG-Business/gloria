from fastapi import FastAPI
app = FastAPI(title="Banking Transfer Platform", version="1.0.0")
@app.get("/")
def root():
    return {"message": "Banking Transfer Platform API"}
print("✅ Main app created")
