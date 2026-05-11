"""
Regression test: Weak Password Storage — VULN-04

Validates that passwords are verified using bcrypt instead of MD5.

Before the fix:
    check_password() used hashlib.md5() — weak, no salt

After the fix:
    check_password() uses bcrypt.checkpw() — proper KDF with salt
"""

import bcrypt

from conftest import read_source


USER_SOURCE = read_source("sqli/dao/user.py")
FIXTURES_SOURCE = read_source("migrations/001-fixtures.sql")


def test_user_does_not_import_md5():
    """Verify that hashlib.md5 is no longer used in user.py."""
    assert "from hashlib import md5" not in USER_SOURCE, (
        "user.py still imports md5 from hashlib"
    )
    assert "hashlib.md5" not in USER_SOURCE, (
        "user.py still uses hashlib.md5"
    )


def test_user_imports_bcrypt():
    """Verify that user.py now uses bcrypt."""
    assert "import bcrypt" in USER_SOURCE, (
        "user.py does not import bcrypt"
    )


def test_check_password_uses_bcrypt():
    """Verify check_password uses bcrypt.checkpw."""
    assert "bcrypt.checkpw" in USER_SOURCE, (
        "check_password does not use bcrypt.checkpw"
    )
    # Find the check_password method
    cp_start = USER_SOURCE.find("def check_password")
    cp_source = USER_SOURCE[cp_start:cp_start + 200]
    assert "md5" not in cp_source, (
        "check_password still references md5"
    )


def test_fixtures_use_bcrypt_hashes():
    """Verify that fixtures use bcrypt hashes, not md5()."""
    assert "md5(" not in FIXTURES_SOURCE, (
        "Fixtures still use md5() function for password hashing"
    )
    assert "$2b$" in FIXTURES_SOURCE, (
        "Fixtures do not contain bcrypt hashes ($2b$ prefix)"
    )


def test_bcrypt_verification_works():
    """
    Functional test: verify that bcrypt check works correctly
    with the pre-computed hashes used in fixtures.
    """
    stored_hash = "$2b$04$PgHLA6dMFRqDrMSBQ8tUbeb8k7Wc8tLX2gMvqOJpyK4/WoQtfwDYW"

    assert bcrypt.checkpw(
        "superadmin".encode('utf-8'),
        stored_hash.encode('utf-8'),
    ), "bcrypt should verify 'superadmin' against its hash"

    assert not bcrypt.checkpw(
        "wrongpassword".encode('utf-8'),
        stored_hash.encode('utf-8'),
    ), "bcrypt should reject wrong password"


def test_bcrypt_all_fixture_passwords():
    """Verify all fixture passwords match their bcrypt hashes."""
    fixture_passwords = {
        "$2b$04$PgHLA6dMFRqDrMSBQ8tUbeb8k7Wc8tLX2gMvqOJpyK4/WoQtfwDYW": "superadmin",
        "$2b$04$Z5iNPI8DLWW8nrFbN2AQJOyx2BgWZnW0lVuUqW2RUqso7AbG85vNK": "password",
        "$2b$04$Itdgsk/W5DHiYrt0pjsFG.oVuxNoNB9CHdx1N.CXmk2v/Vg69m4/2": "spidey",
    }

    for stored_hash, password in fixture_passwords.items():
        assert bcrypt.checkpw(
            password.encode('utf-8'),
            stored_hash.encode('utf-8'),
        ), f"bcrypt verification failed for password '{password}'"
