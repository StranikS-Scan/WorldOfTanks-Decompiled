# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/status_notifications/epic_helpers.py
from items import vehicles

def getEquipmentById(equipmentId):
    return vehicles.g_cache.equipments()[equipmentId]


def getSmokeDataByPredicate(smokeInfo, teamPredicate, postEffectPredicate):
    if smokeInfo is None or not teamPredicate or not postEffectPredicate:
        return (None, None)
    else:
        return (smokeInfo['endTime'], getEquipmentById(smokeInfo['equipmentID'])) if teamPredicate(smokeInfo['team']) and postEffectPredicate(smokeInfo['expiring']) else (None, None)
