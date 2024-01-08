# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/views/sub_views/info_view.py
from constants import PLAYER_RANK
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from frontline.gui.frontline_skill_packer import packBaseSkills
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_category_base_model import SkillCategoryBaseModel, SkillCategoryType
from gui.impl.pub import ViewImpl, WindowImpl
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from frontline.gui.impl.gen.view_models.views.lobby.views.info_view_model import InfoViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.rank_item_model import RankItemModel

class InfoView(ViewImpl):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, layoutID=R.views.frontline.lobby.InfoView(), showFullScreen=False, autoscrollSection='', **kwargs):
        self._autoscrollSection = autoscrollSection
        settings = ViewSettings(layoutID, ViewFlags.VIEW if showFullScreen else ViewFlags.LOBBY_TOP_SUB_VIEW, InfoViewModel())
        settings.kwargs = kwargs
        super(InfoView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(InfoView, self).getViewModel()

    def _getEvents(self):
        return ((self.__epicController.onUpdated, self._fillModel), (self.viewModel.onClose, self.__onViewClose))

    def _onLoading(self, *args, **kwargs):
        super(InfoView, self)._onLoading(*args, **kwargs)
        self._fillModel()

    def _fillModel(self, _=None):
        with self.viewModel.transaction() as vm:
            vm.setAutoscrollSection(self._autoscrollSection)
            vm.setIsBattlePassAvailable(self.__epicController.isBattlePassDataEnabled())
            vm.setIsNinthLevelEnabled(self.__epicController.isUnlockVehiclesInBattleEnabled())
            vm.setIsRandomReservesModeEnabled(self.__epicController.isRandomReservesModeEnabled())
            if hasattr(vm, 'setStartTimestamp') and hasattr(vm, 'setEndTimestamp'):
                startTimestamp, endTimestamp = self.__epicController.getSeasonTimeRange()
                vm.setStartTimestamp(startTimestamp)
                vm.setEndTimestamp(endTimestamp)
            categories = vm.getSkillsCategories()
            categories.clear()
            for category, skillsData in self.__epicController.getGroupedSkills():
                categoryModel = SkillCategoryBaseModel()
                categoryModel.setType(SkillCategoryType(category))
                skills = categoryModel.getSkills()
                packBaseSkills(skills, skillsData)
                categories.addViewModel(categoryModel)

            ranksInfo = self.__epicController.getPlayerRanksWithBonusInfo()
            ranks = vm.getRanksWithPoints()
            ranks.clear()
            for rankLvl, (points, xpBonus, effectivenessBonus) in sorted(ranksInfo.iteritems()):
                rankItem = RankItemModel()
                rankItem.setRankName(PLAYER_RANK.NAMES[rankLvl])
                rankItemPoints = rankItem.getRankPoints()
                rankItemPoints.addNumber(points)
                rankItemPoints.addNumber(xpBonus)
                rankItemPoints.addReal(effectivenessBonus)
                ranks.addViewModel(rankItem)

    def __onViewClose(self):
        self.destroyWindow()


class InfoViewWindow(WindowImpl):

    def __init__(self, parent=None, autoscrollSection=''):
        super(InfoViewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=InfoView(autoscrollSection=autoscrollSection, showFullScreen=True), parent=parent)
