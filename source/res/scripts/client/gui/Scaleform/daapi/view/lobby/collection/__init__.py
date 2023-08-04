# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/collection/__init__.py
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.collection.collection_entry_point import CollectionEntryPoint
    return (ComponentSettings(HANGAR_ALIASES.COLLECTION_ENTRY_POINT, CollectionEntryPoint, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
