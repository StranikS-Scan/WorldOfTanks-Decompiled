# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/shared.py
EXT_PREVIEW_ITEMS = dict()

def tryGetExternalAvailablePreviewAlias():
    for alias, conditionFunc in EXT_PREVIEW_ITEMS.items():
        if conditionFunc():
            return alias

    return None
