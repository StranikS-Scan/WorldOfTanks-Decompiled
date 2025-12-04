# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/shared/events_packers.py
import logging
from armory_yard_constants import CONDITION_PREFIX
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.cond_formatters import FORMATTER_IDS, FormattableField
from gui.server_events.cond_formatters.bonus import CumulativeResultFormatter
from gui.server_events.cond_formatters.postbattle import BattleResultsFormatter
from gui.server_events.conditions import getCustomDescriptionValueFromConditionData
from gui.shared.missions.packers.conditions import BonusConditionPacker, PostBattleConditionPacker, getDefaultMissionsBonusConditionsFormatter, getDefaultBattlesCountFormatter
from gui.shared.missions.packers.events import BattleQuestUIDataPacker
_logger = logging.getLogger(__name__)
_RES_CUMULATIVE_DESCR = R.strings.armory_quest_conditions.conditions.cumulative
_RES_POST_BATTLE_DESCR = R.strings.armory_quest_conditions.conditions.postbattle

def packDescriptionByResource(res, data):
    if res:
        value = getCustomDescriptionValueFromConditionData(data)
        pluralCount = int(value)
        value = backport.getNiceNumberFormat(value)
        return FormattableField(FORMATTER_IDS.DESCRIPTION, (backport.ntext(res(), pluralCount, value=value),))
    else:
        return None


class ArmoryCumulativeResultFormatter(CumulativeResultFormatter):

    def _getDescription(self, condition):
        resCumulativeDescr = _RES_CUMULATIVE_DESCR
        if condition.keyName:
            resCumulativeDescr = resCumulativeDescr.dyn(condition.keyName)
            result = packDescriptionByResource(resCumulativeDescr, condition.getData())
            return result or super(ArmoryCumulativeResultFormatter, self)._getDescription(condition)
        return super(ArmoryCumulativeResultFormatter, self)._getDescription(condition)


class AYBonusConditionPacker(BonusConditionPacker):
    BATTLE_TYPE = u'battles'

    def __init__(self):
        super(AYBonusConditionPacker, self).__init__()
        self.__formatter = getDefaultMissionsBonusConditionsFormatter()
        self.__formatter.updateFormatters({'cumulative': ArmoryCumulativeResultFormatter(),
         'cumulativeExt': ArmoryCumulativeResultFormatter(),
         'unit': ArmoryCumulativeResultFormatter()})
        self.__battlesCountFormatter = getDefaultBattlesCountFormatter(self.isPostBattleConditionPresent)

    def packWithPostBattleCondCheck(self, event, model, isPostBattleConditionPresent):
        self.isPostBattleConditionPresent = isPostBattleConditionPresent
        self.pack(event, model)

    def packBattlesBonusCond(self, event, model):
        bonusConditions = event.bonusCond.getConditions()
        bonusCondsModelList, _ = self._packConditions(bonusConditions, event)
        if bonusCondsModelList:
            for condition in bonusCondsModelList:
                if condition.getConditionType() == self.BATTLE_TYPE:
                    model.setCurrent(condition.getCurrent())
                    model.setEarned(condition.getEarned())
                    model.setTotal(condition.getTotal())
                    model.setIconKey(condition.getIconKey())

        return None

    def pack(self, event, bonusModel):
        return self._pack(event, bonusModel)

    def _pack(self, event, model):
        bonusConditions = event.bonusCond.getConditions()
        bonusCondsModelList, typeOfBonusConditionGroup = self._packConditions(bonusConditions, event)
        isItemAddedToBonusCondModel = False
        if not bonusCondsModelList:
            _logger.debug('BonusConditions were not received for event %s.', event.getID())
            return None
        else:
            for bonusCondModel in bonusCondsModelList:
                if not bonusCondModel or bonusCondModel.getConditionType() == self.BATTLE_TYPE:
                    continue
                model.getItems().addViewModel(bonusCondModel)
                isItemAddedToBonusCondModel = True

            if isItemAddedToBonusCondModel:
                model.setConditionType(typeOfBonusConditionGroup)
            return None

    def _convertConditionIntoPreFormattedCondition(self, ctx):
        conditioName = ctx['data'].getName()
        groupFormatter = self.__formatter.getConditionFormatter(conditioName)
        if groupFormatter:
            return groupFormatter.format(ctx['data'], ctx['event'])
        if conditioName != 'battles':
            _logger.error('No formatter for conditioName %s.', conditioName)
        return self.__battlesCountFormatter.format(ctx['data'], ctx['event'])


class ArmoryBattleResultsFormatter(BattleResultsFormatter):

    def _getDescription(self, condition):
        resPostbattleDescr = _RES_POST_BATTLE_DESCR
        if condition.keyName:
            resPostbattleDescr = resPostbattleDescr.dyn(condition.keyName)
            result = packDescriptionByResource(resPostbattleDescr, condition.getData())
            return result or super(ArmoryBattleResultsFormatter, self)._getDescription(condition)
        return super(ArmoryBattleResultsFormatter, self)._getDescription(condition)


class AYPostBattleConditionPacker(PostBattleConditionPacker):

    def __init__(self):
        super(AYPostBattleConditionPacker, self).__init__()
        self.postBattleCondFormatter.updateFormatters({'results': ArmoryBattleResultsFormatter()})


class ArmoryYardQuestUIDataPacker(BattleQuestUIDataPacker):
    COMPLETE_PROGRESS_COUNT = 1
    IN_PROGRESS_COUNT = 0

    def _packPostBattleConds(self, model):
        postBattleContitionPacker = AYPostBattleConditionPacker()
        postBattleContitionPacker.pack(self._event, model.postBattleCondition)

    def _packBonusConds(self, model):
        bonusConditionPacker = AYBonusConditionPacker()
        bonusConditionPacker.packBattlesBonusCond(self._event, model)
        postBattleConditions = model.postBattleCondition.getItems()
        bonusConditionPacker.packWithPostBattleCondCheck(self._event, model.bonusCondition, bool(postBattleConditions))
        if postBattleConditions:
            for item in postBattleConditions:
                total = model.getTotal()
                current = model.getCurrent()
                earned = model.getEarned()
                if current:
                    item.setCurrent(current)
                else:
                    item.setCurrent(self.COMPLETE_PROGRESS_COUNT if self._event.isCompleted() else self.IN_PROGRESS_COUNT)
                item.setTotal(total if total else self.COMPLETE_PROGRESS_COUNT)
                item.setEarned(earned)

    def _packBonuses(self, model):
        super(ArmoryYardQuestUIDataPacker, self)._packBonuses(model)
        for bonusModel in model.getBonuses():
            tooltipLocalID = bonusModel.getTooltipId()
            if self._event.getID().startswith(CONDITION_PREFIX):
                tooltipUniqueID = self._event.getMainID() << 16 | self._event.getSubCondID() << 8 | int(tooltipLocalID)
            else:
                tooltipUniqueID = id(bonusModel)
            tooltip = self._tooltipData.pop(tooltipLocalID)
            self._tooltipData[tooltipUniqueID] = tooltip
            bonusModel.setTooltipId(str(tooltipUniqueID))
