# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_vehicle_award_view.py
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings
from gui.battle_pass.battle_pass_helpers import isCurrentBattlePassStateBase
from gui.battle_pass.sounds import BattlePassSounds
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_vehicle_award_view_model import BattlePassVehicleAwardViewModel
from gui.impl.pub import ViewImpl
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class BattlePassVehicleAwardView(ViewImpl):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, wsFlags=ViewFlags.OVERLAY_VIEW, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = wsFlags
        settings.model = BattlePassVehicleAwardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(BattlePassVehicleAwardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassVehicleAwardView, self).getViewModel()

    def _initialize(self, data, *args, **kwargs):
        super(BattlePassVehicleAwardView, self)._initialize(*args, **kwargs)
        self.viewModel.setVehicleLevelPoints(data.get('vehiclePoints', 0))
        self.viewModel.setBattlePassPointsAward(data.get('bonusPoints', 0))
        vehicle = self.__itemsCache.items.getItemByCD(data.get('vehTypeCompDescr', 0))
        self.viewModel.setIsPremiumVehicle(vehicle.isPremium)
        self.viewModel.setIsEliteVehicle(vehicle.isElite)
        self.viewModel.setVehicleLevel(vehicle.level)
        self.viewModel.setVehicleName(vehicle.userName)
        self.viewModel.setVehicleNation(vehicle.nationName)
        self.viewModel.setVehicleType(vehicle.type)
        self.viewModel.setIsPostProgression(not isCurrentBattlePassStateBase())
        techName = vehicle.name.split(':')
        self.viewModel.setTechName(techName[1])
        switchHangarOverlaySoundFilter(on=True)
        SoundGroups.g_instance.playSound2D(BattlePassSounds.TANK_POINTS_CAP)

    def _finalize(self):
        super(BattlePassVehicleAwardView, self)._finalize()
        switchHangarOverlaySoundFilter(on=False)
