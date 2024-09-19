# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_vehicle_portal.py
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_portal_awards_base_model import LootBoxOpeningType
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_vehicle_portal_model import WtEventVehiclePortalModel, EventTankType
from gui.impl.lobby.wt_event.wt_event_sound import playVehicleAwardReceivedFromPortal, playLootBoxPortalExit
from gui.impl.lobby.wt_event.wt_event_base_portal_awards_view import WtEventBasePortalAwards
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import closeEventPortalAwardsWindow
from gui.shared.gui_items.loot_box import EventLootBoxes
from gui.wt_event.wt_event_helpers import getSpecialVehicles
from gui.wt_event.wt_event_models_helper import setLootBoxesCount, fillVehicleModel, fillAdditionalAwards
from gui.wt_event.wt_event_bonuses_packers import LootBoxAwardsManager
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from shared_utils import CONST_CONTAINER

class WtEventVehiclePortal(WtEventBasePortalAwards):

    def __init__(self, awards=None):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WtEventVehiclePortal(), model=WtEventVehiclePortalModel())
        super(WtEventVehiclePortal, self).__init__(settings, awards)

    @property
    def viewModel(self):
        return super(WtEventVehiclePortal, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(WtEventVehiclePortal, self)._onLoaded(*args, **kwargs)
        playVehicleAwardReceivedFromPortal()
        Waiting.hide('updating')

    def _updateModel(self):
        super(WtEventVehiclePortal, self)._updateModel()
        with self.viewModel.transaction() as model:
            self._tooltipItems.clear()
            setLootBoxesCount(model.portalAvailability, self._getBoxType())
            model.setIsFirstLaunch(not self._boxesCtrl.isEngineerReroll())
            extra = self._boxesCtrl.getExtraRewards(self._getBoxType(), count=0)
            model.setFirstLaunchReward(extra.get('gold', 0) if extra else 0)
            specialVehicle = self._boxesCtrl.getSpecialVehicleName(self._awards)
            bonusVehicles = getSpecialVehicles()
            if bonusVehicles and len(bonusVehicles) == 3:
                evenTankType = EventTankType.PRIMARY
                if specialVehicle == bonusVehicles[1]:
                    evenTankType = EventTankType.SECONDARY
                elif specialVehicle == bonusVehicles[2]:
                    evenTankType = EventTankType.TERTIARY
                model.setEventTank(evenTankType)
            fillVehicleModel(model.vehicle, specialVehicle)
            model.setOpeningType(LootBoxOpeningType.KEY_USED)
            if self._awards is not None:
                self.__setModelAwards(model)
        return

    def _getBoxType(self):
        return EventLootBoxes.WT_BOSS

    def _finalize(self):
        g_eventBus.handleEvent(events.WtEventPortalsEvent(events.WtEventPortalsEvent.ON_PORTAL_AWARD_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        super(WtEventVehiclePortal, self)._finalize()

    def __setModelAwards(self, model):
        groupedBonuses = LootBoxAwardsManager.getBossGroupedBonuses(self._awards)
        additonalRewards = groupedBonuses.additional
        mainBonuses = [ bonus for bonus in groupedBonuses.main if bonus.getName() == 'customizations' or self.__isRentTankBonus(bonus) ]
        tankReward = [ bonus for bonus in groupedBonuses.main if bonus not in mainBonuses ]
        additonalRewards[0:0] = mainBonuses
        fillAdditionalAwards(model.rewards, tankReward, self._tooltipItems)
        fillAdditionalAwards(model.additionalRewards, additonalRewards, self._tooltipItems)

    def __isRentTankBonus(self, bonus):
        if bonus.getName() != 'vehicles':
            return False
        else:
            value = bonus.getValue()
            return any([ val.get('rent', None) is not None for entry in value for val in entry.values() ])

    def _onClose(self):
        closeEventPortalAwardsWindow()
        playLootBoxPortalExit()
        super(WtEventVehiclePortal, self)._onClose()


class WtEventVehiclePortalWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, awards, parent=None):
        super(WtEventVehiclePortalWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WtEventVehiclePortal(awards), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)


class ReRollButton(CONST_CONTAINER):
    CLAIM_AND_RELAUNCH = 'claimAndRelaunch'
    REROLL = 'reroll'
