# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_intro_view.py
from account_helpers.AccountSettings import AccountSettings, PersonalMissions
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_intro_view_model import PersonalMissionsIntroViewModel
from gui.impl.lobby.personal_missions.personal_missions_window_events import showPersonalMissionsWebbrg, showIntroVideoView, PM3_INFO_PAGE
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.events_dispatcher import showPersonalMissionsOperationsMap
from personal_missions import PM_BRANCH
from gui.server_events.pm3_constants import SOUNDS

class PersonalMissionsIntroView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PersonalMissionsIntroViewModel()
        super(PersonalMissionsIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalMissionsIntroView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        super(PersonalMissionsIntroView, self)._onLoaded(*args, **kwargs)
        self.__playScreenSound()
        AccountSettings.setPersonalMissions(PersonalMissions.INTRO_SEEN, True)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onCloseView),
         (self.viewModel.onContinue, self.__onCloseView),
         (self.viewModel.onVideoOpen, self.__onVideoOpen),
         (self.viewModel.onMoreInfo, self.__onMoreInfo))

    def __onCloseView(self):
        self.destroyWindow()
        showPersonalMissionsOperationsMap(PM_BRANCH.PERSONAL_MISSION_3)

    def __onVideoOpen(self):
        showIntroVideoView()

    def __onMoreInfo(self):
        self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_ON)
        showPersonalMissionsWebbrg(PM3_INFO_PAGE, parent=self.getParentWindow(), returnClb=self.__onInfoClose)

    def __onInfoClose(self, **kwargs):
        self.soundManager.setState(SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_GROUP, SOUNDS.STATE_OVERLAY_HANGAR_GENERAL_OFF)

    def __playScreenSound(self):
        self.soundManager.setState(SOUNDS.STATE_PLACE, SOUNDS.STATE_PLACE_MISSIONS)
        self.soundManager.playSound(SOUNDS.AMBIENT)


class PersonalMissionsIntroViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(PersonalMissionsIntroViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PersonalMissionsIntroView(R.views.lobby.personal_missions.PersonalMissionsIntroView()), parent=parent)
