# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/event/event_king_reward_preview.py
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl.gen.view_models.views.lobby.halloween.meta_view_model import PageTypeEnum
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_dispatcher import showMetaView, showHangar
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from CurrentVehicle import g_currentPreviewVehicle
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from CurrentVehicle import HeroTankPreviewAppearance

class EventKingRewardPreview(VehiclePreview):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, ctx=None):
        super(EventKingRewardPreview, self).__init__(ctx)
        self.hideBottomPanel = ctx.get('hideBottomPanel')
        self._rewardController = self._gameEventController.getEventRewardController()
        self.__rewardBoxIsEnabled = self._gameEventController.isEnabled() and self._gameEventController.isEventCurrentDateActive() and self._rewardController.isEnabled()

    def _populate(self):
        super(EventKingRewardPreview, self)._populate()
        self.updateHeaderMenu(HeaderMenuVisibilityState.NOTHING)
        g_currentPreviewVehicle.onChanged()
        self._gameEventController.onIngameEventsUpdated += self._onIngemaEventsChanged

    def _dispose(self):
        self.updateHeaderMenu(HeaderMenuVisibilityState.ALL)
        self._gameEventController.onIngameEventsUpdated -= self._onIngemaEventsChanged
        super(EventKingRewardPreview, self)._dispose()

    def updateHeaderMenu(self, state):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': state}), scope=EVENT_BUS_SCOPE.LOBBY)

    def setBottomPanel(self):
        if self.__rewardBoxIsEnabled and not self.hideBottomPanel:
            self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.EVENT_KING_REWARD)

    def _onIngemaEventsChanged(self):
        if self.__rewardBoxIsEnabled != (self._gameEventController.isEnabled() and self._gameEventController.isEventCurrentDateActive() and self._rewardController.isEnabled()):
            showHangar()

    def _getBackBtnLabel(self):
        return VEHICLE_PREVIEW.HEADER_BACKBTN_DESCRLABEL_HALLOWEENMETAREWARDS if self._backAlias == VIEW_ALIAS.HALLOWEEN_META_REWARDS else VEHICLE_PREVIEW.HEADER_BACKBTN_DESCRLABEL_HANGAR

    def _processBackClick(self, ctx=None):
        if self._backAlias == VIEW_ALIAS.HALLOWEEN_META_REWARDS and ctx is None:
            showMetaView(PageTypeEnum.FINAL_REWARD.value)
        else:
            showHangar()
        return

    def _getExitEvent(self):
        return events.LoadViewEvent(SFViewLoadParams(self.alias), ctx={'previewAppearance': HeroTankPreviewAppearance(),
         'itemCD': self._vehicleCD,
         'previewAlias': self._backAlias,
         'previousBackAlias': self._previousBackAlias,
         'previewBackCb': self._previewBackCb,
         'isHeroTank': True,
         'hideBottomPanel': self.hideBottomPanel})
