# Docstring Style Standard

This SDK uses a uniform docstring style for public classes and methods.

## Goals

- Fast scanning for beginners.
- Predictable structure for advanced users.
- Consistent IDE help and generated documentation output.

## Method Template

```python
def example(arg1: str, arg2: int | None = None) -> bool:
    """One-line summary.

    Optional short context paragraph.

    Args:
        arg1: Required value description.
        arg2: Optional value description.

    Returns:
        Description of return value.

    Raises:
        ValueError: If input validation fails.
        MTNCloudError: If the API request fails.
    """
```

## Class Template

```python
class Example:
    """One-line summary.

    Explain what the class represents and when it should be used.
    """
```

## Rules

1. Start with an imperative one-line summary.
2. Use `Args`, `Returns`, and `Raises` on public methods.
3. Include examples only when they add clarity.
4. Avoid Markdown code fences inside docstrings; prefer plain text blocks.
5. Keep docstrings accurate to the current method signature.
6. Prefer exact resource names used by the SDK (`group`, `cloud`, `archive bucket`).

