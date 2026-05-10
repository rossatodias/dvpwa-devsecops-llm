"""
Regression test: Cross-Site Request Forgery (CSRF) — VULN-05

Validates that the CSRF middleware is enabled in the application,
ensuring POST requests without valid CSRF tokens are rejected.

Before the fix:
    csrf_middleware was commented out in app.py

After the fix:
    csrf_middleware is active — POST without token → 403
"""

from conftest import read_source


APP_SOURCE = read_source("sqli/app.py")
MIDDLEWARE_SOURCE = read_source("sqli/middlewares.py")
JINJA_UTILS_SOURCE = read_source("sqli/utils/jinja2.py")


def test_csrf_middleware_is_enabled():
    """Verify that csrf_middleware is in the middlewares list, not commented."""
    assert "csrf_middleware," in APP_SOURCE, (
        "csrf_middleware is not in the middlewares list"
    )
    assert "# csrf_middleware" not in APP_SOURCE, (
        "csrf_middleware is still commented out in app.py"
    )


def test_csrf_middleware_is_imported():
    """Verify that csrf_middleware is properly imported."""
    assert "csrf_middleware" in APP_SOURCE, (
        "csrf_middleware is not referenced in app.py"
    )
    assert "from sqli.middlewares import" in APP_SOURCE, (
        "Missing import from sqli.middlewares"
    )


def test_csrf_middleware_validates_token():
    """
    Verify that the csrf_middleware function checks for _csrf_token
    in POST requests and raises HTTPForbidden on mismatch.
    """
    assert "_csrf_token" in MIDDLEWARE_SOURCE, (
        "csrf_middleware does not check for _csrf_token"
    )
    assert "HTTPForbidden" in MIDDLEWARE_SOURCE, (
        "csrf_middleware does not raise HTTPForbidden for invalid tokens"
    )
    assert 'request.method == "POST"' in MIDDLEWARE_SOURCE, (
        "csrf_middleware does not check for POST method"
    )


def test_csrf_token_generation_exists():
    """
    Verify that the CSRF token generation function exists
    and creates tokens for sessions.
    """
    assert "_csrf_token" in JINJA_UTILS_SOURCE, (
        "csrf_processor does not handle _csrf_token"
    )
    assert "uuid4" in JINJA_UTILS_SOURCE, (
        "csrf_processor does not use uuid4 for token generation"
    )
