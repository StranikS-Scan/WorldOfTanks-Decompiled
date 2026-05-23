# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/newbie_restrictions_tooltip_adapters.py
import logging
from frameworks.wulf import Array
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.condition_group import ConditionGroup
from gui.impl.gen.view_models.views.lobby.tooltips.newbie_restrictions_tooltip_model import NewbieRestrictionsTooltipModel
from gui.limited_ui.lui_rules_storage import LuiRules
from helpers import dependency, int2roman
from skeletons.gui.game_control import ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

def _getFooterResource(resourceBranchName, resourceName):
    return R.invalid() if resourceBranchName is None else R.strings.tooltips.newbie_restrictions.footer.dyn(resourceBranchName).dyn(resourceName)()


class NewbieRestrictionsTooltipAdapter(object):

    def fillConditionGroups(self, conditionGroups):
        raise NotImplementedError()

    def fillFooter(self, model):
        raise NotImplementedError()

    def _fillFooter(self, model, resourceBranchName):
        model.setFooterTitleText(_getFooterResource(resourceBranchName, 'title'))
        model.setFooterText(_getFooterResource(resourceBranchName, 'desc'))


class LimitedUINewbieRestrictionsTooltipAdapter(NewbieRestrictionsTooltipAdapter):
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __LUI_RULE_TO_RESOURCE_BRANCH_NAME = {LuiRules.PERSONAL_MISSIONS_CONTENT: 'personal_missions',
     LuiRules.TOURNAMENTS_CONTENT: 'tournaments',
     LuiRules.VERSUS_AI_CONTENT: 'versus_ai',
     LuiRules.STRONGHOLD_CONTENT: 'stronghold',
     LuiRules.RANKED_CONTENT: 'ranked',
     LuiRules.SPEC_BATTLE_CONTENT: 'spec_battles',
     LuiRules.COMP7_CONTENT: 'comp7',
     LuiRules.ARCADE_CONTENT: 'arcade',
     LuiRules.FIELD_TRIALS_CONTENT: 'field_trials',
     LuiRules.FRONTLINE_CONTENT: 'frontline'}

    def __init__(self, luiRuleID):
        self.__luiRuleID = luiRuleID

    def fillConditionGroups(self, conditionGroups):
        conditionRepresentation = self.__limitedUIController.getRuleConditionRepresentation(self.__luiRuleID)
        for conditionGroup in conditionRepresentation:
            conditionGroupModel = ConditionGroup()
            conditions = conditionGroupModel.getConditions()
            for condition in conditionGroup:
                conditions.addString(backport.text(R.strings.tooltips.newbie_restrictions.condition.dyn(condition.resourceName)(), **condition.kwargs))

            conditionGroups.addViewModel(conditionGroupModel)

    def fillFooter(self, model):
        resourceBranchName = self.__LUI_RULE_TO_RESOURCE_BRANCH_NAME.get(self.__luiRuleID)
        if resourceBranchName is None:
            _logger.warning('There is no resource branch name for limited ui rule %s', self.__luiRuleID)
        self._fillFooter(model, resourceBranchName)
        return


class ChatLockNewbieRestrictionsTooltipAdapter(NewbieRestrictionsTooltipAdapter):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def fillConditionGroups(self, conditionGroups):
        conditionGroupModel = ConditionGroup()
        conditions = conditionGroupModel.getConditions()
        serverSettings = self.__lobbyContext.getServerSettings()
        conditions.addString(backport.text(R.strings.tooltips.newbie_restrictions.condition.battlesCountThreshold(), battlesCount=serverSettings.newbieChatLockConfig.battlesCountThreshold))
        conditions.addString(backport.text(R.strings.tooltips.newbie_restrictions.condition.vehicleLevelThreshold(), level=int2roman(serverSettings.newbieChatLockConfig.vehicleLevelThreshold)))
        conditionGroups.addViewModel(conditionGroupModel)

    def fillFooter(self, model):
        self._fillFooter(model, 'chats')
