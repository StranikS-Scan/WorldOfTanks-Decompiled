# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_error_lootbox_open_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_error_lootbox_open_view_model import WtEventErrorLootboxOpenViewModel
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow

class WtEventErrorLootboxOpenView(ViewImpl):
    __slots__ = ('__textsR',)

    def __init__(self, textsR):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WtEventErrorLootboxOpenView(), flags=ViewFlags.OVERLAY_VIEW, model=WtEventErrorLootboxOpenViewModel())
        self.__textsR = textsR
        super(WtEventErrorLootboxOpenView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WtEventErrorLootboxOpenView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(WtEventErrorLootboxOpenView, self)._onLoaded(*args, **kwargs)
        Waiting.hide('loadPage')

    def _onLoading(self, *args, **kwargs):
        super(WtEventErrorLootboxOpenView, self)._onLoading(*args, **kwargs)
        Waiting.show('loadPage')
        self.viewModel.setErrorTitle(backport.text(self.__textsR.title()))
        self.viewModel.setErrorText(backport.text(self.__textsR.text()))

    def _initialize(self):
        wt_event_sound.playLootBoxCrashEnter()
        self.viewModel.onClose += self._onClose
        super(WtEventErrorLootboxOpenView, self)._initialize()

    def _onClose(self):
        self.destroyWindow()

    def _finalize(self):
        wt_event_sound.playLootBoxCrashExit()
        self.viewModel.onClose -= self._onClose
        super(WtEventErrorLootboxOpenView, self)._finalize()


class WtEventErrorLootboxOpenViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, textsR, parent=None):
        super(WtEventErrorLootboxOpenViewWindow, self).__init__(WindowFlags.WINDOW, content=WtEventErrorLootboxOpenView(textsR), parent=parent, decorator=None)
        return
