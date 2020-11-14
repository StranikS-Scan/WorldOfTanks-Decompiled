# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/InBattleUpgradesAvatar.py
import BigWorld
from debug_utils import LOG_DEBUG, LOG_WARNING
import BattleReplay
from items import vehicles, ITEM_TYPES

class InBattleUpgradesAvatar(BigWorld.DynamicScriptComponent):

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self, *args):
        pass

    def vehicleUpgradeResponse(self, intCDs, reasons):
        player = self.entity

        def __vehicleUpgradeLogger(isSuccess, intCD, reason, moduleTxt):
            if isSuccess:
                LOG_DEBUG('{} intCD = {} successfully installed'.format(moduleTxt, intCD))
            else:
                LOG_WARNING('Could not install {} intCD = {}. Reason - {}!'.format(moduleTxt, intCD, reason))

        for intCD, reason in zip(intCDs, reasons):
            __vehicleUpgradeLogger(reason == '', intCD, reason, 'Main' if intCD is intCDs[0] else 'Additional')

        mainIntCDs = intCDs[0]
        mainSuccess = not reasons[0]
        if mainSuccess and ITEM_TYPES.vehicleGun in [ vehicles.parseIntCompactDescr(intCD)[0] for intCD in intCDs ]:
            self.__upgradeVehicleGun()
        if player.guiSessionProvider.dynamic.progression:
            if BattleReplay.g_replayCtrl.isPlaying:
                player.guiSessionProvider.dynamic.progression.vehicleUpgradeRequest(mainIntCDs)
            player.guiSessionProvider.dynamic.progression.vehicleUpgradeResponse(mainIntCDs, mainSuccess)

    def __upgradeVehicleGun(self):
        player = self.entity
        if player.guiSessionProvider.shared.ammo:
            player.guiSessionProvider.shared.ammo.clear(leave=False)
