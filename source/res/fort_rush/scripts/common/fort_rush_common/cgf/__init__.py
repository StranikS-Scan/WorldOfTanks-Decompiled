# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/fort_rush_common/cgf/__init__.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
import CGF
if TYPE_CHECKING:
    from typing import List, Optional, TypeVar
    from CGF import ComponentAccessor
    T = TypeVar('T')

def getTopMostGO(go):
    if not go.valid:
        return None
    else:
        hierarchyManager = CGF.findHierarchySingleton(go.spaceID)
        return None if not hierarchyManager else hierarchyManager.getTopMostParent(go)


def findFirstComponentInHierarchy(root, componentType):
    components = CGF.findInHierarchyWithComponent(root, componentType, True)
    return components[0] if components else None
