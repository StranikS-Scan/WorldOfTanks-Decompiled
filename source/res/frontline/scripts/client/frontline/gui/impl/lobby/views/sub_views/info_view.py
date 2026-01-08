# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/sub_views/info_view.py
import typing
from frontline.gui.frontline_skill_packer import packBaseSkills
from frontline.gui.impl.gen.view_models.views.lobby.views.info_view_model import InfoViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.rank_item_model import RankItemModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_category_base_model import SkillCategoryBaseModel, SkillCategoryType
from frontline.gui.params import getArmorDamageFactors
from constants import PLAYER_RANK
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from frameworks.wulf.view.array import fillIntsArray
from gui.impl.gen import R
from gui.impl.pub import ViewImpl, WindowImpl
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController, IBattlePassController
from skeletons.gui.shared import IItemsCache
from supply_shared import Supply
if typing.TYPE_CHECKING:
    from frameworks.wulf import Array

class InfoView(ViewImpl):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID=R.views.frontline.lobby.InfoView(), showFullScreen=False, **kwargs):
        self._isFullScreen = showFullScreen
        settings = ViewSettings(layoutID, ViewFlags.VIEW if showFullScreen else ViewFlags.LOBBY_TOP_SUB_VIEW, InfoViewModel())
        settings.kwargs = kwargs
        super(InfoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(InfoView, self).getViewModel()

    def _getEvents(self):
        return ((self.__epicController.onUpdated, self._fillModel), (self.viewModel.onClose, self.__onViewClose)) if self._isFullScreen else ((self.__epicController.onUpdated, self._fillModel),)

    def _onLoading(self, *args, **kwargs):
        super(InfoView, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self, _=None):
        with self.viewModel.transaction() as vm:
            self.__updateVehLevels(vm.getValidVehicleLevels())
            vm.setUnlockableInBattleVehicleLevel(self.__epicController.getUnlockableInBattleVehLevels()[0] if self.__epicController.isUnlockVehiclesInBattleEnabled() else 0)
            vm.setIsFullScreen(self._isFullScreen)
            vm.setIsBattlePassAvailable(self.__epicController.isBattlePassDataEnabled())
            self.__updateDestructiblesArmor(vm)
            self.__updateSeasonTimestamps(vm)
            self.__updateSkillsCategories(vm)
            self.__updateRanks(vm)
            self.__updateWinLoseTable(vm)
            self.__updateSupplyParams(vm)

    def __updateVehLevels(self, vehilceLevels):
        vehilceLevels.clear()
        validVehicleLevels = self.__epicController.getValidVehicleLevels()
        validVehicleLevels.sort()
        for level in validVehicleLevels:
            vehilceLevels.addNumber(level)

        vehilceLevels.invalidate()

    def __updateDestructiblesArmor(self, vm):
        armors = self.__epicController.getDestructiblesArmor()
        vm.setSideDestructiblesArmor(armors[2])
        vm.setBackDestructiblesArmor(armors[3])
        vm.setVentilationDestructiblesArmor(armors[4])
        vm.setDoorDestructiblesArmor(armors[5])

    def __updateSeasonTimestamps(self, vm):
        if hasattr(vm, 'setStartTimestamp') and hasattr(vm, 'setEndTimestamp'):
            start, end = self.__epicController.getSeasonTimeRange()
            vm.setStartTimestamp(start)
            vm.setEndTimestamp(end)

    def __updateSkillsCategories(self, vm):
        categories = vm.getSkillsCategories()
        categories.clear()
        for category, skillsData in self.__epicController.getOrderedSkillTree():
            categoryModel = SkillCategoryBaseModel()
            categoryModel.setType(SkillCategoryType(category))
            packBaseSkills(categoryModel.getSkills(), skillsData)
            categories.addViewModel(categoryModel)

    def __updateRanks(self, vm):
        ranksInfo = self.__epicController.getPlayerRanksWithBonusInfo()
        ranks = vm.getRanksWithPoints()
        ranks.clear()
        for lvl, (points, xpBonus, _) in sorted(ranksInfo.iteritems()):
            item = RankItemModel()
            item.setRankName(PLAYER_RANK.NAMES[lvl])
            rankItemPoints = item.getRankPoints()
            rankItemPoints.addNumber(points)
            rankItemPoints.addNumber(xpBonus)
            ranks.addViewModel(item)

    def __updateWinLoseTable(self, vm):
        winPoints, losePoints = self.__battlePassController.getWinLosePointsList()
        fillIntsArray(winPoints, vm.getWinTablePoints())
        fillIntsArray(losePoints, vm.getLoseTablePoints())

    def __updateSupplyParams(self, vm):
        supplyParams = self.__epicController.getSupplyParams()
        vm.setMortarRespawnTime(supplyParams[Supply.MORTAR].get('resurrectTime', 0))
        airshipParams = supplyParams[Supply.AIRSHIP]
        vehicle = self.__itemsCache.items.getItemByCD(airshipParams['intCD'])
        hullDamageFactor, turretDamageFactor = getArmorDamageFactors(vehicle.descriptor)
        vm.setAirshipHullDamageFactor(hullDamageFactor)
        vm.setAirshipTurretDamageFactor(turretDamageFactor)
        vm.setAirshipRespawnTime(airshipParams.get('cooldownTime', 0))
        vm.setAirshipCaptureDuration(airshipParams.get('captureTime', 0))
        vm.setPillboxRespawnTime(supplyParams[Supply.PILLBOX].get('resurrectTime', 0))
        vm.setFlamerRespawnTime(supplyParams[Supply.FLAMER].get('resurrectTime', 0))

    def __onViewClose(self):
        self.destroyWindow()


class InfoViewWindow(WindowImpl):

    def __init__(self, parent=None):
        super(InfoViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=InfoView(showFullScreen=True), parent=parent)
