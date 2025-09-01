# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/spec_mode_selector_item.py
import operator
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.prb_control.entities.battle_session.legacy.requester import AutoInvitesRequester
from helpers import dependency
from shared_utils import first
from skeletons.gui.impl import IGuiLoader

class SpecModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ('__requester',)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def handleClick(self):
        from gui.impl.lobby.mode_selector.states import BattleSessionState
        BattleSessionState.goTo()

    def _getIsDisabled(self):
        return False

    def _onInitializing(self):
        super(SpecModeSelectorItem, self)._onInitializing()
        self.__requester = AutoInvitesRequester()
        self.__requester.start(self.__onListReceived)
        self.__requester.request()

    def _onDisposing(self):
        self.__requester.stop()
        super(SpecModeSelectorItem, self)._onDisposing()

    def __onListReceived(self, sessions):
        item = first(sorted(sessions, key=operator.attrgetter('startTime')))
        if item:
            self.viewModel.setStatusActive(backport.text(R.strings.mode_selector.mode.specBattlesList.call.c_2(), date=backport.getShortDateFormat(item.startTime), time=backport.getShortTimeFormat(item.startTime)))
        else:
            self.viewModel.setStatusActive(backport.text(R.strings.mode_selector.mode.specBattlesList.call.c_1()))
