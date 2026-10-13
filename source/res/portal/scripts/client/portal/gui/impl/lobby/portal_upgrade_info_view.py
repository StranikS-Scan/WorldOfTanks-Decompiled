# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/portal_upgrade_info_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from portal.gui.impl.gen.view_models.views.lobby.portal_upgrade_info_view_model import PortalUpgradeInfoViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from portal.sounds.sound_constants import PORTAL_UPGRADE_INFO_SOUND_SPACE
from portal_account_settings import setAboutImprovementsViewed

class PortalUpgradeInfoView(ViewImpl):
    __slots__ = ()
    _COMMON_SOUND_SPACE = PORTAL_UPGRADE_INFO_SOUND_SPACE

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PortalUpgradeInfoViewModel()
        super(PortalUpgradeInfoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PortalUpgradeInfoView, self).getViewModel()

    def _onLoaded(self, *args, **kwargs):
        setAboutImprovementsViewed(True)

    def __onClose(self):
        self.destroyWindow()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)


class PortalUpgradeInfoViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(PortalUpgradeInfoViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PortalUpgradeInfoView(R.views.portal.lobby.PortalUpgradeInfoView()), parent=parent)
