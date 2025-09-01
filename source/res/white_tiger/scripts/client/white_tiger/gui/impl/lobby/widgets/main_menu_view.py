# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/widgets/main_menu_view.py
from gui.impl.lobby.hangar.presenters.main_menu_presenter import MainMenuPresenter
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from white_tiger.skeletons.white_tiger_controller import IWhiteTigerController

class MainMenuView(MainMenuPresenter):
    __wtCtrl = dependency.descriptor(IWhiteTigerController)

    def _getCallbacks(self):
        return super(MainMenuView, self)._getCallbacks() + (('tokens', self.__onTokensUpdate),)

    def __onTokensUpdate(self, diff):
        if self.__wtCtrl.isEventPrbActive() and ('wtevent:' in key for key in diff.keys()):
            g_eventBus.handleEvent(events.FightButtonEvent(events.FightButtonEvent.FIGHT_BUTTON_UPDATE), scope=EVENT_BUS_SCOPE.LOBBY)
