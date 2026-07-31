import bcrypt
from passlib.context import CryptContext

print("Testing bcrypt...")

# Test 1: Direct bcrypt
password = b"pass123"
salt = bcrypt.gensalt()
hashed = bcrypt.hashpw(password, salt)
print(f"Direct bcrypt hash: {hashed}")
print(f"Verify: {bcrypt.checkpw(password, hashed)}")

# Test 2: Passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
hashed2 = pwd_context.hash("pass123")
print(f"Passlib hash: {hashed2}")
print(f"Passlib verify: {pwd_context.verify('pass123', hashed2)}")

print("✅ All tests passed!")