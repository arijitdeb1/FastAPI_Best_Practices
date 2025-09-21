from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Pydantic model for a user as stored in the database
# Includes sensitive information
class UserInDB(BaseModel):
    username: str
    email: str
    hashed_password: str

# Pydantic model for the response payload
# This model *omits* the sensitive password field
class UserResponse(BaseModel):
    username: str
    email: str

# In a real app, you would fetch this from a database
fake_db = {
    "alice": UserInDB(
        username="alice",
        email="alice@example.com",
        hashed_password="hashed_secret"
    )
}

# The route decorator uses the optimized `response_model`
@app.get("/users/{username}", response_model=UserResponse)
def read_user(username: str):
    # Retrieve the raw database object
    db_user = fake_db.get(username)
    if not db_user:
        return {"error": "User not found"}
    
    # Return the raw object.
    # FastAPI automatically filters it using the `UserResponse` schema.
    return db_user
