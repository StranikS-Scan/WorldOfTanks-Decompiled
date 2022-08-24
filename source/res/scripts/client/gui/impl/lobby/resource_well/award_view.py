# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/resource_well/award_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.resource_well.award_view_model import AwardViewModel
from gui.impl.lobby.resource_well.tooltips.serial_number_tooltip import SerialNumberTooltip
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.resource_well.sounds import RESOURCE_WELL_SOUND_SPACE
from gui.shared.event_dispatcher import selectVehicleInHangar, showResourceWellProgressionWindow, showHangar
from helpers import dependency
from skeletons.gui.game_control import IResourceWellController
from tutorial.control.game_vars import getVehicleByIntCD

class AwardView(ViewImpl):
    __slots__ = ('__vehicle',)
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.resource_well.AwardView())
        settings.model = AwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AwardView, self).__init__(settings)
        self.__vehicle = getVehicleByIntCD(self.__resourceWell.getRewardVehicle())

    @property
    def viewModel(self):
        return super(AwardView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return SerialNumberTooltip(parentLayout=self.layoutID) if contentID == R.views.lobby.resource_well.tooltips.SerialNumberTooltip() else super(AwardView, self).createToolTipContent(event, contentID)

    def _onLoading(self, serialNumber, *args, **kwargs):
        super(AwardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            fillVehicleInfo(model.vehicleInfo, self.__vehicle)
            model.setPersonalNumber(serialNumber if serialNumber is not None else '')
        return

    def _finalize(self):
        self.soundManager.playSound(backport.sound(R.sounds.gui_hangar_award_screen_stop()))
        showResourceWellProgressionWindow()
        super(AwardView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.showInHangar, self.__showVehicle), (self.__resourceWell.onEventUpdated, self.__onEventStateUpdated))

    def __showVehicle(self):
        selectVehicleInHangar(self.__vehicle.intCD)
        self.destroyWindow()

    def __onEventStateUpdated(self):
        if not self.__resourceWell.isActive():
            self.destroyWindow()
            showHangar()


class AwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, serialNumber):
        super(AwardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=AwardView(serialNumber=serialNumber))
