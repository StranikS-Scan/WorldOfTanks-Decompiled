# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/missions/packers/conditions.py
import logging
import typing
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.impl.gen.view_models.common.missions.conditions.condition_group_model import ConditionGroupModel
from gui.impl.gen.view_models.common.missions.conditions.preformatted_condition_model import PreformattedConditionModel
from gui.server_events import formatters
from gui.server_events.cond_formatters import FORMATTER_IDS
from gui.server_events.cond_formatters import FormattableField
from gui.server_events.cond_formatters import prebattle, postbattle, vehicle
from gui.server_events.cond_formatters.bonus import BattlesCountFormatter
from gui.server_events.cond_formatters.bonus import MissionsBonusConditionsFormatter
from gui.server_events.formatters import PreFormattedCondition
from gui.shared.formatters.plain_text import PlainTextFormatter
from helpers import i18n
from personal_missions_constants import CONDITION_ICON
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Optional, Union
    from gui.server_events.conditions import _Condition
    from gui.server_events.conditions import _ConditionsGroup
    from gui.server_events.event_items import ServerEventAbstract
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)
CONDITION_GROUP_AND = 'and'
CONDITION_GROUP_OR = 'or'
CONDITION_GROUP_NOP = 'nop'
CONDITION_GROUP_NOT = 'not'
CONDITION_DEFAULT_NAME = 'play'
CONDITION_GROUP_TYPE_LIST = (CONDITION_GROUP_AND,
 CONDITION_GROUP_OR,
 CONDITION_GROUP_NOP,
 CONDITION_GROUP_NOT)
CONDITION_SPECIFIC_TYPE_LIST = (CONDITION_DEFAULT_NAME,)
CONDITION_TYPE_LIST = CONDITION_GROUP_TYPE_LIST + CONDITION_SPECIFIC_TYPE_LIST

class PreFormattedConditionModelPacker(object):

    @staticmethod
    def pack(preFormattedConditionTuple, conditionType):
        model = getDefaultPreformattedConditionModel()
        textFormatter = getDefaultPlainTextFormatter()
        if conditionType:
            model.setConditionType(conditionType)
        if preFormattedConditionTuple.titleData:
            model.setTitleData(textFormatter.getPlainTextFromFormattedField(preFormattedConditionTuple.titleData))
        if preFormattedConditionTuple.descrData:
            model.setDescrData(textFormatter.getPlainTextFromFormattedField(preFormattedConditionTuple.descrData))
        if preFormattedConditionTuple.iconKey:
            iconKey = preFormattedConditionTuple.iconKey
            model.setIconKey(iconKey)
        if preFormattedConditionTuple.current:
            current = preFormattedConditionTuple.current
            model.setCurrent(current)
        if preFormattedConditionTuple.earned:
            model.setEarned(max(preFormattedConditionTuple.earned, 0))
        if preFormattedConditionTuple.total:
            total = preFormattedConditionTuple.total
            model.setTotal(total)
        if preFormattedConditionTuple.progressID:
            progressID = preFormattedConditionTuple.progressID
            model.setProgressType(progressID)
        if preFormattedConditionTuple.sortKey:
            sortKey = preFormattedConditionTuple.sortKey
            model.setSortKey(sortKey)
        return model


class UIConditionPacker(object):

    def _packConditions(self, conditions, event):
        ctx = {'data': conditions,
         'event': event}
        classType = None
        try:
            classType = ctx['data'].classType
        except AttributeError:
            pass

        if classType != 'ConditionsGroup':
            return (self._travers(ctx), CONDITION_GROUP_NOP)
        else:
            booleanOperation = ctx['data'].getName()
            ctx['data'] = ctx['data'].items
            return (self._traversConditionItemsList(ctx), booleanOperation)

    def _convertConditionIntoPreFormattedCondition(self, ctx):
        raise SoftException('This method should not be reached in this context')

    def pack(self, event, model):
        return self._pack(event, model)

    def _pack(self, event, model):
        raise SoftException('This method should not be reached in this context')

    def _traversConditionItemsList(self, ctx):
        if not ctx['data']:
            return None
        else:
            result = []
            for condition in ctx['data']:
                ctx['data'] = condition
                result.append(self._travers(ctx))

            return result

    def _traversConditionGroup(self, ctx, operation):
        model = getDefaultConditionGroupModel()
        model.setConditionType(operation)
        for condition in self._traversConditionItemsList(ctx):
            if not condition:
                continue
            model.getItems().addViewModel(condition)

        return model

    def _traversCondition(self, ctx):
        condition = ctx['data']
        conditionName = condition.getName()
        preFormattedCondition = self._convertConditionIntoPreFormattedCondition(ctx)
        if not preFormattedCondition:
            _logger.error('Should not be reached: preFormattedConditionTuple was not received.')
            return None
        else:
            if len(preFormattedCondition) > 1:
                _logger.error('Should not be reached: More than one tuple was received.')
            preFmtCond = preFormattedCondition[0]
            return getDefaultPreFormattedConditionModelPacker().pack(preFmtCond, conditionName)

    def _travers(self, ctx):
        ctx['data'] = ctx.get('data', [])
        contextData = ctx['data']
        classType = None
        try:
            classType = contextData.classType
        except AttributeError:
            _logger.error('Type %s does not have attribute classType.', type(contextData))

        if classType == 'ConditionsGroup':
            booleanOperation = contextData.getName()
            ctx['data'] = contextData.items
            return self._traversConditionGroup(ctx, booleanOperation)
        elif classType == 'Condition':
            if contextData.isHidden():
                return
            return self._traversCondition(ctx)
        else:
            _logger.error('Condition packer for %s type is not implemented yet.', type(contextData))
            return


