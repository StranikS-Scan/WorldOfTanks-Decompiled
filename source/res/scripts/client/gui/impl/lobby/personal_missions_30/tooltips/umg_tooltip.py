# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/tooltips/umg_tooltip.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
import nations
from CurrentVehicle import g_currentVehicle
from constants import ROLE_TYPE_TO_COMMON_ROLE
from frameworks.wulf import ViewSettings
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import getBonusesWithModifyTokens
from helpers import dependency
from helpers.i18n import makeString
from future.utils import viewvalues
from personal_missions import PM_BRANCH, PM_BRANCH_TO_FREE_TOKEN_NAME
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.PERSONAL_MISSIONS_30 import PERSONAL_MISSIONS_30
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.tooltips.umg_tooltip_model import UmgTooltipModel, MissionConditionModel
from gui.impl.lobby.personal_missions_30.bonus_packers import getBonusPacker, packMissionsBonusModelAndTooltipData
from gui.impl.lobby.personal_missions_30.views_helpers import getMissionConfigData
from gui.impl.pub import ViewImpl
from gui.server_events.personal_progress.formatters import PMTooltipConditionsFormatters
from skeletons.gui.server_events import IEventsCache
if TYPE_CHECKING:
    from typing import Optional
    from gui.server_events.event_items import PersonalMission
    from gui.server_events.bonuses import SimpleBonus

