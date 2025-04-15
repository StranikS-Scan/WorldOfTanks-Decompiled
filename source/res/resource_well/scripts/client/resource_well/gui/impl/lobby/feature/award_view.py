# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/impl/lobby/feature/award_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import selectVehicleInHangar, showHangar
from helpers import dependency
from resource_well.gui.impl.gen.view_models.views.lobby.award_view_model import AwardViewModel
from resource_well.gui.impl.lobby.feature.sounds import RESOURCE_WELL_SOUND_SPACE
from resource_well.gui.impl.lobby.feature.tooltips.serial_number_tooltip import SerialNumberTooltip
from resource_well.gui.shared.event_dispatcher import showResourceWellProgressionWindow
from skeletons.gui.resource_well import IResourceWellController

class AwardView(ViewImpl):
    _COMMON_SOUND_SPACE = RESOURCE_WELL_SOUND_SPACE
    __resourceWell = dependency.descriptor(IResourceWellController)

    def __init__(self, rewardID, *args, **kwargs):
        settings = ViewSettings(R.views.resource_well.lobby.feature.AwardView(), model=AwardViewModel(), args=args, kwargs=kwargs)
        super(AwardView, self).__init__(settings)
        self.__vehicle = self.__resourceWell.getRewardVehicle(rewardID)
        self.__rewardConfig = self.__resourceWell.config.getRewardConfig(rewardID)

    @property
    def viewModel(self):
        return super(AwardView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return SerialNumberTooltip() if contentID == R.views.resource_well.lobby.feature.tooltips.SerialNumberTooltip() else super(AwardView, self).createToolTipContent(event, contentID)

    def _onLoading(self, serialNumber, *args, **kwargs):
        super(AwardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            fillVehicleInfo(tx.vehicleInfo, self.__vehicle)
            tx.setRewardIndex(self.__rewardConfig.order)
            tx.setPersonalNumber(serialNumber if serialNumber is not None else '')
        return

    def _finalize(self):
        self.soundManager.playSound(backport.sound(R.sounds.gui_hangar_award_screen_stop()))
        self.__vehicle = None
        self.__rewardConfig = None
        super(AwardView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.showInHangar, self.__showVehicle), (self.viewModel.close, self.__close))

    def __close(self):
        self.destroyWindow()
        if self.__resourceWell.isActive():
            showResourceWellProgressionWindow()
        else:
            showHangar()

    def __showVehicle(self):
        selectVehicleInHangar(self.__vehicle.intCD)
        self.destroyWindow()


class AwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewardID, serialNumber):
        super(AwardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=AwardView(rewardID, serialNumber))
