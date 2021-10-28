# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/SquadTypeSelectPopover.py
from adisp import process
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.meta.BattleTypeSelectPopoverMeta import BattleTypeSelectPopoverMeta
from gui.Scaleform.locale.PLATOON import PLATOON
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui.prb_control.settings import PREBATTLE_ACTION_NAME

class SquadTypeSelectPopover(BattleTypeSelectPopoverMeta, IGlobalListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, _=None):
        super(SquadTypeSelectPopover, self).__init__()

    def selectFight(self, actionName):
        self.__selectFight(actionName)

    @process
    def __selectFight(self, actionName):
        if actionName == PREBATTLE_ACTION_NAME.EVENT_SQUAD or actionName == PREBATTLE_ACTION_NAME.SQUAD:
            navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
            if not navigationPossible:
                return
        if self.prbDispatcher:
            self.__doSelect(actionName)
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')

    def getTooltipData(self, itemData, itemIsDisabled):
        tooltip = ''
        if itemData == PREBATTLE_ACTION_NAME.EVENT_SQUAD:
            tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_EVENTSQUAD
        elif itemData == PREBATTLE_ACTION_NAME.SQUAD:
            tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_SQUAD
        return tooltip

    def demoClick(self):
        pass

    def update(self):
        if not self.isDisposed():
            self.as_updateS(*battle_selector_items.getSquadItems().getVOs())

    def _populate(self):
        super(SquadTypeSelectPopover, self)._populate()
        self.update()

    @process
    def __doSelect(self, prebattleActionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(prebattleActionName))
