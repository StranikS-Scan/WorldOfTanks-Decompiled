# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/limited_ui_unlock_info_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.condition_group import ConditionGroup
from gui.impl.gen.view_models.views.lobby.tooltips.limited_ui_unlock_info_tooltip_model import LimitedUiUnlockInfoTooltipModel
from gui.impl.pub import ViewImpl
from gui.impl import backport
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.limited_ui.lui_controller import CallHandlerReason
from helpers import dependency
from skeletons.gui.game_control import ILimitedUIController

class LimitedUiUnlockInfoTooltip(ViewImpl):
    __slots__ = ('__ruleID',)
    __RULE_TO_RESOURCE_BRANCH_NAME = {LuiRules.PERSONAL_MISSIONS_CONTENT: 'personal_missions',
     LuiRules.TOURNAMENTS_CONTENT: 'tournaments',
     LuiRules.VERSUS_AI_CONTENT: 'versus_ai',
     LuiRules.STRONGHOLD_CONTENT: 'stronghold'}
    __limitedUIController = dependency.descriptor(ILimitedUIController)

    def __init__(self, ruleID):
        settings = ViewSettings(R.views.lobby.tooltips.LimitedUiUnlockInfoTooltip())
        settings.model = LimitedUiUnlockInfoTooltipModel()
        super(LimitedUiUnlockInfoTooltip, self).__init__(settings)
        self.__ruleID = ruleID

    @property
    def viewModel(self):
        return super(LimitedUiUnlockInfoTooltip, self).getViewModel()

    @staticmethod
    def getFooterResource(resourceBranchName, resourceName):
        return R.invalid() if resourceBranchName is None else R.strings.tooltips.limited_ui.unlock_info.footer.dyn(resourceBranchName).dyn(resourceName)()

    def _onLoading(self, *args, **kwargs):
        super(LimitedUiUnlockInfoTooltip, self)._onLoading(*args, **kwargs)
        self.__updateModel()
        self.__limitedUIController.startObserve(self.__ruleID, self.__onLuiRuleChanged)

    def _finalize(self):
        self.__limitedUIController.stopObserve(self.__ruleID, self.__onLuiRuleChanged)
        super(LimitedUiUnlockInfoTooltip, self)._finalize()

    def __onLuiRuleChanged(self, _, reason):
        if reason == CallHandlerReason.CONDITION_REPRESENTATION_CHANGED:
            self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            self.__fillConditionGroups(model.getConditionGroups())
            resourceBranchName = self.__RULE_TO_RESOURCE_BRANCH_NAME.get(self.__ruleID)
            model.setFooterTitleText(self.getFooterResource(resourceBranchName, 'title'))
            model.setFooterText(self.getFooterResource(resourceBranchName, 'desc'))

    def __fillConditionGroups(self, conditionGroupsModel):
        conditionGroupsModel.clear()
        conditionRepresentation = self.__limitedUIController.getRuleConditionRepresentation(self.__ruleID)
        for conditionGroup in conditionRepresentation:
            conditionGroupModel = ConditionGroup()
            conditions = conditionGroupModel.getConditions()
            for condition in conditionGroup:
                conditions.addString(backport.text(R.strings.tooltips.limited_ui.unlock_info.condition.dyn(condition.resourceName)(), **condition.kwargs))

            conditionGroupsModel.addViewModel(conditionGroupModel)

        conditionGroupsModel.invalidate()
