import textwrap

import typocalypse


def test_basic() -> None:
    input = ""
    expected = "from typing import Any"
    assert typocalypse.transform(input) == expected


def test_no_double_import() -> None:
    input = "from typing import Any"
    expected = "from typing import Any"
    assert typocalypse.transform(input) == expected


def test_import_if_nested() -> None:
    input = textwrap.dedent(
        """
            def f(x):
                from typing import Any
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            def f(x: Any) -> Any:
                from typing import Any
        """
    ).strip()

    assert typocalypse.transform(input) == expected


def test_add_to_typing_import() -> None:
    input = "from typing import List"
    expected = "from typing import Any, List"
    assert typocalypse.transform(input) == expected


def test_double_typing_import() -> None:
    input = textwrap.dedent(
        """
            from typing import Any
            from typing import List
        """
    ).strip()

    expected = textwrap.dedent(
        """
            from typing import Any
            from typing import List
        """
    ).strip()

    assert typocalypse.transform(input) == expected


def test_import_star() -> None:
    input = "from typing import *"

    expected = textwrap.dedent(
        """
            from typing import Any
            from typing import *
        """
    ).strip()

    assert typocalypse.transform(input) == expected
