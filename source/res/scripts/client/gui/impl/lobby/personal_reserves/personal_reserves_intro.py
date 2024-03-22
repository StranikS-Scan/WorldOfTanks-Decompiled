# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_reserves/personal_reserves_intro.py
import typing
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_reserves.reserves_intro_view_model import ReservesIntroViewModel
from gui.impl.lobby.personal_reserves.reserves_constants import PERSONAL_RESERVES_SOUND_SPACE
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import showPersonalReservesInfomationScreen
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from typing import Dict, Any

class PersonalReservesIntro(ViewImpl, EventSystemEntity):
    __slots__ = ()
    _COMMON_SOUND_SPACE = PERSONAL_RESERVES_SOUND_SPACE
    _uiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID, ctx=None):
        settings = ViewSettings(layoutID)
        settings.model = ReservesIntroViewModel()
        super(PersonalReservesIntro, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalReservesIntro, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(PersonalReservesIntro, self)._initialize()
        self.viewModel.onClose += self.close
        self.viewModel.onDetailsClicked += self._onDetailsClicked

    def _finalize(self):
        self.viewModel.onClose -= self.close
        self.viewModel.onDetailsClicked -= self._onDetailsClicked
        super(PersonalReservesIntro, self)._finalize()

    def close(self):
        self.destroyWindow()

    def _onDetailsClicked(self):
        showPersonalReservesInfomationScreen()


class PersonalReservesIntroWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, ctx=None):
        super(PersonalReservesIntroWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PersonalReservesIntro(R.views.lobby.personal_reserves.ReservesIntroView(), ctx=ctx))
