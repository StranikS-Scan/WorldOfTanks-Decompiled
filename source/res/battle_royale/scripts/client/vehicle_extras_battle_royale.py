# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/vehicle_extras_battle_royale.py
from __future__ import absolute_import
from helpers.EntityExtra import EntityExtra

class AfterburningBattleRoyale(EntityExtra):

    def _start(self, data, args):
        vehicle = data['entity']
        appearance = vehicle.appearance
        if appearance is not None:
            effectMgr = appearance.customEffectManager
            if effectMgr:
                effectMgr.variables['Nitro'] = 1
        return

    def _cleanup(self, data):
        vehicle = data['entity']
        appearance = vehicle.appearance
        if appearance is not None:
            effectMgr = appearance.customEffectManager
            if effectMgr:
                effectMgr.variables['Nitro'] = 0
        return
