# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/lobby/portal_upgrade_reset_view.py
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from portal.gui.impl.gen.view_models.views.lobby.portal_upgrade_reset_view_model import PortalUpgradeResetViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.gen import R
from gui.shared.view_helpers.blur_manager import CachedBlur
from portal.skeletons.portal_event_controller import IPortalEventController
from helpers import dependency
from portal.sounds.sound_constants import PORTAL_UPGRADE_RESET_SOUND_SPACE

class PortalUpgradeResetView(ViewImpl):
    __slots__ = ('__blur',)
    __portalController = dependency.descriptor(IPortalEventController)
    _COMMON_SOUND_SPACE = PORTAL_UPGRADE_RESET_SOUND_SPACE

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PortalUpgradeResetViewModel()
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.VIEW)
        super(PortalUpgradeResetView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PortalUpgradeResetView, self).getViewModel()

    def _finalize(self):
        self.__blur.fini()
        super(PortalUpgradeResetView, self)._finalize()

    def __onClose(self):
        self.destroyWindow()

    def __onReset(self):
        self.__portalController.resetCurrentVehicleUpgrades()
        self.destroyWindow()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose), (self.viewModel.onReset, self.__onReset))


class PortalUpgradeResetViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(PortalUpgradeResetViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PortalUpgradeResetView(R.views.portal.lobby.PortalUpgradeResetView()), parent=parent)
