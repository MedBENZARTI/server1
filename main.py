from fastapi import FastAPI, Depends, HTTPException

app = FastAPI()

# Sample API keys (replace with your actual API keys)
api_keys = {"api_key_1": "user_1", "api_key_2": "user_2"}

# Custom authentication dependency
def authenticate_api_key(api_key: str = Depends(lambda x: x)):
    if api_key not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return api_keys[api_key]

@app.get("/")
def read_root():
    """
    This is a hello world apihow to refresh uvicorn 
      test
    """
    return {"message": "Hello, FastAPI!"}

@app.get("/protected")
def protected_route(user: str = Depends(authenticate_api_key)):
    return {"message": f"Hello, {user}! This is a protected route."}