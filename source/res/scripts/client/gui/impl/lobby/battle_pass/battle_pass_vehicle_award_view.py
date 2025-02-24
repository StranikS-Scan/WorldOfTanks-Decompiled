# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_vehicle_award_view.py
import typing
import SoundGroups
from frameworks.wulf import ViewSettings, ViewStatus
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_vehicle_award_view_model import BattlePassVehicleAwardViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.Scaleform.managers import GameInputMgr

class BattlePassVehicleAwardView(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = BattlePassVehicleAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BattlePassVehicleAwardView, self).__init__(settings)
        self.inputManager.addEscapeListener(self.__onClose)

    @property
    def viewModel(self):
        return super(BattlePassVehicleAwardView, self).getViewModel()

    @property
    def inputManager(self):
        app = self.__appLoader.getApp()
        return app.gameInputManager

    def _initialize(self, data, *args, **kwargs):
        super(BattlePassVehicleAwardView, self)._initialize(*args, **kwargs)
        self.viewModel.onClose += self.__onClose
        self.viewModel.setVehicleLevelPoints(data.get('vehiclePoints', 0))
        self.viewModel.setBattlePassPointsAward(data.get('bonusPoints', 0))
        vehicle = self.__itemsCache.items.getItemByCD(data.get('vehTypeCompDescr', 0))
        self.viewModel.setIsPremiumVehicle(vehicle.isPremium)
        self.viewModel.setIsEliteVehicle(vehicle.isElite)
        self.viewModel.setVehicleLevel(vehicle.level)
        self.viewModel.setVehicleName(vehicle.userName)
        self.viewModel.setVehicleNation(vehicle.nationName)
        self.viewModel.setVehicleType(vehicle.type)
        techName = vehicle.name.split(':')
        self.viewModel.setTechName(techName[1])
        chapterID = self.__battlePass.getCurrentChapterID()
        self.viewModel.setChapterID(chapterID)
        isBattlePassPurchased = self.__battlePass.isBought(chapterID=chapterID)
        self.viewModel.setIsBattlePassPurchased(isBattlePassPurchased)
        self.viewModel.setLimitRefreshTimeLeft(self.__battlePass.getTimeToLimitReset())
        switchHangarOverlaySoundFilter(on=True)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.TANK_POINTS_CAP)

    def __onClose(self):
        if self.viewStatus == ViewStatus.LOADED:
            self.destroyWindow()

    def _finalize(self):
        self.viewModel.onClose -= self.__onClose
        self.inputManager.removeEscapeListener(self.__onClose)
        super(BattlePassVehicleAwardView, self)._finalize()
        switchHangarOverlaySoundFilter(on=False)


class BattlePassVehicleAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, data):
        super(BattlePassVehicleAwardWindow, self).__init__(content=BattlePassVehicleAwardView(R.views.lobby.battle_pass.BattlePassVehicleAwardView(), data=data))
