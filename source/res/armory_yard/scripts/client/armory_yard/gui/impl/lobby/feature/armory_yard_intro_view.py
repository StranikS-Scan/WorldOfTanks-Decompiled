# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_intro_view.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ArmoryYard
from armory_yard.gui.window_events import showArmoryYardIntroVideo
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_intro_view_model import ArmoryYardIntroViewModel
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sound_constants import ARMORY_YARD_INTRO_SOUND_SPACE
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from items.vehicles import getVehicleClassFromVehicleType
from skeletons.gui.game_control import IArmoryYardController
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
_logger = logging.getLogger(__name__)

class ArmoryYardIntroView(ViewImpl):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    _COMMON_SOUND_SPACE = ARMORY_YARD_INTRO_SOUND_SPACE
    __slots__ = ('__closeCallback', '__loadedCallback')

    def __init__(self, layoutID, finalRewardVehicle, closeCallback=None, loadedCallback=None):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=ArmoryYardIntroViewModel(), args=(finalRewardVehicle,))
        super(ArmoryYardIntroView, self).__init__(settings)
        self.__closeCallback = closeCallback
        self.__loadedCallback = loadedCallback

    @property
    def viewModel(self):
        return super(ArmoryYardIntroView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardIntroView, self)._onLoading(*args, **kwargs)
        finalRewardVehicle = args[0]
        currentSeason = self.__armoryYardCtrl.serverSettings.getCurrentSeason()
        with self.viewModel.transaction() as vm:
            vm.setVehicleName(finalRewardVehicle.userName)
            vm.setVehicleType(getVehicleClassFromVehicleType(finalRewardVehicle.descriptor.type))
            vm.setVehicleLvl(finalRewardVehicle.level)
            vm.setIsElite(finalRewardVehicle.isElite)
            vm.setStartDate(currentSeason.getStartDate())
            vm.setEndDate(currentSeason.getEndDate())
            url = self.__armoryYardCtrl.serverSettings.getModeSettings().introVideoLink
            if url:
                vm.setHasIntroVideoLink(True)
                showArmoryYardIntroVideo(url, parent=self.getParentWindow())

    def _onLoaded(self, *args, **kwargs):
        if self.__loadedCallback:
            self.__loadedCallback()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),
         (self.viewModel.onContinue, self.__onContinue),
         (self.viewModel.onGoBack, self.__onGoBack),
         (self.__armoryYardCtrl.onUpdated, self.__onEventUpdated))

    def __onClose(self):
        self.__close()

    def __onContinue(self):
        self.__close()

    def __onGoBack(self):
        url = self.__armoryYardCtrl.serverSettings.getModeSettings().introVideoLink
        showArmoryYardIntroVideo(url, parent=self.getParentWindow())

    def __setIntroViewed(self):
        AccountSettings.setArmoryYard(ArmoryYard.ARMORY_YARD_LAST_INTRO_VIEWED, self.__armoryYardCtrl.serverSettings.getCurrentSeason().getSeasonID())

    def __onEventUpdated(self):
        if not self.__armoryYardCtrl.isEnabled():
            self.destroyWindow()

    def __close(self):
        self.destroyWindow()
        self.__setIntroViewed()
        if self.__closeCallback:
            self.__closeCallback()
        self.__closeCallback = None
        return


class ArmoryYardIntroWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, finalRewardVehicle, closeCallback=None, parent=None, loadedCallback=None):
        super(ArmoryYardIntroWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ArmoryYardIntroView(R.views.armory_yard.lobby.feature.ArmoryYardIntroView(), finalRewardVehicle, closeCallback=closeCallback, loadedCallback=loadedCallback), parent=parent, layer=WindowLayer.FULLSCREEN_WINDOW)
