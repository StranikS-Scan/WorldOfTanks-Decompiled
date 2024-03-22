# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/personal_case/service_record_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.personal_case.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.service_record_view_model import ServiceRecordViewModel
from gui.impl.lobby.crew.personal_case import IPersonalTab
from gui.impl.lobby.crew.personal_case.base_personal_case_view import BasePersonalCaseView
from gui.impl.lobby.crew.tankman_info import TankmanInfo
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.dossier.achievements.abstract import isRareAchievement
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from uilogging.crew.logging_constants import CrewViewKeys

class ServiceRecordView(IPersonalTab, BasePersonalCaseView):
    __slots__ = ('tankmanID', '__dossier')
    TITLE = backport.text(R.strings.crew.tankmanContainer.tab.serviceRecord())
    _UI_LOGGING_KEY = CrewViewKeys.SERVICE_RECORD
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID=R.views.lobby.crew.personal_case.ServiceRecordView(), **kwargs):
        self.tankmanID = kwargs.get('tankmanID')
        self.__dossier = self.itemsCache.items.getTankmanDossier(self.tankmanID)
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, ServiceRecordViewModel())
        super(ServiceRecordView, self).__init__(settings, **kwargs)

    @property
    def viewModel(self):
        return super(ServiceRecordView, self).getViewModel()

    @property
    def tankmanInfo(self):
        return self.getParentView().getChildView(TankmanInfo.LAYOUT_DYN_ACCESSOR())

    def onChangeTankman(self, tankmanID):
        self.tankmanID = tankmanID
        self.__dossier = self.itemsCache.items.getTankmanDossier(self.tankmanID)
        self.tankmanInfo.setTankmanId(tankmanID)
        self.tankmanInfo.setParentViewKey(CrewViewKeys.SERVICE_RECORD)
        self.__fillModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.ACHIEVEMENT:
                return createBackportTooltipContent(specialAlias=TOOLTIPS_CONSTANTS.ACHIEVEMENT, specialArgs=(self.__dossier.getDossierType(),
                 dumpDossier(self.__dossier),
                 event.getArgument('block'),
                 event.getArgument('name'),
                 event.getArgument('isRare')))
        return super(ServiceRecordView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(ServiceRecordView, self)._onLoading(*args, **kwargs)
        if not self.tankmanInfo:
            self.getParentView().setChildView(TankmanInfo.LAYOUT_DYN_ACCESSOR(), TankmanInfo(self.tankmanID, parentViewKey=CrewViewKeys.SERVICE_RECORD))
        self.__fillModel()

    def _getEvents(self):
        return ((self.itemsCache.onSyncCompleted, self.__onCacheResync),)

    def __fillModel(self):
        tankman = self.itemsCache.items.getTankman(self.tankmanID)
        with self.viewModel.transaction() as vm:
            vm.setIsTankmanInVehicle(tankman.vehicleDescr is not None)
            vm.setRankName(tankman.rankUserName)
            vm.setRankIcon(tankman.extensionLessIconRank)
            achievementsListVM = vm.getAchievementsList()
            achievementsListVM.clear()
            if self.__dossier:
                vm.setBattlesCount(self.__dossier.getBattlesCount())
                vm.setAverageXP(self.__dossier.getAvgXP())
                achieves = self.__dossier.getTotalStats().getAchievements(isInDossier=True)
                for _, section in enumerate(achieves):
                    for achievement in section:
                        achievementVM = AchievementModel()
                        achievementVM.setName(achievement.getName())
                        achievementVM.setAmount(achievement.getValue())
                        achievementVM.setBlock(achievement.getBlock())
                        achievementVM.setIsRare(isRareAchievement(achievement))
                        achievementsListVM.addViewModel(achievementVM)

            achievementsListVM.invalidate()
        return

    def __onCacheResync(self, _, diff):
        if diff is not None and GUI_ITEM_TYPE.TANKMAN in diff and self.tankmanID in diff[GUI_ITEM_TYPE.TANKMAN] and self.itemsCache.items.getTankman(self.tankmanID):
            self.__dossier = self.itemsCache.items.getTankmanDossier(self.tankmanID)
            self.__fillModel()
        return
