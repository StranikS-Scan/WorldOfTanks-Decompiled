# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/__init__.py
"""
This package contains components that are used in vehicle's items, optional devices, equipment,
tankman and so on.

The following rules are applied to this package:

1. A component shall not contain any other component.
2. Namedtuple is created if the component is simple and does not include logic.
3. Class + slots is created if the component includes a logic or has variability set of data.
"""
from items.components import chassis_components
from items.components import component_constants
from items.components import gun_components
from items.components import legacy_stuff
from items.components import shared_components
from items.components import shell_components
from items.components import skills_components
from items.components import skills_constants
from items.components import sound_components
from items.components import tankmen_components
__all__ = ('chassis_components', 'component_constants', 'gun_components', 'legacy_stuff', 'shared_components', 'shell_components', 'skills_components', 'skills_constants', 'sound_components', 'tankmen_components')
