# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/BattleTypeSelectPopover.py
from adisp import process
from frameworks.wulf import WindowLayer
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
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.lobby_context import ILobbyContext

class BattleTypeSelectPopover(BattleTypeSelectPopoverMeta):
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

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
            elif itemData == PREBATTLE_ACTION_NAME.RTS:
                tooltip, isSpecial = TOOLTIPS_CONSTANTS.RTS_SELECTOR_INFO, True
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
            elif itemData == PREBATTLE_ACTION_NAME.MAPBOX:
                tooltip = TOOLTIPS_CONSTANTS.MAPBOX_SELECTOR_INFO
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

    def _populate(self):
        super(BattleTypeSelectPopover, self)._populate()
        self.update()

    def __getRankedAvailabilityData(self):
        return (TOOLTIPS_CONSTANTS.RANKED_SELECTOR_INFO, True) if self.__rankedController.isAvailable() else (TOOLTIPS_CONSTANTS.RANKED_UNAVAILABLE_INFO, True)

    def __getEpicAvailabilityData(self):
        return (TOOLTIPS_CONSTANTS.EPIC_BATTLE_SELECTOR_INFO, True)

    @process
    def __selectFight(self, actionName):
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if not navigationPossible:
            return
        battle_selector_items.getItems().select(actionName)
