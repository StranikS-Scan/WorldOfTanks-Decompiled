# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/perks_panel.py
from gui.Scaleform.daapi.view.meta.PerksPanelMeta import PerksPanelMeta
import WWISE
import items
import BigWorld
from shared_utils import CONST_CONTAINER
from helpers import dependency
from items.components.perks_constants import PERKS_TYPE, PERK_STATE
from skeletons.gui.battle_session import IBattleSessionProvider

class PerksSounds(CONST_CONTAINER):
    TALENT = 'detachment_talent'
    PERK = 'detachment_perk'
    STACK_TALENT = 'detachment_stack_talent'
    STACK_PERK = 'detachment_stack_perk'
    MICRO_STATE = 'detachment_micro_state'


def _isUltimate(perkID):
    return items.perks.g_cache.perks().perks.get(perkID).perkType == PERKS_TYPE.ULTIMATE


class PerksPanel(PerksPanelMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def updatePerks(self, changedPerks, prevPerks):
        for perkID, perkData in changedPerks.iteritems():
            lifeTime = self._getLifeTime(perkData)
            isUltimate = _isUltimate(perkID)
            state = perkData['state']
            self.as_updatePerkS(perkID, state, perkData['stacks'], isUltimate, perkData['coolDown'], lifeTime)
            if state == PERK_STATE.ACTIVE:
                if perkID not in prevPerks or prevPerks[perkID]['state'] < state:
                    WWISE.WW_eventGlobal(PerksSounds.TALENT if isUltimate else PerksSounds.PERK)
                elif prevPerks[perkID]['stacks'] != perkData['stacks']:
                    WWISE.WW_eventGlobal(PerksSounds.STACK_TALENT if isUltimate else PerksSounds.STACK_PERK)

    def clearHUD(self):
        self.as_clearPanelS()

    def onMinimizedChanged(self, isMinimized):
        WWISE.WW_eventGlobal(PerksSounds.MICRO_STATE)

    def _populate(self):
        super(PerksPanel, self)._populate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self._onVehicleControlling
        return

    def _setPerks(self, vehicle):
        self.clearHUD()
        perksData = []
        for perkData in sorted(vehicle.perks, key=lambda k: k['perkID']):
            perkID = perkData['perkID']
            perk = {'perkID': perkID,
             'state': perkData['state'],
             'stack': perkData['stacks'],
             'isUltimate': _isUltimate(perkID),
             'duration': perkData['coolDown'],
             'lifeTime': self._getLifeTime(perkData)}
            perksData.append(perk)

        self.as_initS(perksData)

    def _dispose(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self._onVehicleControlling
        super(PerksPanel, self)._dispose()
        return

    def _onVehicleControlling(self, vehicle):
        self._setPerks(vehicle)

    def _getLifeTime(self, perkData):
        lifeTimeServer = perkData['lifeTime']
        return lifeTimeServer - BigWorld.serverTime() if BigWorld.serverTime() < lifeTimeServer else -1