class UmgPersonalMissionsTooltip(ViewImpl):
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, campaignId, missionId):
        settings = ViewSettings(R.views.mono.personal_missions_30.tooltips.umg_tooltip(), model=UmgTooltipModel())
        self._branchID = campaignId
        self._missionId = missionId
        super(UmgPersonalMissionsTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(UmgPersonalMissionsTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(UmgPersonalMissionsTooltip, self)._onLoading()
        self._fillViewModel()

    def _fillViewModel(self):
        with self.viewModel.transaction() as vm:
            personalMissionsCache = self.eventsCache.getPersonalMissions()
            vm.setCampaignId(PM_BRANCH.PM_CAMPAIGNS_IDS[self._branchID])
            if self._missionId == 0:
                quests = personalMissionsCache.getSelectedQuestsForBranch(self._branchID)
                randomQuest = next(iter(viewvalues(quests)), None)
                operationId = randomQuest.getOperationID() if randomQuest else 0
                vm.setOperationId(operationId)
                self._fillCompleteState(vm)
                return
            quests = personalMissionsCache.getQuestsForBranch(self._branchID)
            quest = quests.get(self._missionId, None)
            if quest:
                vm.setOperationId(quest.getOperationID())
                vm.setMissionId(self._missionId)
                operation = self._getOperation(quest)
                vm.setIcon(self._getMissionIcon(operation, quest))
                vm.setMissionState(self._getMissionState(quest))
                vm.setTitle(quest.getShortUserName())
                totalVehiclesForQuest = 1
                completedInVehicles = 0
                if PM_BRANCH.TYPE_TO_NAME[self._branchID] in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES:
                    questConfig = getMissionConfigData(quest)
                    totalVehiclesForQuest = questConfig.maxProgressValue
                    curVehiclesForQuest = len(quest.getConditionsProgress().get('battlesUniqueVehicles', {}))
                    completedInVehicles = totalVehiclesForQuest if quest.isCompleted() else curVehiclesForQuest
                vm.setTotalVehiclesForQuest(totalVehiclesForQuest)
                vm.setCompletedInVehicles(completedInVehicles)
                self._fillConditions(vm, quest)
                self._fillRewards(vm, quest)
        return

    def _fillCompleteState(self, vm):
        if not g_currentVehicle.isPresent():
            return
        vehType = g_currentVehicle.item.descriptor.type
        classifierAttr = ''
        title = ''
        if self._branchID == PM_BRANCH.REGULAR:
            classifierAttr = vehType.classTag
            title = makeString(PERSONAL_MISSIONS.chainNameByVehicleType(classifierAttr))
        elif self._branchID == PM_BRANCH.PERSONAL_MISSION_2:
            allianceId = nations.NATION_TO_ALLIANCE_IDS_MAP[vehType.id[0]]
            classifierAttr = nations.ALLIANCES_TAGS_ORDER[allianceId]
            title = makeString(PERSONAL_MISSIONS.getAllianceName(allianceId))
        elif self._branchID == PM_BRANCH.PERSONAL_MISSION_3:
            classifierAttr = ROLE_TYPE_TO_COMMON_ROLE[vehType.role]
            title = makeString(PERSONAL_MISSIONS_30.chainNameByRole(classifierAttr))
        if not classifierAttr:
            return
        vm.setTitle(title)
        vm.setMissionState(UmgTooltipModel.STATE_COMPLETE)
        vm.setIcon(R.images.gui.maps.icons.personal_missions_30.tooltips.umg.icon.dyn(classifierAttr.replace('-', '_'))())

    def _getOperation(self, quest):
        personalMissions = self.eventsCache.getPersonalMissions()
        return personalMissions.getOperationsForBranch(quest.getQuestBranch())[quest.getOperationID()]

    @staticmethod
    def _fillConditions(vm, quest):
        isMain = None
        if not quest.isMainCompleted():
            isMain = True
        formatter = PMTooltipConditionsFormatters()
        tasks = formatter.format(quest, isMain, isForNewTooltip=True)
        andConditions = vm.getAndConditions()
        orConditions = vm.getOrConditions()
        for task in tasks:
            condition = MissionConditionModel()
            condition.setIcon(task.icon)
            condition.setText(task.title)
            if task.isInOrGroup:
                orConditions.addViewModel(condition)
            andConditions.addViewModel(condition)

        return

    def _fillRewards(self, vm, quest):
        rewards = vm.getRewards()
        rewards.clear()
        packer = getBonusPacker()
        if PM_BRANCH.TYPE_TO_NAME[self._branchID] in PM_BRANCH.WITH_AWARD_LIST_BRANCHES:
            bonuses = quest.getBonuses(isMain=not quest.isMainCompleted())
            self._packPM1n2(bonuses, packer, rewards, quest)
        elif PM_BRANCH.TYPE_TO_NAME[self._branchID] in PM_BRANCH.WITHOUT_AWARD_LIST_BRANCHES:
            bonuses = quest.getBonuses()
            packMissionsBonusModelAndTooltipData(bonuses, packer, rewards)
        rewards.invalidate()

    def _packPM1n2(self, bonuses, packer, rewards, quest):
        bonusIdx = 0
        pawnedTokensCount = quest.getPawnCost() if quest.areTokensPawned() else 0
        freeTokenName = PM_BRANCH_TO_FREE_TOKEN_NAME.get(quest.getQuestBranch())
        ctx = {'branchID': self._branchID,
         'questID': self._missionId}
        bonuses = getBonusesWithModifyTokens(bonuses, freeTokenName, pawnedTokensCount, True, additionalCtx=ctx)
        for bonus in bonuses:
            if not bonus.isShowInGUI():
                continue
            bonusList = packer.pack(bonus)
            for packedBonus in bonusList:
                if isinstance(packedBonus, list):
                    packedBonus[0].setIndex(bonusIdx)
                    rewards.addViewModel(packedBonus[0])
                else:
                    packedBonus.setIndex(bonusIdx)
                    rewards.addViewModel(packedBonus)
                bonusIdx += 1

    def _getMissionState(self, quest):
        if quest.isMainCompleted():
            return UmgTooltipModel.STATE_IMPROVE
        if self._branchID == PM_BRANCH.PERSONAL_MISSION_3:
            vehCmpDescr = g_currentVehicle.item.descriptor.type.compactDescr
            if quest.isAmongUsedQuestVehicle(vehCmpDescr):
                return UmgTooltipModel.STATE_WRONG_VEHICLE
        return UmgTooltipModel.STATE_ACTIVE

    @staticmethod
    def _getMissionIcon(operation, quest):
        classifier = operation.getChainClassifier(quest.getChainID()).classificationAttr
        return R.images.gui.maps.icons.personal_missions_30.tooltips.umg.icon.dyn(classifier.replace('-', '_'))()
