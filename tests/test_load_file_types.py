from __future__ import annotations

import types

import pytest

from dynaconf import Dynaconf

pytestmark = pytest.mark.usefixtures("no_deprecations")


def test_load_file_with_module_object_raises_type_error():
    """load_file must raise TypeError when handed a module, not a path.

    Reported in #1299: passing a module object loads nothing and raises
    nothing, so the mistake is silent.
    """
    settings = Dynaconf()
    with pytest.raises(TypeError):
        settings.load_file(types)
