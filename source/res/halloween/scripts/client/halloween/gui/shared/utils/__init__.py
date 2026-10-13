# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/shared/utils/__init__.py
from __future__ import absolute_import
import BigWorld
import wg_async as future_async
from adisp import adisp_async
from halloween.gui.shared.event_dispatcher import showAbilitiesIncompleteConfirm

def findMarkerEntity():
    return [ e for e in BigWorld.entities.valuesOfType('EmptyEntity') if any((c.__class__.__name__ == 'EntityMarkerComponent' for c in e.dynamicComponents.values())) ]


@adisp_async
@future_async.wg_async
def checkAbilities(vehicle, callback):
    if vehicle:
        if any((not item for item in vehicle.consumables.installed)):
            result = yield future_async.wg_await(showAbilitiesIncompleteConfirm())
            if result.busy or not result.result:
                callback(False)
                return
            toBattle, _ = result.result
            callback(toBattle)
        else:
            callback(True)
