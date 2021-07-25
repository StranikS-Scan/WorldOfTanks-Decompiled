# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/perk_ctrl.py
import BigWorld
import Event
import items
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import ViewComponentsController
from skeletons.gui.battle_session import IBattleSessionProvider
from items.components.perks_constants import PERKS_TYPE
_UPDATE_FUN_PREFIX = '_updatePerk'

class PerksController(ViewComponentsController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PerksController, self).__init__()
        self.onPerkChanged = Event.Event()
        self._prevData = {}

    def getControllerID(self):
        return BATTLE_CTRL_ID.PERKS

    def updatePerks(self, perks):
        perksData = self._convertToDict(perks)
        changedPerks = {perkID:value for perkID, value in perksData.iteritems() if perkID not in self._prevData or self._prevData[perkID] != perksData[perkID]}
        for viewCmp in self._viewComponents:
            viewCmp.updatePerks(changedPerks, self._prevData)

        for perkID, data in changedPerks.iteritems():
            updater = getattr(self, _UPDATE_FUN_PREFIX + str(perkID), None)
            if updater is not None:
                updater(perkID=perkID, **data)

        self._prevData = {perkID:data.copy() for perkID, data in perksData.iteritems()}
        return

    def notifyRibbonChanges(self, perksInfo):
        for perkInfo in sorted(perksInfo, key=lambda k: k['endTime']):
            if perkInfo['endTime'] < BigWorld.serverTime():
                continue
            perkID = perkInfo['perkID']
            self.onPerkChanged({'perkID': perkID,
             'stacks': perkInfo['stacks'],
             'isUltimate': items.perks.g_cache.perks().perks.get(perkID).perkType == PERKS_TYPE.ULTIMATE})

    def clearHUD(self):
        for viewCmp in self._viewComponents:
            viewCmp.clearHUD()

    def startControl(self, *args):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self._onVehicleControlling
        return

    def stopControl(self, *args):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self._onVehicleControlling
        self.onPerkChanged.clear()
        return

    def _onVehicleControlling(self, vehicle):
        for perkID, data in self._prevData.iteritems():
            updater = getattr(self, _UPDATE_FUN_PREFIX + str(perkID), None)
            if updater is not None:
                updater(vehicle=vehicle, perkID=perkID, **data)

        return

    def _convertToDict(self, source):
        return {item['perkID']:{'state': item['state'],
         'stacks': item['stacks'],
         'coolDown': item['coolDown'],
         'lifeTime': item['lifeTime']} for item in source}

    def _updatePerk303(self, perkID, state, stacks, coolDown, lifeTime, vehicle=None):
        isActive = bool(state)
        if vehicle is None:
            vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is not None:
            BigWorld.player().updateVehicleQuickShellChanger(vehicle, isActive)
        return
