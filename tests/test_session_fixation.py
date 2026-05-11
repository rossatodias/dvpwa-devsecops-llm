"""
Regression test: Session Fixation — VULN-03

Validates that the session identity is regenerated on login,
preventing session fixation attacks.

Before the fix:
    Session ID stayed the same after login

After the fix:
    Session is cleared and _identity is reset on login/logout
"""

from conftest import read_source


VIEWS_SOURCE = read_source("sqli/views.py")
MIDDLEWARE_SOURCE = read_source("sqli/middlewares.py")


def test_session_regeneration_on_login():
    """
    Verify that the login handler clears the session and
    forces a new identity (prevents session fixation).
    """
    assert "session.clear()" in VIEWS_SOURCE, (
        "Login handler does not call session.clear() — "
        "old session data may persist (session fixation risk)"
    )

    assert "session._identity = None" in VIEWS_SOURCE, (
        "Login handler does not reset session._identity — "
        "session cookie remains the same (session fixation risk)"
    )

    assert "session._new = True" in VIEWS_SOURCE, (
        "Login handler does not set session._new = True — "
        "session middleware may not generate a new cookie"
    )


def test_session_cleared_before_user_id_set():
    """
    Verify that session.clear() comes BEFORE session['user_id'] = user.id.
    This ensures the old session data is wiped before the new identity is set.
    """
    clear_pos = VIEWS_SOURCE.find("session.clear()")
    user_id_pos = VIEWS_SOURCE.find("session['user_id'] = user.id")

    assert clear_pos < user_id_pos, (
        "session.clear() must come before setting user_id"
    )


def test_session_regeneration_on_logout():
    """
    Verify that logout clears the session and forces new identity.
    """
    # Find the logout function in the source
    logout_start = VIEWS_SOURCE.find("async def logout")
    assert logout_start != -1, "logout function not found in views.py"

    logout_source = VIEWS_SOURCE[logout_start:]

    assert "session.clear()" in logout_source, (
        "Logout handler does not call session.clear()"
    )
    assert "session._identity = None" in logout_source, (
        "Logout handler does not reset session._identity"
    )


def test_httponly_cookie_flag():
    """
    Verify that session cookies have httponly=True set.
    """
    assert "httponly=True" in MIDDLEWARE_SOURCE, (
        "Session storage does not set httponly=True — "
        "cookies are accessible via JavaScript"
    )
    assert "httponly=False" not in MIDDLEWARE_SOURCE, (
        "Session storage still has httponly=False"
    )
