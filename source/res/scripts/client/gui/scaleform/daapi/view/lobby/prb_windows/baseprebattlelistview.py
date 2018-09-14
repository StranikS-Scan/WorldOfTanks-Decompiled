# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/BasePrebattleListView.py
from gui.Scaleform.daapi.view.meta.BasePrebattleListViewMeta import BasePrebattleListViewMeta
from messenger.gui import events_dispatcher
from messenger.gui.Scaleform.view import MESSENGER_VIEW_ALIAS
__author__ = 'a_ushyutsau'

class BasePrebattleListView(BasePrebattleListViewMeta):

    def __init__(self, name):
        super(BasePrebattleListView, self).__init__()
        self._searchDP = None
        self._name = name
        return

    @property
    def chat(self):
        chat = None
        if MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT in self.components:
            chat = self.components[MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT]
        return chat

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            events_dispatcher.rqActivateLazyChannel(self._name, viewPy)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        if alias == MESSENGER_VIEW_ALIAS.CHANNEL_COMPONENT:
            if self.isMinimising:
                events_dispatcher.rqDeactivateLazyChannel(self._name)
            else:
                events_dispatcher.rqExitFromLazyChannel(self._name)
