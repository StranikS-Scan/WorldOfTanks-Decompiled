# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/full_stats/personal_reserves_tab_view.py
import logging
import typing
import BigWorld
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PERSONAL_RESOURCE_ORDER
from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import getPersonalBoosterModelDataByResourceType, addPersonalBoostersGroup, addEventGroup
from gui.impl.gen import R
from gui.impl.gen.view_models.views.battle.battle_page.personal_reserves_tab_view_model import PersonalReservesTabViewModel
from gui.impl.gui_decorators import args2params
from gui.impl.lobby.personal_reserves.personal_reserves_utils import generatePersonalReserveTick
from gui.impl.pub import ViewImpl
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from skeletons.gui.goodies import IBoostersStateProvider
from frameworks.wulf import ViewModel
if typing.TYPE_CHECKING:
    from typing import List, Dict
    from frameworks.wulf import Array
    from frameworks.wulf.view.view import View
    from frameworks.wulf.view.view_event import ViewEvent
    from gui.goodies.booster_state_provider import BoosterStateProvider
    from gui.impl.gen.view_models.common.personal_reserves.reserves_group_model import ReservesGroupModel
    from gui.impl.common.personal_reserves.personal_reserves_shared_model_utils import BoosterModelData
_logger = logging.getLogger(__name__)

class PersonalReservesTabView(ViewImpl):
    __slots__ = ('_notificatorManager',)
    _boostersStateProvider = dependency.descriptor(IBoostersStateProvider)

    def __init__(self):
        settings = ViewSettings(R.views.battle.battle_page.PersonalReservesTabView(), ViewFlags.VIEW, PersonalReservesTabViewModel())
        super(PersonalReservesTabView, self).__init__(settings)
        self._notificatorManager = Notifiable()

    @property
    def viewModel(self):
        return super(PersonalReservesTabView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.personal_reserves.ReservesDisabledTooltip():
            settings = ViewSettings(layoutID=R.views.common.personal_reserves.ReservesDisabledTooltip(), model=ViewModel())
            return ViewImpl(settings)
        return super(PersonalReservesTabView, self).createToolTipContent(event, contentID)

    def _finalize(self):
        self._notificatorManager.clearNotification()
        super(PersonalReservesTabView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onBoosterActivate, self.onBoosterActivate), (self._boostersStateProvider.onStateUpdated, self._update))

    def _onLoading(self, *args, **kwargs):
        super(PersonalReservesTabView, self)._onLoading(*args, **kwargs)
        self._notificatorManager.addNotificator(PeriodicNotifier(self._timeTillNextPersonalReserveTick, self.fillViewModel))
        self._update()

    def activatePersonalReserve(self, boosterId):
        BigWorld.player().activateGoodie(boosterId)

    @args2params(int)
    def onBoosterActivate(self, boosterId):
        booster = self._boostersStateProvider.getBooster(boosterId)
        if booster.boosterType in self._boostersStateProvider.getActiveBoosterTypes():
            _logger.warning('[PersonalReservesTabView] Booster %d cannot be activated as another booster of the same type is already active in this battle.', booster.boosterID)
            return
        if booster.isInAccount:
            self.activatePersonalReserve(boosterId)
        else:
            _logger.warning('[PersonalReservesTabView] Cannot activate booster %d, player does not have this booster in inventory. Buy and activate action is not possible during battle.', booster.boosterID)

    def _update(self):
        self._notificatorManager.startNotification()
        self.fillViewModel()

    def fillViewModel(self):
        boosterModelsArgsByType = getPersonalBoosterModelDataByResourceType(self._boostersStateProvider)
        with self.viewModel.transaction() as model:
            groupArray = model.getReserveGroups()
            groupArray.clear()
            for resourceType in PERSONAL_RESOURCE_ORDER:
                addPersonalBoostersGroup(resourceType, boosterModelsArgsByType, groupArray)

            addEventGroup(groupArray, self._boostersStateProvider)
            groupArray.invalidate()

    def _timeTillNextPersonalReserveTick(self):
        expiringReserves = self._boostersStateProvider.getBoosters(REQ_CRITERIA.BOOSTER.LIMITED).values()
        return generatePersonalReserveTick(expiringReserves)
