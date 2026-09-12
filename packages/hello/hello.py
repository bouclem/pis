"""hello — a tiny sample pis package.

After `pis install hello`, this becomes importable:
    >>> import hello
    >>> hello.greet()
    'hello from pis!'
"""


def greet(name: str = "pis") -> str:
    """Return a friendly greeting."""
    return f"hello from {name}!"


def main() -> int:
    print(greet())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
