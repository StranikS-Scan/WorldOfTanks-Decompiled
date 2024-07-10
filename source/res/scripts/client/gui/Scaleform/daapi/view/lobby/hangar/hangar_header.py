# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/hangar_header.py
import logging
import typing
import BigWorld
import constants
from CurrentVehicle import g_currentVehicle
from gui import g_guiResetters
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.flag_constants import QuestFlagTypes
from gui.Scaleform.daapi.view.meta.HangarHeaderMeta import HangarHeaderMeta
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.battle_pass.battle_pass_helpers import getSupportedArenaBonusTypeFor
from gui.event_boards.listener import IEventBoardsListener
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.battle_matters import IBattleMattersController
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IBattlePassController, IResourceWellController, IHangarGuiController, IMarathonEventsController, IFestivityController, IRankedBattlesController, IBattleRoyaleController, IMapboxController, ILimitedUIController, ILiveOpsWebEventsController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

class ActiveWidgets(object):
    LEFT = 1
    CENTER = 2
    RIGHT = 3

    def __init__(self):
        self.__widgets = {self.LEFT: '',
         self.CENTER: '',
         self.RIGHT: ''}
        super(ActiveWidgets, self).__init__()

    def update(self, position, alias):
        if position in self.__widgets:
            if self.__widgets[position] != alias:
                self.__widgets[position] = alias
                return True
        return False


_SCREEN_WIDTH_FOR_MARATHON_GROUP = 1300

