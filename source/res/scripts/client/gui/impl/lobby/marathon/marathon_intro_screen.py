# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/marathon/marathon_intro_screen.py
import typing
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen.view_models.views.lobby.marathon.marathon_intro_screen_model import MarathonIntroScreenModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.events_dispatcher import showMissionsMarathon
from helpers import dependency
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    import Vehicle

class MarathonIntroView(ViewImpl):

    def __init__(self, layoutId, vehicleID, *args, **kwargs):
        settings = ViewSettings(layoutId)
        settings.model = MarathonIntroScreenModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__vehicleID = vehicleID
        super(MarathonIntroView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MarathonIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        self.__update()
        self.viewModel.onGoToMarathonClick += self.__openMarathon

    def _finalize(self):
        super(MarathonIntroView, self)._finalize()
        self.viewModel.onGoToMarathonClick -= self.__openMarathon

    def __update(self):
        with self.viewModel.transaction() as model:
            if self.__vehicleID != 0:
                itemsCache = dependency.instance(IItemsCache)
                vehicle = itemsCache.items.getItemByCD(self.__vehicleID)
                model.setVehicleIcon(vehicle.typeBigIconResource())
                model.setVehicleLevel(vehicle.level)
                model.setVehicleName(vehicle.userName)

    def __openMarathon(self):
        showMissionsMarathon()
        self.destroyWindow()


class MarathonIntroWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, layoutId, vehicleID, *args, **kwargs):
        super(MarathonIntroWindow, self).__init__(content=MarathonIntroView(layoutId, vehicleID, *args, **kwargs), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW)


def showMarathonIntroWindow(introScreenLayoutId, vehicleID):
    if MarathonIntroWindow.getInstances():
        return
    window = MarathonIntroWindow(introScreenLayoutId, vehicleID)
    window.load()
