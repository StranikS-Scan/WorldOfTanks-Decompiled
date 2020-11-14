# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/vehicle_extras_battle_royale.py
from helpers.EntityExtra import EntityExtra

class AfterburningBattleRoyale(EntityExtra):

    def _start(self, extraData, activate=None):
        vehicle = extraData['entity']
        appearance = vehicle.appearance
        if appearance is not None:
            effectMgr = appearance.customEffectManager
            if effectMgr is not None:
                effectMgr.variables['Nitro'] = 1
        return

    def _cleanup(self, extraData):
        vehicle = extraData['entity']
        appearance = vehicle.appearance
        if appearance is not None:
            effectMgr = appearance.customEffectManager
            if effectMgr is not None:
                effectMgr.variables['Nitro'] = 0
        return
