# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/tooltips/personal_missions_last_operation_tooltip.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.personal_missions_last_operation_tooltip_model import PersonalMissionsLastOperationTooltipModel, LastMissionStatus
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.pm3_last_operation_tooltip_rewards_model import Pm3LastOperationTooltipRewardsModel
from gui.impl.pub import ViewImpl
from helpers import dependency, i18n
from personal_missions_constants import PM3_FINAL_REWARD_VIEW_ID
from skeletons.gui.game_control import IPersonalMissionsController
from skeletons.gui.shared import IItemsCache
from frameworks.wulf.view.array import fillViewModelsArray

class PersonalMissionsLastOperationTooltip(ViewImpl):
    __slots__ = ('__operationId',)
    __personalMissionsCtrl = dependency.descriptor(IPersonalMissionsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, layoutID, operationId):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PersonalMissionsLastOperationTooltipModel()
        self.__operationId = operationId
        super(PersonalMissionsLastOperationTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalMissionsLastOperationTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsLastOperationTooltip, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    def __updateModel(self, model):
        ctrl = self.__personalMissionsCtrl
        vehicles = ctrl.getVehiclesForChampionQuestPM3()
        bonuses = ctrl.getBadgesForChampionQuestPM3()
        model.setName(i18n.makeString('#personal_missions:operations/title%d' % PM3_FINAL_REWARD_VIEW_ID))
        countFinalQuests = len(ctrl.getFinalQuests())
        countFullCompletedFinalQuests = len(ctrl.getFullCompletedFinalQuests())
        model.setAll(countFinalQuests)
        model.setCompleted(countFullCompletedFinalQuests)
        model.setMissionStatus(LastMissionStatus.COMPLETED if countFullCompletedFinalQuests >= countFinalQuests else LastMissionStatus.ACTIVE)
        array = model.getRewards()
        bonusesList = self.__fillRewardsModels(vehicles, bonuses)
        fillViewModelsArray(bonusesList, array)
        array.invalidate()

    def __fillRewardsModels(self, vehicles, bonuses):
        bonusesList = []
        for vehicle in vehicles:
            nextModel = Pm3LastOperationTooltipRewardsModel()
            nextModel.setName(vehicle.userName)
            nextModel.setIcon(vehicle.iconBonus)
            bonusesList.append({'modelEl': nextModel,
             'weight': 1})

        for bonus in bonuses:
            achievements = bonus.getAchievements()
            if achievements is not None:
                for achievement in achievements:
                    nextModel = Pm3LastOperationTooltipRewardsModel()
                    nextModel.setIcon(achievement.getBigIcon())
                    bonusesList.append({'modelEl': nextModel,
                     'weight': 0})

            badges = bonus.getBadges()
            if badges is not None:
                for badge in badges:
                    nextModel = Pm3LastOperationTooltipRewardsModel()
                    nextModel.setIcon(badge.getBonusIcon())
                    bonusesList.append({'modelEl': nextModel,
                     'weight': 2})

        if not bonusesList:
            return []
        else:
            sortedBonuses = sorted(bonusesList, key=lambda x: x['weight'])
            return [ item['modelEl'] for item in sortedBonuses ]
