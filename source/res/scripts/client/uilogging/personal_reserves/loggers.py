# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/personal_reserves/loggers.py
import json
import logging
from typing import TYPE_CHECKING
import BigWorld
from constants import ARENA_PERIOD
from gui.impl.gen.view_models.views.dialogs.dialog_template_view_model import DialogTemplateViewModel
from gui.impl.pub.dialog_window import DialogButtons
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.impl import IGuiLoader
from uilogging.base.logger import MetricsLogger, FlowLogger
from uilogging.personal_reserves.logging_constants import FEATURE, PersonalReservesLogKeys, PersonalReservesLogActions, MIN_VIEW_TIME, PersonalReservesLogNotifications, PersonalReservesLogButtons, PersonalReservesLogDialogs, ACTIVATION_LAYOUT_ID, PersonalReservesLogClicks, ARENA_PERIOD_KEY, ARENA_PERIOD_TO_KEY, SECONDS_SINCE_BATTLE_STARTED_KEY, BATTLE_DURATION_KEY
from wotdecorators import noexcept
if TYPE_CHECKING:
    from uilogging.types import InfoType, ParentScreenType, ItemType
    from gui.impl.gui_loader import GuiLoader
_logger = logging.getLogger(__name__)

class PersonalReservesMetricsLogger(MetricsLogger):
    __slots__ = ('_parent', '_item')

    def __init__(self, parent, item):
        super(PersonalReservesMetricsLogger, self).__init__(FEATURE)
        self._item = item
        self._parent = parent

    def onViewInitialize(self):
        self.startAction(action=PersonalReservesLogActions.VIEWED)

    @noexcept
    def onViewFinalize(self):
        self.stopAction(action=PersonalReservesLogActions.VIEWED, item=self._item, parentScreen=self._parent, info=self._getInfo(), timeLimit=MIN_VIEW_TIME)

    def _getInfo(self):
        return None


class PersonalReservesFlowLogger(FlowLogger):
    __slots__ = ()

    def __init__(self):
        super(PersonalReservesFlowLogger, self).__init__(FEATURE)


class PersonalReservesActivationScreenFlowLogger(PersonalReservesFlowLogger):
    __slots__ = ()
    _guiLoader = dependency.descriptor(IGuiLoader)

    @noexcept
    def logOpenFromNotification(self):
        if self.canLog():
            self.log(action=PersonalReservesLogActions.OPEN, sourceItem=PersonalReservesLogNotifications.EXPIRE, destinationItem=PersonalReservesLogKeys.ACTIVATION_WINDOW, transitionMethod=PersonalReservesLogButtons.TO_RESERVES)

    def canLog(self):
        if self.disabled:
            return False
        else:
            view = self._guiLoader.windowsManager.getViewByLayoutID(ACTIVATION_LAYOUT_ID)
            return view is None

    @noexcept
    def logOpenFromWidgetClick(self):
        if self.canLog():
            self.log(action=PersonalReservesLogActions.OPEN, sourceItem=PersonalReservesLogKeys.WIDGET, destinationItem=PersonalReservesLogKeys.ACTIVATION_WINDOW, transitionMethod=PersonalReservesLogClicks.WIDGET_CLICKED)


SUBMIT_BUTTON_BY_DIALOG = {PersonalReservesLogDialogs.BUY_AND_ACTIVATE: PersonalReservesLogButtons.BUY_AND_ACTIVATE,
 PersonalReservesLogDialogs.BUY_AND_UPGRADE: PersonalReservesLogButtons.BUY_AND_ACTIVATE,
 PersonalReservesLogDialogs.BUY_GOLD: PersonalReservesLogButtons.BUY_GOLD}
BUTTON_TO_ITEM_MAP = {DialogButtons.CANCEL: PersonalReservesLogButtons.CANCEL,
 DialogTemplateViewModel.DEFAULT: PersonalReservesLogButtons.EXIT,
 DialogTemplateViewModel.ESCAPE: PersonalReservesLogButtons.EXIT}

class BuyAndActivateDialogsLogger(MetricsLogger):
    __slots__ = ('_item',)

    def __init__(self, item):
        super(BuyAndActivateDialogsLogger, self).__init__(FEATURE)
        self._item = item

    def logOpenDialog(self):
        self.log(action=PersonalReservesLogActions.OPEN, item=self._item, parentScreen=PersonalReservesLogKeys.ACTIVATION_WINDOW)

    def logButtonClick(self, button):
        if button == DialogButtons.SUBMIT:
            loggedItem = SUBMIT_BUTTON_BY_DIALOG.get(self._item)
            if loggedItem is None:
                _logger.warning('[PR2UILOG] Cannot find dialog in SUBMIT_BUTTON_BY_DIALOG - dialog %s, keys %s', self._item, SUBMIT_BUTTON_BY_DIALOG.keys())
                return
        else:
            loggedItem = BUTTON_TO_ITEM_MAP.get(button)
            if loggedItem is None:
                _logger.warning('[PR2UILOG] Button could not be mapped to log item - button %s, keys %s', button, BUTTON_TO_ITEM_MAP.keys())
                return
        self.log(action=PersonalReservesLogActions.CLICK, item=loggedItem, parentScreen=self._item)
        return


class PersonalReservesFullStatsLogger(PersonalReservesMetricsLogger):
    __slots__ = ()
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(PersonalReservesFullStatsLogger, self).__init__(parent=PersonalReservesLogKeys.BATTLE.value, item=PersonalReservesLogKeys.ACTIVATION_IN_BATTLE_TAB.value)

    @noexcept
    def _getInfo(self):
        arenaVisitor = self._sessionProvider.arenaVisitor
        arenaPeriod = arenaVisitor.getArenaPeriod()
        arenaPeriodlength = arenaVisitor.getArenaPeriodLength()
        additionalInfo = {ARENA_PERIOD_KEY: ARENA_PERIOD_TO_KEY[arenaPeriod],
         BATTLE_DURATION_KEY: arenaVisitor.getArenaPeriodLength(),
         SECONDS_SINCE_BATTLE_STARTED_KEY: 0}
        startTime = arenaVisitor.getArenaPeriodEndTime() - arenaPeriodlength
        logTime = int(BigWorld.serverTime() - startTime)
        if arenaVisitor.getArenaPeriod() in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE, ARENA_PERIOD.AFTERBATTLE):
            additionalInfo[SECONDS_SINCE_BATTLE_STARTED_KEY] = logTime
        return json.dumps(additionalInfo)
