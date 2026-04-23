# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/shared/utils/__init__.py
from __future__ import absolute_import
from future.utils import viewvalues
import BigWorld
from LSAccountEquipmentController import getLSConsumables
import wg_async as future_async
from adisp import adisp_async
from last_stand.gui.shared.event_dispatcher import showAbilitiesIncompleteConfirm

def findMarkerEntity():
    return [ e for e in BigWorld.entities.valuesOfType('EmptyEntity') if any((c.__class__.__name__ == 'EntityMarkerComponent' for c in viewvalues(e.dynamicComponents))) ]


@adisp_async
@future_async.wg_async
def checkAbilities(vehicle, callback):
    if vehicle:
        if any((not item for item in getLSConsumables(vehicle).installed)):
            result = yield future_async.wg_await(showAbilitiesIncompleteConfirm())
            if result.busy or not result.result:
                callback(False)
                return
            toBattle, _ = result.result
            callback(toBattle)
        else:
            callback(True)
