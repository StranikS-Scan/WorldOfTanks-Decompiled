# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/SquadTypeSelectPopover.py
from adisp import process
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.meta.BattleTypeSelectPopoverMeta import BattleTypeSelectPopoverMeta
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.utils.functions import makeTooltip
_SQUAD_SELECTOR_TEMPLATE = 'html_templates:lobby/tooltips/squad_selector'

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
            tooltip = makeTooltip(backport.text(R.strings.tooltips.header.eventSquad.header()), makeHtmlString(_SQUAD_SELECTOR_TEMPLATE, 'event'))
        elif itemData == 'squad':
            tooltip = makeTooltip(backport.text(R.strings.tooltips.header.squad.header()), makeHtmlString(_SQUAD_SELECTOR_TEMPLATE, 'regular'))
        result = {'isSpecial': False,
         'tooltip': tooltip}
        return result

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
