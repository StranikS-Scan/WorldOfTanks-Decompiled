# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/tooltips/personal_missions_last_operation_tooltip.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.personal_missions_last_operation_tooltip_model import PersonalMissionsLastOperationTooltipModel, LastMissionStatus
from gui.impl.gen.view_models.views.lobby.personal_missions.tooltips.pm3_last_operation_tooltip_rewards_model import Pm3LastOperationTooltipRewardsModel
from gui.impl.pub import ViewImpl
from helpers import dependency, i18n
from skeletons.gui.game_control import IPersonalMissionsController
from skeletons.gui.shared import IItemsCache
rewards = [{'icon': 'R.images.gui.maps.icons.quests.bonuses.badges.c_220x220.badge_10045'}]

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
        model.setMissionStatus(LastMissionStatus.DEVELOPMENT)
        model.setName(i18n.makeString('#personal_missions:operations/title%d' % 11))
        model.setAll(len(ctrl.getFinalQuests()))
        model.setCompleted(len(ctrl.getFullCompletedFinalQuests()))
        array = model.getRewards()
        for item in rewards:
            nextModel = Pm3LastOperationTooltipRewardsModel()
            if 'name' in item:
                nextModel.setName(item['name'])
            nextModel.setIcon(item['icon'])
            array.addViewModel(nextModel)

        array.invalidate()
