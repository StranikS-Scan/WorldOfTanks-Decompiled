# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/SquadTypeSelectPopover.py
from __future__ import absolute_import
from adisp import adisp_process
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.meta.BattleTypeSelectPopoverMeta import BattleTypeSelectPopoverMeta
from gui.Scaleform.locale.PLATOON import PLATOON
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener

class SquadTypeSelectPopover(BattleTypeSelectPopoverMeta, IGlobalListener):

    def __init__(self, _=None):
        super(SquadTypeSelectPopover, self).__init__()

    def selectFight(self, actionName):
        if self.prbDispatcher:
            self.__doSelect(actionName)
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')

    def getTooltipData(self, itemData, itemIsDisabled):
        tooltip = ''
        if itemData == 'eventSquad':
            tooltip = PLATOON.HEADERBUTTON_TOOLTIPS_EVENTSQUAD
        elif itemData == 'squad':
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

    @adisp_process
    def __doSelect(self, prebattleActionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(prebattleActionName))
