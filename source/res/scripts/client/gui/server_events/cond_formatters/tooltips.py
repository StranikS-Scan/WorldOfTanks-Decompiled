# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/cond_formatters/tooltips.py
from constants import EVENT_TYPE
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.cond_formatters import packText, getSeparator, requirements
from gui.server_events.cond_formatters.formatters import ConditionFormatter, ConditionsFormatter
from gui.server_events.cond_formatters.requirements import prepareAccountConditionsGroup
from gui.server_events.conditions import GROUP_TYPE
from gui.server_events.events_helpers import getPreviousBattleQuest, isHalloween
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.server_events import IEventsCache
from soft_exception import SoftException

def reqStyle(_):
    return text_styles.main


def getSeparatorBlock(groupType=GROUP_TYPE.AND):
    label = getSeparator(groupType)
    if label:
        item = packText(text_styles.standard(label))
        return item
    else:
        return None


class MissionsAccountRequirementsFormatter(ConditionsFormatter):

    def __init__(self):
        super(MissionsAccountRequirementsFormatter, self).__init__({'token': _TokenRequirementFormatter(),
         'premiumAccount': requirements.PremiumAccountFormatter(),
         'premiumPlusAccount': requirements.PremiumPlusAccountFormatter(),
         'inClan': requirements.InClanRequirementFormatter(),
         'igrType': requirements.IgrTypeRequirementFormatter(),
         'GR': requirements.GlobalRatingRequirementFormatter(),
         'accountDossier': requirements.AccountDossierRequirementFormatter(),
         'vehiclesUnlocked': requirements.VehiclesRequirementFormatter(),
         'vehiclesOwned': requirements.VehiclesRequirementFormatter(),
         'hasReceivedMultipliedXP': requirements.HasReceivedMultipliedXPFormatter()})

    def format(self, conditions, event):
        if event.isGuiDisabled():
            return {}
        group = prepareAccountConditionsGroup(conditions, event)
        rqs = self._format(group, event)
        return rqs

    def _format(self, group, event, isNested=False, topHasOrGroup=False):
        result = []
        separator = getSeparatorBlock(group.getName())
        sortedItems = group.getSortedItems()
        itemsCount = len(sortedItems)
        for idx, condition in enumerate(sortedItems, 1):
            branch = []
            if not condition.isAvailable():
                conditionName = condition.getName()
                isNotLast = idx < itemsCount
                if conditionName in GROUP_TYPE.ALL():
                    isInOrGroup = topHasOrGroup or conditionName == GROUP_TYPE.OR
                    branch = self._format(condition, event, isNested=True, topHasOrGroup=isInOrGroup)
                    if branch and isInOrGroup and not isNested:
                        branch[0].update(bullet=TOOLTIPS.QUESTS_UNAVAILABLE_BULLET)
                    result.extend(branch)
                    if separator and isNotLast:
                        result.append(separator)
                else:
                    fmt = self.getConditionFormatter(conditionName)
                    if fmt:
                        branch = fmt.format(condition, event, reqStyle)
                    if branch:
                        result.extend(self._processNonGroupConidtions(branch, isNested, separator, topHasOrGroup, isNotLast))

        return result

    @classmethod
    def _processNonGroupConidtions(cls, branch, isNested, separator, isInOrGroup, isNotLast):
        formattedBranch = []
        for item in branch:
            if not isNested or not isInOrGroup:
                item.update(bullet=TOOLTIPS.QUESTS_UNAVAILABLE_BULLET)
            formattedBranch.append(item)

        if separator and isNotLast:
            formattedBranch.append(separator)
        return formattedBranch

    def _packCondition(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')

    def _packConditions(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')

    def _getFormattedField(self, *args, **kwargs):
        raise SoftException('This method should not be reached in this context')


class _TokenRequirementFormatter(ConditionFormatter):
    eventsCache = dependency.descriptor(IEventsCache)

    @classmethod
    def format(cls, condition, event, styler=reqStyle):
        style = styler(condition.isAvailable())
        result = []
        if event.getType() not in EVENT_TYPE.LIKE_BATTLE_QUESTS + EVENT_TYPE.LIKE_TOKEN_QUESTS:
            return result
        else:
            if isHalloween(event.getGroupID()):
                prevEvent = getPreviousBattleQuest(event)
                if prevEvent is not None and not prevEvent.isCompleted():
                    return [packText(style(backport.text(R.strings.quests.missionDetails.requirements.conclusion.previousIncomplete(), quest_name=prevEvent.getUserName())))]
            tokensNeedCount = condition.getNeededCount()
            return [packText(style(_ms(TOOLTIPS.QUESTS_UNAVAILABLE_TOKEN, tokenName=text_styles.neutral(condition.getUserName()), count=tokensNeedCount)))]
