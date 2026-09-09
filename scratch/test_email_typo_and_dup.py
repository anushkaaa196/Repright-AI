import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.auth_service import AuthService, check_email_format
from database.user_repository import UserRepository

# 1. Test check_email_format
test_emails = [
    ("rohit@gmai.com", False, "Invalid email domain '@gmai.com'. Did you mean '@gmail.com'?"),
    ("user@gamil.com", False, "Invalid email domain '@gamil.com'. Did you mean '@gmail.com'?"),
    ("user@yaho.com", False, "Invalid email domain '@yaho.com'. Did you mean '@yahoo.com'?"),
    ("user@hotmial.com", False, "Invalid email domain '@hotmial.com'. Did you mean '@hotmail.com'?"),
    ("user@outlok.com", False, "Invalid email domain '@outlok.com'. Did you mean '@outlook.com'?"),
    ("user@gmail.com", True, ""),
    ("valid.athlete+test@company.co.uk", True, ""),
    ("notanemail", False, "Please enter a valid email address (e.g. athlete@example.com)."),
]

print("--- 1. Testing Email Format & Typo Detection ---")
for email, expected_valid, expected_hint in test_emails:
    valid, msg = check_email_format(email)
    assert valid == expected_valid, f"Failed for {email}: expected {expected_valid}, got {valid}"
    if not valid:
        assert msg == expected_hint, f"Failed hint for {email}: expected '{expected_hint}', got '{msg}'"
    print(f"  [OK] '{email}' -> valid={valid}, msg='{msg}'")

# 2. Test AuthService registration with typo domain
auth = AuthService()
success, msg, user = auth.register("Test Typo", "someone@gmai.com", "password123")
print("\n--- 2. Testing AuthService with Typo Domain ---")
assert not success, "Registration should fail on @gmai.com"
assert "@gmail.com" in msg, f"Expected suggestion in '{msg}'"
print(f"  [OK] Registration blocked with message: '{msg}'")

# 3. Test duplicate email with rohit@gmail.com
print("\n--- 3. Testing Duplicate Registration with Existing Email ---")
success, msg, user = auth.register("Test Dup", "rohit@gmail.com", "password123")
assert not success, "Registration should fail on duplicate email"
assert "already exists" in msg, f"Expected duplicate message in '{msg}'"
print(f"  [OK] Duplicate registration blocked: '{msg}'")

# 4. Test UserRepository.create_user directly with existing email
print("\n--- 4. Testing UserRepository direct duplicate guard ---")
repo = UserRepository()
try:
    repo.create_user("Direct Dup", "rohit@gmail.com", "dummyhash")
    assert False, "Should have raised ValueError"
except ValueError as e:
    assert "already exists" in str(e)
    print(f"  [OK] UserRepository raised ValueError: '{e}'")

print("\n[ALL TESTS PASSED SUCCESSFULLY!]")

