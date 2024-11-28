import textwrap

import typocalypse


def test_basic_function() -> None:
    input = textwrap.dedent(
        """
            def f(x):
                pass
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            def f(x: Any) -> Any:
                pass
        """
    ).strip()

    assert typocalypse.transform(input) == expected


def test_class_function_self() -> None:
    input = textwrap.dedent(
        """
            class A:
                def f(self, x):
                    pass
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            class A:
                def f(self, x: Any) -> Any:
                    pass
        """
    ).strip()

    assert typocalypse.transform(input) == expected


def test_class_function_cls() -> None:
    input = textwrap.dedent(
        """
            class A:
                def f(cls, x):
                    pass
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            class A:
                def f(cls, x: Any) -> Any:
                    pass
        """
    ).strip()

    assert typocalypse.transform(input) == expected


def test_class_function_custom() -> None:
    input = textwrap.dedent(
        """
            class A:
                def f(custom, x):
                    pass
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            class A:
                def f(custom, x: Any) -> Any:
                    pass
        """
    ).strip()

    assert typocalypse.transform(input, self_argument_name_re="custom") == expected


def test_function_override_annotation() -> None:
    input = textwrap.dedent(
        """
            def f(x: int) -> None:
                pass
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            def f(x: Any) -> Any:
                pass
        """
    ).strip()

    assert typocalypse.transform(input, override_existing_annotations=True) == expected
