"""
Regression test: Stored XSS — VULN-02

Validates that Jinja2 autoescape is enabled, preventing
stored XSS attacks via unescaped HTML in template output.

Before the fix:
    autoescape=False → <script>alert('XSS')</script> was rendered as HTML

After the fix:
    autoescape=True → <script> is escaped to &lt;script&gt;
"""

from jinja2 import Environment

from conftest import read_source


APP_SOURCE = read_source("sqli/app.py")


def test_jinja2_autoescape_is_enabled():
    """Verify that setup_jinja is called with autoescape=True."""
    assert "autoescape=True" in APP_SOURCE, (
        "Jinja2 autoescape is not set to True in sqli/app.py — "
        "Stored XSS is still possible"
    )
    assert "autoescape=False" not in APP_SOURCE, (
        "Jinja2 autoescape=False is still present in sqli/app.py"
    )


def test_xss_payload_would_be_escaped():
    """
    Demonstrate that with autoescape=True, Jinja2 escapes HTML entities.
    """
    env = Environment(autoescape=True)
    template = env.from_string("{{ content }}")

    xss_payload = "<script>alert('XSS')</script>"
    rendered = template.render(content=xss_payload)

    assert "<script>" not in rendered, (
        "XSS payload was NOT escaped — <script> tag appears in output"
    )
    assert "&lt;script&gt;" in rendered, (
        "XSS payload should be escaped to &lt;script&gt;"
    )


def test_html_injection_in_review():
    """
    Simulate what happens when a user submits HTML as a review.
    With autoescape=True, the HTML should be escaped.
    """
    env = Environment(autoescape=True)
    template = env.from_string(
        "<div class='review'>{{ review_text }}</div>"
    )

    payloads = [
        "<script>alert(document.cookie)</script>",
        "<img src=x onerror=alert(1)>",
        "<b onmouseover=alert(1)>hover me</b>",
    ]

    for payload in payloads:
        rendered = template.render(review_text=payload)
        assert "<script>" not in rendered
        assert "onerror=" not in rendered or "&" in rendered
        assert "onmouseover=" not in rendered or "&" in rendered
