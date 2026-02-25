# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/fall_tanks_pbs_helper.py
from __future__ import absolute_import
import typing
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from fall_tanks.gui.battle_results.reusable.fall_tanks_shared import FallTanksVehicleSummarizeInfo

def isFinished(reusable, results):
    vehicleSumInfo = reusable.getPersonalVehiclesInfo(results[_RECORD.PERSONAL])
    return vehicleSumInfo.finishTime > 0


def getFinishPlace(vehicleInfo, _=None):
    return vehicleInfo.finishPosition if vehicleInfo.finishTime > 0 else 0


def getFinishTime(vehicleInfo, _=None):
    return max(vehicleInfo.finishTime, 0.0)


def getRespawnCount(vehicleInfo, _):
    return vehicleInfo.respawns
