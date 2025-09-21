from pydantic import BaseModel, Field

# Using the nested Config class in Pydantic v1
class User(BaseModel):
    # This field uses an alias, common for API compatibility
    first_name: str = Field(..., alias='firstName')
    email: str

    # The nested Config class controls model behavior
    class Config:
        # Ignore any extra fields present in the input data
        extra = 'ignore'
        # Allow instantiation using either 'first_name' or 'firstName'
        allow_population_by_field_name = True

# --- Optimized behavior with extra='ignore' ---
print("Optimized Model (ignoring extra):")
try:
    # 'age' is an extra field, but no error is raised
    data = {"firstName": "Alice", "email": "alice@example.com", "age": 30}
    user_optimized = User(**data)
    print(user_optimized.model_dump_json(indent=2))
except Exception as e:
    print(f"Error caught: {e}")

# --- Populating by field name ---
print("\nPopulating by field name:")
try:
    # Use the Python field name 'first_name' instead of the alias
    user_by_field_name = User(first_name="Bob", email="bob@example.com")
    print(user_by_field_name.model_dump_json(indent=2))
except Exception as e:
    print(f"Error caught: {e}")
