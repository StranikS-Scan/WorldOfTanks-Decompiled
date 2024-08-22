# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_vehicle_award_view.py
import SoundGroups
from frameworks.wulf import ViewSettings
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_vehicle_award_view_model import BattlePassVehicleAwardViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache

class BattlePassVehicleAwardView(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = BattlePassVehicleAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BattlePassVehicleAwardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassVehicleAwardView, self).getViewModel()

    def _onLoading(self, data, *args, **kwargs):
        super(BattlePassVehicleAwardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setVehicleLevelPoints(data.get('vehiclePoints', 0))
            model.setBattlePassPointsAward(data.get('bonusPoints', 0))
            vehicle = self.__itemsCache.items.getItemByCD(data.get('vehTypeCompDescr', 0))
            fillVehicleInfo(model.vehicleInfo, vehicle)
            _, vehicleName = vehicle.name.split(':')
            model.setTechName(vehicleName)
            chapterID = self.__battlePass.getCurrentChapterID()
            model.setChapterID(chapterID)
            isBattlePassPurchased = self.__battlePass.isBought(chapterID=chapterID)
            model.setIsBattlePassPurchased(isBattlePassPurchased)
        switchHangarOverlaySoundFilter(on=True)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.TANK_POINTS_CAP)

    def _finalize(self):
        super(BattlePassVehicleAwardView, self)._finalize()
        switchHangarOverlaySoundFilter(on=False)


class BattlePassVehicleAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, data):
        super(BattlePassVehicleAwardWindow, self).__init__(content=BattlePassVehicleAwardView(R.views.lobby.battle_pass.BattlePassVehicleAwardView(), data=data))
