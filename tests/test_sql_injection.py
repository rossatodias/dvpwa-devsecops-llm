"""
Regression test: SQL Injection — VULN-01

Validates that the Student.create() method uses parameterized queries
and does NOT allow SQL injection via the student name field.

Before the fix:
    Payload: Robert'); DROP TABLE students CASCADE; --
    Result:  TABLE students was dropped (SQL injection successful)

After the fix:
    Payload is stored as literal text, no SQL execution.
"""

from conftest import read_source


STUDENT_SOURCE = read_source("sqli/dao/student.py")


def test_student_create_uses_parameterized_query():
    """Ensure Student.create() uses %s placeholder, not string formatting."""
    # Must NOT contain Python string formatting for the query
    assert "% {'name': name}" not in STUDENT_SOURCE, (
        "Student.create() still uses Python string formatting — "
        "SQL Injection is still possible"
    )
    assert "%(name)s')" not in STUDENT_SOURCE or "VALUES (%s)" in STUDENT_SOURCE, (
        "Student.create() still interpolates 'name' directly into SQL"
    )


def test_student_create_passes_params_to_execute():
    """Ensure cur.execute() is called with a separate params tuple."""
    # The execute call must have a second argument (params)
    assert "execute(q, (name,))" in STUDENT_SOURCE, (
        "Student.create() must pass parameters as second arg to execute()"
    )


def test_sqli_payload_would_be_safe():
    """
    Verify that the query template uses parameterized VALUES (%s),
    which means any SQL injection payload would be treated as a literal string.
    """
    assert "VALUES (%s)" in STUDENT_SOURCE, (
        "Expected parameterized VALUES (%s) in Student.create()"
    )
    # The old vulnerable pattern should NOT exist
    assert "VALUES ('%(name)s')" not in STUDENT_SOURCE, (
        "The vulnerable pattern VALUES ('%(name)s') still exists"
    )
