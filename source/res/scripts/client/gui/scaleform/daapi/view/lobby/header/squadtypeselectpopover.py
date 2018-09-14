# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/SquadTypeSelectPopover.py
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.daapi.view.meta.SquadTypeSelectPopoverMeta import SquadTypeSelectPopoverMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.prb_helpers import prbDispatcherProperty
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.prb_control.context import PrebattleAction

class SquadTypeSelectPopover(SquadTypeSelectPopoverMeta, SmartPopOverView, View, AppRef):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def selectFight(self, actionName):
        if self.prbDispatcher is not None:
            self.prbDispatcher.doSelectAction(PrebattleAction(actionName))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return

    def getTooltipData(self, itemData):
        if itemData is None:
            return ''
        elif itemData == PREBATTLE_ACTION_NAME.SQUAD:
            return TOOLTIPS.BATTLETYPES_SQUAD
        elif itemData == PREBATTLE_ACTION_NAME.EVENT_SQUAD:
            return TOOLTIPS.BATTLETYPES_EVENTSQUAD
        else:
            return ''

    def update(self):
        if not self.isDisposed():
            self.as_updateS(battle_selector_items.getItems().getSquadVOs())

    def _populate(self):
        super(SquadTypeSelectPopover, self)._populate()
        self.update()