class BonusConditionPacker(UIConditionPacker):

    def __init__(self):
        super(BonusConditionPacker, self).__init__()
        self.isPostBattleConditionPresent = False

    def _convertConditionIntoPreFormattedCondition(self, ctx):
        conditioName = ctx['data'].getName()
        groupFormatter = getDefaultMissionsBonusConditionsFormatter().getConditionFormatter(conditioName)
        if groupFormatter:
            return groupFormatter.format(ctx['data'], ctx['event'])
        if conditioName != 'battles':
            _logger.error('No formatter for conditioName %s.', conditioName)
        arePostBattleCondsPresent = self.isPostBattleConditionPresent
        battleFormatter = getDefaultBattlesCountFormatter(arePostBattleCondsPresent)
        return battleFormatter.format(ctx['data'], ctx['event'])

    def packWithPostBattleCondCheck(self, event, model, isPostBattleConditionPresent):
        self.isPostBattleConditionPresent = isPostBattleConditionPresent
        self.pack(event, model)

    def _pack(self, event, model):
        bonusConditions = event.bonusCond.getConditions()
        bonusCondsModelList, typeOfBonusConditionGroup = self._packConditions(bonusConditions, event)
        isItemAddedToBonusCondModel = False
        if not bonusCondsModelList:
            _logger.debug('BonusConditions were not received for event %s.', event.getID())
            return None
        else:
            for bonusCondModel in bonusCondsModelList:
                if not bonusCondModel:
                    continue
                model.getItems().addViewModel(bonusCondModel)
                isItemAddedToBonusCondModel = True

            if isItemAddedToBonusCondModel:
                model.setConditionType(typeOfBonusConditionGroup)
            return None


class PostBattleConditionPacker(UIConditionPacker):

    def __init__(self):
        super(PostBattleConditionPacker, self).__init__()
        self.postBattleCondFormatter = getDefaultPostBattleCondFormatter()
        self.typeOfPostBattleConditionGroup = CONDITION_GROUP_NOP

    def _convertConditionIntoPreFormattedCondition(self, ctx):
        conditionType = ctx['data'].getName()
        groupFormatter = self.postBattleCondFormatter.getConditionFormatter(conditionType)
        if not groupFormatter:
            _logger.error('Condition packer for type %s does not exists.', conditionType)
            return None
        else:
            return groupFormatter.format(ctx['data'], ctx['event'])

    def _pack(self, event, model):
        postBattleConditions = event.postBattleCond.getConditions()
        postBattleCondsModelList, self.typeOfPostBattleConditionGroup = self._packConditions(postBattleConditions, event)
        if not postBattleCondsModelList:
            _logger.debug('PostBattleConditions were not received for event %s.', event.getID())
            return None
        else:
            for postBattleCondModel in postBattleCondsModelList:
                if not postBattleCondModel:
                    continue
                model.getItems().addViewModel(postBattleCondModel)

            model.setConditionType(self.typeOfPostBattleConditionGroup)
            return None

    @classmethod
    def packDefaultCondition(cls, model):
        model.getItems().addViewModel(cls.getPlayBattleCondition())
        model.setConditionType(CONDITION_GROUP_AND)

    @staticmethod
    def getPlayBattleCondition(packer=PreFormattedConditionModelPacker):
        titleArgs = (i18n.makeString(QUESTS.DETAILS_CONDITIONS_PLAYBATTLE_TITLE),)
        descrArgs = (i18n.makeString(QUESTS.MISSIONDETAILS_CONDITIONS_PLAYBATTLE),)
        playBattleCondition = formatters.packMissionIconCondition(FormattableField(FORMATTER_IDS.SIMPLE_TITLE, titleArgs), MISSIONS_ALIASES.NONE, FormattableField(FORMATTER_IDS.DESCRIPTION, descrArgs), CONDITION_ICON.BATTLES)
        return packer.pack(playBattleCondition, CONDITION_DEFAULT_NAME)


def getDefaultBonusCondPacker():
    return BonusConditionPacker()


def getDefaultPreBattleCondFormatter():
    return prebattle.MissionsPreBattleConditionsFormatter()


def getDefaultPostBattleCondFormatter():
    return postbattle.MissionsPostBattleConditionsFormatter()


def getDefaultVehicleCondFormatter():
    return vehicle.MissionsVehicleConditionsFormatter()


def getDefaultMissionsBonusConditionsFormatter():
    return MissionsBonusConditionsFormatter()


def getDefaultBattlesCountFormatter(hasPostBattleConditions):
    return BattlesCountFormatter(hasPostBattleConditions)


def getDefaultPreformattedConditionModel():
    return PreformattedConditionModel()


def getDefaultPlainTextFormatter():
    return PlainTextFormatter()


def getDefaultConditionGroupModel():
    return ConditionGroupModel()


def getDefaultPreFormattedConditionModelPacker():
    return PreFormattedConditionModelPacker()