class HangarHeader(HangarHeaderMeta, IGlobalListener, IEventBoardsListener):
    __slots__ = ('_currentVehicle', '__screenWidth')
    __battleMattersController = dependency.descriptor(IBattleMattersController)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    _eventsCache = dependency.descriptor(IEventsCache)
    _eventsController = dependency.descriptor(IEventBoardController)
    _festivityController = dependency.descriptor(IFestivityController)
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __liveOpsWebEventsController = dependency.descriptor(ILiveOpsWebEventsController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self):
        super(HangarHeader, self).__init__()
        self._currentVehicle = None
        self.__screenWidth = None
        self.__activeWidgets = None
        return

    def onQuestBtnClick(self, questType, questID):
        _, flagsGetter = self.__hangarGuiCtrl.getHangarHeaderBlock()
        if flagsGetter is not None:
            flagsGetter.showQuestsInfo(questType, questID)
        return

    def onUpdateHangarFlag(self):
        self.update()

    def onPrbEntitySwitched(self):
        super(HangarHeader, self).onPrbEntitySwitched()
        self.__updateBattleMattersEntryPoint()

    def update(self, *_):
        headerVO = self._makeHeaderVO()
        self.as_setDataS(headerVO)
        self.__updateWidget()
        self.__updateRightWidget()

    def _populate(self):
        super(HangarHeader, self)._populate()
        self._currentVehicle = g_currentVehicle
        self.__screenWidth = BigWorld.screenSize()[0]
        self.__activeWidgets = ActiveWidgets()
        self._eventsCache.onSyncCompleted += self.update
        self._eventsCache.onProgressUpdated += self.update
        self._festivityController.onStateChanged += self.update
        self.__battlePassController.onSeasonStateChanged += self.update
        self.__battleRoyaleController.onPrimeTimeStatusUpdated += self.update
        self.__rankedController.onGameModeStatusUpdated += self.update
        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.update
        self.__mapboxCtrl.addProgressionListener(self.update)
        self.__resourceWell.onEventUpdated += self.update
        self.__liveOpsWebEventsController.onSettingsChanged += self.__updateRightWidget
        self.__liveOpsWebEventsController.onEventStateChanged += self.__updateRightWidget
        self.__battleMattersController.onStateChanged += self.__onBattleMattersStateChanged
        self.__battleMattersController.onFinish += self.__onBattleMattersStateChanged
        self.__limitedUIController.startObserve(LuiRules.BP_ENTRY, self.__updateBattlePassWidgetVisibility)
        self.__limitedUIController.startObserve(LuiRules.BATTLE_MISSIONS, self.__updateVOHeader)
        self.__limitedUIController.startObserve(LuiRules.BM_FLAG, self.__updateBattleMattersEntryPoint)
        self.__limitedUIController.startObserve(LuiRules.PERSONAL_MISSIONS, self.__updateVOHeader)
        self.__limitedUIController.startObserve(LuiRules.LIVE_OPS_WEB_EVENTS_ENTRY_POINT, self.__updateRightWidget)
        self.__updateBattleMattersEntryPoint()
        g_clientUpdateManager.addCallbacks({'inventory.1': self.update})
        if self._eventsController:
            self._eventsController.addListener(self)
        self._marathonsCtrl.onFlagUpdateNotify += self.update
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_guiResetters.add(self.__onChangeScreenResolution)
        self.startGlobalListening()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._marathonsCtrl.onFlagUpdateNotify -= self.update
        self.__mapboxCtrl.removeProgressionListener(self.update)
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.update
        self._eventsCache.onSyncCompleted -= self.update
        self._eventsCache.onProgressUpdated -= self.update
        self._festivityController.onStateChanged -= self.update
        self.__battlePassController.onSeasonStateChanged -= self.update
        self.__battleRoyaleController.onPrimeTimeStatusUpdated -= self.update
        self.__rankedController.onGameModeStatusUpdated -= self.update
        self.__resourceWell.onEventUpdated -= self.update
        self.__liveOpsWebEventsController.onEventStateChanged -= self.__updateRightWidget
        self.__liveOpsWebEventsController.onSettingsChanged -= self.__updateRightWidget
        self.__battleMattersController.onStateChanged -= self.__onBattleMattersStateChanged
        self.__battleMattersController.onFinish -= self.__onBattleMattersStateChanged
        self.__limitedUIController.stopObserve(LuiRules.BP_ENTRY, self.__updateBattlePassWidgetVisibility)
        self.__limitedUIController.stopObserve(LuiRules.BATTLE_MISSIONS, self.__updateVOHeader)
        self.__limitedUIController.stopObserve(LuiRules.BM_FLAG, self.__updateBattleMattersEntryPoint)
        self.__limitedUIController.stopObserve(LuiRules.PERSONAL_MISSIONS, self.__updateVOHeader)
        self.__limitedUIController.stopObserve(LuiRules.LIVE_OPS_WEB_EVENTS_ENTRY_POINT, self.__updateRightWidget)
        self._currentVehicle = None
        self.__screenWidth = None
        self.__activeWidgets = None
        if self._eventsController:
            self._eventsController.removeListener(self)
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_guiResetters.remove(self.__onChangeScreenResolution)
        self.stopGlobalListening()
        super(HangarHeader, self)._dispose()
        return

    def _makeHeaderVO(self):
        isVisible, flagsGetter = self.__hangarGuiCtrl.getHangarHeaderBlock()
        if flagsGetter is None:
            return {'isVisible': isVisible,
             'quests': []}
        else:
            isGrouped = self.__screenWidth <= _SCREEN_WIDTH_FOR_MARATHON_GROUP
            params = {QuestFlagTypes.MARATHON: {'isGrouped': isGrouped}}
            quests = flagsGetter.getVO(self._currentVehicle.item, params)
            return {'isVisible': isVisible,
             'quests': quests}

    def __onChangeScreenResolution(self):
        self.__screenWidth = BigWorld.screenSize()[0]
        self.update()

    def __onBattleMattersStateChanged(self):
        self.__updateBattleMattersEntryPoint()

    def __onServerSettingChanged(self, diff):
        if 'elenSettings' in diff or constants.PremiumConfigs.PREM_QUESTS in diff:
            self.update()

    def __getCurentArenaBonusType(self):
        queueType = None
        isInUnit = False
        if self.prbDispatcher is not None and self.prbEntity is not None:
            state = self.prbDispatcher.getFunctionalState()
            isInUnit = state.isInUnit(state.entityTypeID)
            queueType = self.prbEntity.getQueueType()
        return getSupportedArenaBonusTypeFor(queueType, isInUnit)

    def __getBPWidget(self):
        isBPAvailable = not self.__battlePassController.isDisabled()
        isValidBattleType = self.prbDispatcher and self.prbDispatcher.getEntity() and self.__battlePassController.isValidBattleType(self.prbDispatcher.getEntity())
        isRuleCompleted = self.__limitedUIController.isRuleCompleted(LuiRules.BP_ENTRY)
        isVisible = isBPAvailable and isValidBattleType and isRuleCompleted
        return HANGAR_ALIASES.BATTLE_PASSS_ENTRY_POINT if isVisible else ''

    def __updateWidget(self):
        alias = self.__hangarGuiCtrl.getHangarWidgetAlias() or self.__getBPWidget()
        if not self.__activeWidgets.update(ActiveWidgets.CENTER, alias):
            return
        self.as_addEntryPointS(alias)
        self.__updateBattlePassSmallWidget()

    def __updateBattlePassWidgetVisibility(self, *_):
        self.__updateWidget()

    def __updateBattlePassSmallWidget(self):
        currentArenaBonusType = self.__getCurentArenaBonusType()
        secondaryPointCanBeAvailable = currentArenaBonusType not in (constants.ARENA_BONUS_TYPE.REGULAR,
         constants.ARENA_BONUS_TYPE.UNKNOWN,
         constants.ARENA_BONUS_TYPE.MAPBOX,
         constants.ARENA_BONUS_TYPE.WINBACK)
        isRuleCompleted = self.__limitedUIController.isRuleCompleted(LuiRules.BP_ENTRY)
        secondaryEntryPointAvailable = secondaryPointCanBeAvailable and not self.__battlePassController.isDisabled() and isRuleCompleted
        self.as_setSecondaryEntryPointVisibleS(secondaryEntryPointAvailable)
        if secondaryEntryPointAvailable:
            self.getComponent(HANGAR_ALIASES.SECONDARY_ENTRY_POINT).update(currentArenaBonusType)

    def __updateVOHeader(self, *_):
        headerVO = self._makeHeaderVO()
        self.as_setDataS(headerVO)

    def __updateRightWidget(self, *_):
        isRandom = self.__getCurentArenaBonusType() in (constants.ARENA_BONUS_TYPE.REGULAR, constants.ARENA_BONUS_TYPE.WINBACK)
        alias = ''
        if isRandom:
            if self.__resourceWell.isActive() or self.__resourceWell.isPaused() or self.__resourceWell.isNotStarted():
                alias = HANGAR_ALIASES.RESOURCE_WELL_ENTRY_POINT
            elif self.__liveOpsWebEventsController.canShowHangarEntryPoint() and self.__limitedUIController.isRuleCompleted(LuiRules.LIVE_OPS_WEB_EVENTS_ENTRY_POINT):
                alias = HANGAR_ALIASES.LIVE_OPS_WEB_EVENTS_ENTRY_POINT
        if self.__activeWidgets.update(ActiveWidgets.RIGHT, alias):
            self.as_addSecondaryEntryPointS(alias, True)

    def __updateBattleMattersEntryPoint(self, *_):
        isValidArena = self.__getCurentArenaBonusType() in (constants.ARENA_BONUS_TYPE.REGULAR, constants.ARENA_BONUS_TYPE.WINBACK)
        controller = self.__battleMattersController
        isLuiRuleCompleted = self.__limitedUIController.isRuleCompleted(LuiRules.BM_FLAG)
        isBattleMattersMShow = controller.isEnabled() and (not controller.isFinished() or controller.hasDelayedRewards()) and isValidArena and isLuiRuleCompleted
        alias = HANGAR_ALIASES.BATTLE_MATTERS_ENTRY_POINT if isBattleMattersMShow else ''
        if self.__activeWidgets.update(ActiveWidgets.LEFT, alias):
            self.as_addSecondaryEntryPointS(alias, False)
