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

    assert typocalypse.transform(input, override_existing=True) == expected


def test_args() -> None:
    input = textwrap.dedent(
        """
            def f(*args):
                pass
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            def f(*args: Any) -> Any:
                pass
        """
    ).strip()

    assert typocalypse.transform(input) == expected


def test_kwargs() -> None:
    input = textwrap.dedent(
        """
            def f(**kwargs):
                pass
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            def f(**kwargs: Any) -> Any:
                pass
        """
    ).strip()

    assert typocalypse.transform(input) == expected


def test_args_kwargs() -> None:
    input = textwrap.dedent(
        """
            def f(*args, **kwargs):
                pass
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            def f(*args: Any, **kwargs: Any) -> Any:
                pass
        """
    ).strip()

    assert typocalypse.transform(input) == expected


def test_param_star() -> None:
    input = textwrap.dedent(
        """
            def f(x, *, y):
                pass
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            def f(x: Any, *, y: Any) -> Any:
                pass
        """
    ).strip()

    assert typocalypse.transform(input) == expected
