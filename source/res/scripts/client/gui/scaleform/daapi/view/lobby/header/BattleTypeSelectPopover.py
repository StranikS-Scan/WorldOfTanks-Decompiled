# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/BattleTypeSelectPopover.py
from adisp import process
from frameworks.wulf import WindowLayer
from uilogging.deprecated.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.deprecated.mode_selector.constants import MS_LOG_KEYS, MS_LOG_ACTIONS
from uilogging.deprecated.mode_selector.decorators import logSelectMode, logCloseView, markTooltipOpened, logTooltipClosed
from uilogging.deprecated.mode_selector.loggers import ModeSelectorUILogger
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.meta.BattleTypeSelectPopoverMeta import BattleTypeSelectPopoverMeta
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import LoadViewEvent
from skeletons.gui.game_control import IEpicBattleMetaGameController
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.lobby_context import ILobbyContext

@loggerTarget(logKey=MS_LOG_KEYS.BATTLE_TYPES_VIEW, loggerCls=ModeSelectorUILogger)
class BattleTypeSelectPopover(BattleTypeSelectPopoverMeta):
    __epicQueueController = dependency.descriptor(IEpicBattleMetaGameController)
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __eventsCache = dependency.descriptor(IEventsCache)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, _=None):
        super(BattleTypeSelectPopover, self).__init__()
        self._tooltip = None
        return

    def selectFight(self, actionName):
        self.__selectFight(actionName)

    def getTooltipData(self, itemData, itemIsDisabled):
        if itemData is None:
            return
        else:
            tooltip = ''
            isSpecial = False
            if itemData == PREBATTLE_ACTION_NAME.RANDOM:
                tooltip = TOOLTIPS.BATTLETYPES_STANDART
            elif itemData == PREBATTLE_ACTION_NAME.EPIC:
                tooltip, isSpecial = self.__getEpicAvailabilityData()
            elif itemData == PREBATTLE_ACTION_NAME.RANKED:
                tooltip, isSpecial = self.__getRankedAvailabilityData()
            elif itemData == PREBATTLE_ACTION_NAME.E_SPORT:
                tooltip = TOOLTIPS.BATTLETYPES_UNIT
            elif itemData == PREBATTLE_ACTION_NAME.STRONGHOLDS_BATTLES_LIST:
                if not itemIsDisabled:
                    tooltip = TOOLTIPS.BATTLETYPES_STRONGHOLDS
                else:
                    tooltip = TOOLTIPS.BATTLETYPES_STRONGHOLDS_DISABLED
            elif itemData == PREBATTLE_ACTION_NAME.TRAININGS_LIST:
                tooltip = TOOLTIPS.BATTLETYPES_TRAINING
            elif itemData == PREBATTLE_ACTION_NAME.EPIC_TRAINING_LIST:
                tooltip = TOOLTIPS.BATTLETYPES_EPIC_TRAINING
            elif itemData == PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST:
                tooltip = TOOLTIPS.BATTLETYPES_SPEC
            elif itemData == PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL:
                tooltip = TOOLTIPS.BATTLETYPES_BATTLETUTORIAL
            elif itemData == PREBATTLE_ACTION_NAME.SANDBOX:
                isSpecial = True
                tooltip = TOOLTIPS_CONSTANTS.BATTLE_TRAINING
            elif itemData == PREBATTLE_ACTION_NAME.BATTLE_ROYALE:
                tooltip = TOOLTIPS_CONSTANTS.BATTLE_ROYALE_SELECTOR_INFO
                isSpecial = True
            result = {'isSpecial': isSpecial,
             'tooltip': tooltip}
            self._tooltip = tooltip
            return result

    def demoClick(self):
        demonstratorWindow = self.app.containerManager.getView(WindowLayer.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.DEMONSTRATOR_WINDOW})
        if demonstratorWindow is not None:
            demonstratorWindow.onWindowClose()
        else:
            self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.DEMONSTRATOR_WINDOW)), EVENT_BUS_SCOPE.LOBBY)
        return

    def update(self):
        if not self.isDisposed():
            self.as_updateS(*battle_selector_items.getItems().getVOs())

    @loggerEntry
    @simpleLog(action=MS_LOG_ACTIONS.OPEN)
    def _populate(self):
        app = self.__appLoader.getApp()
        if app and app.getToolTipMgr():
            app.getToolTipMgr().onShow += self.__onShowTooltip
            app.getToolTipMgr().onHide += self.__onHideTooltip
        super(BattleTypeSelectPopover, self)._populate()
        self.update()

    @logCloseView
    def _dispose(self):
        super(BattleTypeSelectPopover, self)._dispose()
        app = self.__appLoader.getApp()
        if app and app.getToolTipMgr():
            app.getToolTipMgr().onShow -= self.__onShowTooltip
            app.getToolTipMgr().onHide -= self.__onHideTooltip

    def __getRankedAvailabilityData(self):
        return (TOOLTIPS_CONSTANTS.RANKED_SELECTOR_INFO, True) if self.__rankedController.isAvailable() else (TOOLTIPS_CONSTANTS.RANKED_UNAVAILABLE_INFO, True)

    def __getEpicAvailabilityData(self):
        return (TOOLTIPS_CONSTANTS.EVENT_PROGRESSION_SELECTOR_INFO, True)

    @logSelectMode
    @process
    def __selectFight(self, actionName):
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if not navigationPossible:
            return
        battle_selector_items.getItems().select(actionName)

    @markTooltipOpened
    def __onShowTooltip(self, tooltip, advanced):
        pass

    @logTooltipClosed(timeLimit=2)
    def __onHideTooltip(self, tooltip):
        pass
