import argparse

from . import typocalypse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--override-existing-annotation", action="store_true")
    parser.add_argument("--annotate-all-variables", action="store_true")
    args = parser.parse_args()

    input_code = """
class A:
    def f(self, x):
        pass
"""
    print("Original Code:")
    print(input_code)
    print("\nTransformed Code:")
    print(typocalypse.transform(input_code))


if __name__ == "__main__":
    main()


# Add Any to anything that's not a function call OR literal.
