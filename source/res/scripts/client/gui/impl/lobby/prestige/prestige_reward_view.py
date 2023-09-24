# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/prestige/prestige_reward_view.py
import typing
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.prestige.views.prestige_reward_view_model import PrestigeRewardViewModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.prestige.prestige_helpers import fillPrestigeEmblemModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class PrestigeRewardView(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PrestigeRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(PrestigeRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PrestigeRewardView, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.destroyWindow),)

    def _onLoading(self, vehIntCD, level):
        super(PrestigeRewardView, self)._onLoading()
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.gui_reward_screen_general()))
        vehicle = self.__itemsCache.items.getItemByCD(vehIntCD)
        fillVehicleModel(self.viewModel.vehicle, vehicle)
        fillPrestigeEmblemModel(self.viewModel.vehicle.emblem, level, vehIntCD)


class PrestigeRewardViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, vehIntCD, level, parent=None):
        super(PrestigeRewardViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PrestigeRewardView(R.views.lobby.prestige.views.PrestigeRewardView(), vehIntCD, level), parent=parent)
