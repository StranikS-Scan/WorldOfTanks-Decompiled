# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/header/BattleTypeSelectPopover.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.Scaleform.daapi.view.lobby.popover.SmartPopOverView import SmartPopOverView
from gui.Scaleform.daapi.view.meta.BattleTypeSelectPopoverMeta import BattleTypeSelectPopoverMeta
from gui.Scaleform.framework import ViewTypes, AppRef
from gui.Scaleform.framework.entities.View import View
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared.events import LoadViewEvent
from gui.shared.ClanCache import g_clanCache
from gui.shared.fortifications import isStartingScriptDone
from gui import game_control

class BattleTypeSelectPopover(BattleTypeSelectPopoverMeta, SmartPopOverView, View, AppRef):

    def __init__(self, ctx = None):
        super(BattleTypeSelectPopover, self).__init__()

    def selectFight(self, actionName):
        battle_selector_items.getItems().select(actionName)

    def getTooltipData(self, itemData):
        if itemData is None:
            return ''
        isInRoaming = game_control.g_instance.roaming.isInRoaming()
        if itemData == PREBATTLE_ACTION_NAME.JOIN_RANDOM_QUEUE:
            return TOOLTIPS.BATTLETYPES_STANDART
        elif itemData == PREBATTLE_ACTION_NAME.HISTORICAL:
            return TOOLTIPS.BATTLETYPES_HISTORICAL
        elif itemData == PREBATTLE_ACTION_NAME.UNIT:
            return TOOLTIPS.BATTLETYPES_UNIT
        elif itemData == PREBATTLE_ACTION_NAME.COMPANY:
            return TOOLTIPS.BATTLETYPES_COMPANY
        elif itemData == PREBATTLE_ACTION_NAME.FORT:
            if not g_clanCache.isInClan:
                return '#tooltips:fortification/disabled/no_clan'
            if not isStartingScriptDone():
                return '#tooltips:fortification/disabled/no_fort'
            return TOOLTIPS.BATTLETYPES_FORTIFICATION
        elif itemData == PREBATTLE_ACTION_NAME.TRAINING:
            return TOOLTIPS.BATTLETYPES_TRAINING
        elif itemData == PREBATTLE_ACTION_NAME.SPEC_BATTLE:
            return TOOLTIPS.BATTLETYPES_SPEC
        elif itemData == PREBATTLE_ACTION_NAME.BATTLE_TUTORIAL:
            return TOOLTIPS.BATTLETYPES_BATTLETUTORIAL
        else:
            return ''

    def demoClick(self):
        demonstratorWindow = self.app.containerManager.getView(ViewTypes.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.DEMONSTRATOR_WINDOW})
        if demonstratorWindow is not None:
            demonstratorWindow.onWindowClose()
        else:
            self.fireEvent(LoadViewEvent(VIEW_ALIAS.DEMONSTRATOR_WINDOW))
        return

    def update(self):
        if not self.isDisposed():
            self.as_updateS(*battle_selector_items.getItems().getVOs())

    def _populate(self):
        super(BattleTypeSelectPopover, self)._populate()
        self.update()

    def _dispose(self):
        super(BattleTypeSelectPopover, self)._dispose()
