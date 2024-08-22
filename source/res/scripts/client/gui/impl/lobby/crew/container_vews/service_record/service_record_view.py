# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/container_vews/service_record/service_record_view.py
import typing
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl import backport
from gui.impl.backport.backport_tooltip import createBackportTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.crew.common.tooltip_constants import TooltipConstants
from gui.impl.gen.view_models.views.lobby.crew.personal_case.achievement_model import AchievementModel
from gui.impl.gen.view_models.views.lobby.crew.personal_case.service_record_view_model import ServiceRecordViewModel
from gui.impl.lobby.container_views.base.components import ContainerBase
from gui.impl.lobby.crew.container_vews.common.tankman_info_component import TankmanInfoComponent
from gui.impl.lobby.crew.container_vews.service_record.context import ServiceRecordViewContext
from gui.impl.lobby.crew.container_vews.service_record.controller import ServiceRecordInteractionController
from gui.impl.lobby.crew.personal_case import IPersonalTab
from gui.impl.lobby.crew.personal_case.base_personal_case_view import BasePersonalCaseView
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.dossier.achievements.abstract import isRareAchievement
from uilogging.crew.logging_constants import CrewViewKeys
if typing.TYPE_CHECKING:
    from typing import List, Type
    from gui.impl.lobby.container_views.base.controllers import InteractionController
    from gui.impl.lobby.container_views.base.components import ComponentBase

class ServiceRecordView(ContainerBase, IPersonalTab, BasePersonalCaseView):
    __slots__ = ('__viewKey',)
    TITLE = backport.text(R.strings.crew.tankmanContainer.tab.serviceRecord())
    _UI_LOGGING_KEY = CrewViewKeys.SERVICE_RECORD

    def __init__(self, layoutID=R.views.lobby.crew.personal_case.ServiceRecordView(), **kwargs):
        self.__viewKey = CrewViewKeys.SERVICE_RECORD
        settings = ViewSettings(layoutID, ViewFlags.LOBBY_TOP_SUB_VIEW, ServiceRecordViewModel())
        super(ServiceRecordView, self).__init__(settings, **kwargs)

    def _getComponents(self):
        return [TankmanInfoComponent(key='tankman_info', parent=self)]

    def _getContext(self, *args, **kwargs):
        return ServiceRecordViewContext(kwargs.get('tankmanID'))

    def _getInteractionControllerCls(self):
        return ServiceRecordInteractionController

    @property
    def viewModel(self):
        return super(ServiceRecordView, self).getViewModel()

    @property
    def viewKey(self):
        return self.__viewKey

    def onChangeTankman(self, tankmanID):
        if hasattr(self, 'interactionCtrl'):
            self.interactionCtrl.onChangeTankman(tankmanID)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == TooltipConstants.ACHIEVEMENT:
                return createBackportTooltipContent(specialAlias=TOOLTIPS_CONSTANTS.ACHIEVEMENT, specialArgs=(self.context.dossier.getDossierType(),
                 dumpDossier(self.context.dossier),
                 event.getArgument('block'),
                 event.getArgument('name'),
                 event.getArgument('isRare')))
        return super(ServiceRecordView, self).createToolTipContent(event, contentID)

    def _fillViewModel(self, vm):
        vm.setIsTankmanInVehicle(self.context.tankman.vehicleDescr is not None)
        vm.setRankName(self.context.tankman.rankUserName)
        vm.setRankIcon(self.context.tankman.extensionLessIconRank)
        achievementsListVM = vm.getAchievementsList()
        achievementsListVM.clear()
        if self.context.dossier:
            vm.setBattlesCount(self.context.dossier.getBattlesCount())
            vm.setAverageXP(self.context.dossier.getAvgXP())
            achieves = self.context.dossier.getTotalStats().getAchievements(isInDossier=True)
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
