# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/user_missions_presenter.py
from __future__ import absolute_import
import typing
from frameworks.wulf import ViewStatus
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.hangar.user_missions_widget_model import UserMissionsWidgetModel
from gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import OverlapCtrlMixin
from gui.impl.lobby.user_missions.hangar_widget.presenters.battle_pass_presenter import BattlePassPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.event_banners_presenter import EventBannersPresenter
from gui.impl.lobby.user_missions.hangar_widget.presenters.quests_presenter import QuestsPresenter
from gui.impl.lobby.user_missions.hangar_widget.services import IBattlePassService, IEventsService, IMissionsService, ICampaignService
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Optional

class UserMissionsPresenter(ViewComponent[UserMissionsWidgetModel]):
    eventsCache = dependency.descriptor(IEventsCache)
    __battlePassService = dependency.descriptor(IBattlePassService)
    __eventsService = dependency.descriptor(IEventsService)
    __missionsService = dependency.descriptor(IMissionsService)
    __campaignService = dependency.descriptor(ICampaignService)
    _WIDGET_ALIAS = R.aliases.user_missions.hangarWidget
    _CHILDREN = {_WIDGET_ALIAS.BattlePass(): BattlePassPresenter,
     _WIDGET_ALIAS.Events(): EventBannersPresenter,
     _WIDGET_ALIAS.Quests(): QuestsPresenter}

    def __init__(self):
        super(UserMissionsPresenter, self).__init__(model=UserMissionsWidgetModel)

    @property
    def viewModel(self):
        return super(UserMissionsPresenter, self).getViewModel()

    def _getBaseEvents(self):
        return super(UserMissionsPresenter, self)._getEvents()

    def _getEvents(self):
        baseEvents = self._getBaseEvents()
        return baseEvents + ((self.__battlePassService.onBattlePassChanged, self._onBattlePassEvent),
         (self.__eventsService.onEventsListChanged, self._onEventsEvent),
         (self.__missionsService.onMissionsChanged, self._onMissionsEvent),
         (self.__campaignService.onEventsListChanged, self._onEventsEvent),
         (self.viewModel.onPresenterDisappear, self._onPresenterDisappear),
         (self.viewModel.onWidgetUnmounted, self._onWidgetUnmounted))

    def _onLoading(self, *args, **kwargs):
        super(UserMissionsPresenter, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            self._updateBattlePass(vm)
            self._updateEntryPoints(vm)
            self._updateMissions(vm)

    def _onBattlePassEvent(self):
        with self.viewModel.transaction() as vm:
            self._updateBattlePass(vm)

    def _onEventsEvent(self):
        with self.viewModel.transaction() as vm:
            self._updateEntryPoints(vm)

    def _onMissionsEvent(self):
        with self.viewModel.transaction() as vm:
            self._updateMissions(vm)

    def _onPresenterDisappear(self, args):
        self._removeChild(int(args.get('resId')))

    def _onWidgetUnmounted(self):
        for posId in self._CHILDREN:
            child = self._getChild(posId)
            if isinstance(child, OverlapCtrlMixin):
                child.onWidgetUnmounted()

    def _updateBattlePass(self, vm):
        isAvailable = self.__battlePassService.isVisible()
        self._addChild(self._WIDGET_ALIAS.BattlePass(), isAvailable)
        vm.setIsBattlePassActive(isAvailable)

    def _updateEntryPoints(self, vm):
        isAvailable = len(self.__eventsService.getEntries() + self.__campaignService.getEntries()) > 0
        self._addChild(self._WIDGET_ALIAS.Events(), isAvailable)
        vm.setIsAnyEntryPointAvailable(isAvailable)

    def _updateMissions(self, vm):
        isVisible = bool(self.__missionsService.isVisible())
        self._addChild(self._WIDGET_ALIAS.Quests(), isVisible)
        vm.setAreMissionsActive(isVisible)

    def _addChild(self, posId, isEnable):
        child = self._getChild(posId)
        if child or not isEnable:
            return
        child = self._CHILDREN[posId]()
        self._registerChild(posId, child)
        if child.viewStatus in [ViewStatus.UNDEFINED, ViewStatus.CREATED, ViewStatus.LOADING]:
            self._prepareChild(child.uniqueID, child)

    def _removeChild(self, posId):
        uid = self._childrenUidByPosition.get(posId, None)
        self._unregisterChild(uid, True)
        return
