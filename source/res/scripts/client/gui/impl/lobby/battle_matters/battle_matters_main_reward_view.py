# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_matters/battle_matters_main_reward_view.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_main_reward_view_model import BattleMattersMainRewardViewModel
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showBattleMatters, showBattleMattersMainReward
from gui.server_events.bonuses import VehiclesBonus
from gui.shared.event_dispatcher import showVehiclePreviewWithoutBottomPanel, showHangar, selectVehicleInHangar
from gui.impl.lobby.battle_matters.battle_matters_bonus_packer import BattleMattersVehiclesBonusUIPacker
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.server_events import IEventsCache
from web.web_client_api.common import ItemPackEntry, ItemPackType
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from typing import Tuple, Sequence, Callable, Optional
    from Event import Event
_BATTLEMATTERS_VEHICLES_ORDER = ('Pl19_CS_52_LIS', 'R165_Object_703_II', 'A122_TS-5')

def _vehiclesSortOrder(firstModel, secondModel):
    firstIdx = secondIdx = len(_BATTLEMATTERS_VEHICLES_ORDER)
    firstName = firstModel.getVehName()
    secondName = secondModel.getVehName()
    if firstName in _BATTLEMATTERS_VEHICLES_ORDER:
        firstIdx = _BATTLEMATTERS_VEHICLES_ORDER.index(firstName)
    if secondName in _BATTLEMATTERS_VEHICLES_ORDER:
        secondIdx = _BATTLEMATTERS_VEHICLES_ORDER.index(secondName)
    return cmp(firstIdx, secondIdx)


class BattleMattersMainRewardView(ViewImpl):
    __slots__ = ()
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_matters.BattleMattersMainRewardView())
        settings.flags = ViewFlags.VIEW
        settings.model = BattleMattersMainRewardViewModel()
        super(BattleMattersMainRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleMattersMainRewardView, self).getViewModel()

    def onStateChanged(self):
        if not self.__battleMattersController.isEnabled():
            showHangar()

    def onPreview(self, vehCDDict):
        vehCD = int(vehCDDict.get('vehCD', 0))
        if findFirst(lambda v: v.getVehCD() == vehCD, self.viewModel.getVehicles()).getIsInHangar():
            selectVehicleInHangar(vehCD)
        else:

            def subscriptionFunc():
                controller = dependency.instance(IBattleMattersController)
                if not controller.isEnabled() or controller.isPaused():
                    showHangar()

            showVehiclePreviewWithoutBottomPanel(vehCD, backCallback=showBattleMattersMainReward, itemsPack=[ItemPackEntry(type=ItemPackType.CREW_100, count=1, groupID=1)], backBtnLabel=VEHICLE_PREVIEW.HEADER_BACKBTN_DESCRLABEL_BATTLEMATTERSMAINREWARD, subscriptions=[[self.__battleMattersController.onStateChanged, subscriptionFunc]])

    @staticmethod
    def onBack():
        showBattleMatters()

    @staticmethod
    def onClose():
        showHangar()

    def _initialize(self, *args, **kwargs):
        super(BattleMattersMainRewardView, self)._initialize(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        return ((self.viewModel.onPreview, self.onPreview),
         (self.viewModel.onBack, self.onBack),
         (self.viewModel.onClose, self.onClose),
         (self.__battleMattersController.onStateChanged, self.onStateChanged),
         (self.__eventsCache.onSyncCompleted, self.__update))

    def __update(self):
        finalQuest = self.__battleMattersController.getFinalQuest()
        bonuses = finalQuest.getBonuses()
        vehiclesBonus = None
        for bonus in bonuses:
            if bonus.getName() == VehiclesBonus.VEHICLES_BONUS:
                vehiclesBonus = bonus
                break

        if vehiclesBonus is None:
            _logger.error('Wrong bonus count for Battme Matters main reward view. Exiting.')
            return
        else:
            vehicleVMs = sorted(BattleMattersVehiclesBonusUIPacker.pack(vehiclesBonus), cmp=_vehiclesSortOrder)
            with self.viewModel.transaction() as tx:
                vehicles = tx.getVehicles()
                vehicles.clear()
                for vehicle in vehicleVMs:
                    vehicles.addViewModel(vehicle)

                vehicles.invalidate()
            return
