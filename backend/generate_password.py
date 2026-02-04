"""
Generate bcrypt password hashes for default users
"""
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate hashes for default passwords
passwords = {
    "admin": "admin123",
    "user1": "user123",
    "user2": "user123"
}

print("Generated password hashes:")
print("-" * 80)

for username, password in passwords.items():
    hashed = pwd_context.hash(password)
    print(f"-- {username}: {password}")
    print(f"INSERT INTO user_manage (username, password, user_type, status, role_id) VALUES ('{username}', '{hashed}', {1 if username == 'admin' else 0}, 1, {None if username == 'admin' else (2 if username == 'user1' else 3)});")
    print()

print("-" * 80)
print("\nSQL statements generated above!")
