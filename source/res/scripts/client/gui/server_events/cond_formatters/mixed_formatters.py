# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/cond_formatters/mixed_formatters.py
from collections import namedtuple
from constants import QUEST_PROGRESS_STATE
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.Scaleform.genConsts.QUEST_PROGRESS_BASE import QUEST_PROGRESS_BASE
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.server_events import formatters
from gui.server_events.cond_formatters import FormattableField, FORMATTER_IDS, BATTLE_RESULTS_KEYS
from gui.server_events.cond_formatters import postbattle
from gui.server_events.cond_formatters.bonus import MissionsBonusConditionsFormatter, BattlesCountFormatter
from gui.server_events.cond_formatters.formatters import ConditionsFormatter
from gui.server_events.cond_formatters.postbattle import GroupResult
from gui.server_events.cond_formatters.prebattle import PersonalMissionsVehicleConditionsFormatter
from gui.server_events.formatters import PreFormattedCondition
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import i18n
from personal_missions_constants import CONDITION_ICON, DISPLAY_TYPE

def _packPlayBattleCondition():
    titleArgs = (i18n.makeString(QUESTS.DETAILS_CONDITIONS_PLAYBATTLE_TITLE),)
    descrArgs = (i18n.makeString(QUESTS.MISSIONDETAILS_CONDITIONS_PLAYBATTLE),)
    return formatters.packMissionIconCondition(FormattableField(FORMATTER_IDS.SIMPLE_TITLE, titleArgs), MISSIONS_ALIASES.NONE, FormattableField(FORMATTER_IDS.DESCRIPTION, descrArgs), CONDITION_ICON.BATTLES)


class MissionBonusAndPostBattleCondFormatter(ConditionsFormatter):

    def __init__(self):
        super(MissionBonusAndPostBattleCondFormatter, self).__init__()
        self.bonusCondFormatter = MissionsBonusConditionsFormatter()
        self.postBattleCondFormatter = postbattle.MissionsPostBattleConditionsFormatter()

    def format(self, event):
        result = []
        bonusConditions = self.bonusCondFormatter.format(event.bonusCond, event)
        postBattleConditions = self.postBattleCondFormatter.format(event.postBattleCond, event)
        battleCountCondition = event.bonusCond.getConditions().find('battles')
        for pCondGroup in postBattleConditions:
            for bCondGroup in bonusConditions:
                if battleCountCondition is not None:
                    conditions = []
                    conditions.extend(pCondGroup)
                    conditions.extend(bCondGroup)
                    conditions.extend(BattlesCountFormatter(bool(pCondGroup)).format(battleCountCondition, event))
                else:
                    conditions = pCondGroup + bCondGroup
                if not conditions:
                    conditions.append(_packPlayBattleCondition())
                result.append(conditions)

        return result

    @classmethod
    def _packSeparator(cls, key):
        raise NotImplementedError


PERSONAL_MISSSIONS_FORMATTERS = {FORMATTER_IDS.SIMPLE_TITLE: formatters.simpleFormat,
 FORMATTER_IDS.CUMULATIVE: formatters.personalTitleCumulativeFormat,
 FORMATTER_IDS.COMPLEX: formatters.personalTitleCumulativeFormat,
 FORMATTER_IDS.RELATION: formatters.personalTitleRelationFormat,
 FORMATTER_IDS.DESCRIPTION: formatters.simpleFormat,
 FORMATTER_IDS.COMPLEX_RELATION: formatters.personalTitleComplexRelationFormat}
KEYS_ORDER = ('vehicleDamage', 'vehicleKills', 'vehicleStun', 'achievements', 'crits', 'multiStunEvent', 'top', 'results', 'damageDealt', 'kills', 'isAnyOurCrittedInnerModules', 'isNotSpotted', 'unitResults', 'clanKills', 'installedItem', 'correspondedCamouflage', 'win', 'isAlive')

def getKeySortOrder(key):
    if key in KEYS_ORDER:
        return KEYS_ORDER.index(key)
    return KEYS_ORDER.index('results') if key in BATTLE_RESULTS_KEYS else -1


def sortConditionsFunc(aData, bData):
    aCondData, _, aInOrGroup = aData
    bCondData, _, bInOrGroup = bData
    res = cmp(aInOrGroup, bInOrGroup)
    return res if res else cmp(getKeySortOrder(aCondData.sortKey), getKeySortOrder(bCondData.sortKey))


class PersonalMissionConditionsFormatter(ConditionsFormatter):

    def __init__(self):
        super(PersonalMissionConditionsFormatter, self).__init__()
        self._formatters = PERSONAL_MISSSIONS_FORMATTERS
        self.postBattleCondFormatter = postbattle.PersonalMissionsPostBattleConditionsFormatter()
        self.vehicleConditionsFormatter = PersonalMissionsVehicleConditionsFormatter()

    def format(self, event, isMain=None):
        conditionsData = []
        isAvailable = self._isConditionBlockAvailable(event, isMain)
        postBattleResult = self.postBattleCondFormatter.format(event.getPostBattleConditions(isMain), event)
        vehicleResult = self.vehicleConditionsFormatter.format(event.getVehicleRequirements(isMain), event)
        conditionsData.extend(self._packConditions(vehicleResult, isAvailable))
        conditionsData.extend(self._packConditions(postBattleResult, isAvailable))
        conditionsData = sorted(conditionsData, cmp=sortConditionsFunc)
        results = [ self._packCondition(*c) for c in conditionsData ]
        return results

    @classmethod
    def _isConditionBlockAvailable(cls, event, isMain):
        isAvailable = event.isUnlocked()
        if isMain:
            isAvailable = isAvailable and not event.isMainCompleted()
        elif not isMain:
            isAvailable = isAvailable and not event.isFullCompleted()
        return isAvailable

    def _getFormattedField(self, formattableField):
        formatter = self._formatters.get(formattableField.formatterID)
        return formatter(*formattableField.args)

    def _packConditions(self, groupResult, isAvailable):
        result = []
        if isinstance(groupResult, list):
            for res in groupResult:
                if isinstance(res, PreFormattedCondition):
                    result.append((res, isAvailable, False))
                result.extend(self._packConditions(res, isAvailable))

        elif isinstance(groupResult, GroupResult):
            for res in groupResult.results:
                if isinstance(res, PreFormattedCondition):
                    result.append((res, isAvailable, groupResult.isOrGroup))
                result.extend(self._packConditions(res, isAvailable))

        return result


class StringPersonalMissionConditionsFormatter(PersonalMissionConditionsFormatter):
    _CONDITION = namedtuple('_CONDITION', ['text', 'isInOrGroup'])

    def format(self, event, isMain=None):
        results = super(StringPersonalMissionConditionsFormatter, self).format(event, isMain)
        orConditions = [ q for q in results if q.isInOrGroup ]
        andConditions = [ q for q in results if not q.isInOrGroup ]
        andResult = ''
        for c in andConditions:
            andResult += '%s %s\n' % (i18n.makeString(QUESTS.QUEST_CONDITION_DOT), c.text)

        orTexts = [ '%s %s' % (i18n.makeString(QUESTS.QUEST_CONDITION_DOT), c.text) for c in orConditions ]
        orResult = ('\n%s\n' % i18n.makeString(QUESTS.QUEST_CONDITION_OR)).join(orTexts)
        return '%s\n%s' % (orResult, andResult) if orResult else andResult

    def _packCondition(self, preFormattedCondition, isAvailable, isInOrGroup):
        title = self._getFormattedField(preFormattedCondition.titleData)
        description = self._getFormattedField(preFormattedCondition.descrData)
        if description:
            text = description
        else:
            text = title
        return self._CONDITION(text, isInOrGroup)


def _wrapToNewConditionsFormat(result, isMain, isCompleted):
    if isMain:
        orderType = QUEST_PROGRESS_BASE.MAIN_ORDER_TYPE
    else:
        orderType = QUEST_PROGRESS_BASE.ADD_ORDER_TYPE
    return {'progressID': None,
     'initData': {'title': result.get('title'),
                  'description': result.get('description'),
                  'iconID': result.get('icon'),
                  'orderType': orderType,
                  'progressType': 'regular',
                  'isInOrGroup': result.get('isInOrGroup', False),
                  'topMetricIndex': -1},
     'progressData': {'current': 0,
                      'state': QUEST_PROGRESS_STATE.COMPLETED if isCompleted else QUEST_PROGRESS_STATE.NOT_STARTED,
                      'goal': 1,
                      'metrics': []}}


class PM1ConditionsFormatter(PersonalMissionConditionsFormatter):

    def format(self, event, isMain=None):
        results = super(PM1ConditionsFormatter, self).format(event, isMain)
        isCompleted = self._markAsCompleted(event, isMain)
        return [ self._getWrappedData(res, isMain, isCompleted) for res in results ]

    @classmethod
    def _getWrappedData(cls, res, isMain, isCompleted):
        return _wrapToNewConditionsFormat(res, isMain, isCompleted)

    def _packCondition(self, preFormattedCondition, isAvailable, isInOrGroup):
        return {'icon': preFormattedCondition.iconKey,
         'title': self._getFormattedField(preFormattedCondition.titleData),
         'description': self._getFormattedField(preFormattedCondition.descrData),
         'isEnabled': isAvailable,
         'isInOrGroup': isInOrGroup}

    @classmethod
    def _markAsCompleted(cls, event, isMain):
        raise NotImplementedError


class PM1AwardScreenConditionsFormatter(PM1ConditionsFormatter):

    @classmethod
    def _getWrappedData(cls, res, isMain, isCompleted):
        title = res.get('title')
        description = res.get('description')
        tooltip = ''
        if title and description:
            tooltip = makeTooltip(title, description)
        return {'initData': {'title': text_styles.middleTitle(title),
                      'iconID': res.get('icon'),
                      'progressType': 'regular',
                      'tooltip': tooltip},
         'progressData': {'current': 0,
                          'state': QUEST_PROGRESS_STATE.COMPLETED if isCompleted else QUEST_PROGRESS_STATE.FAILED,
                          'goal': 1}}

    @classmethod
    def _markAsCompleted(cls, event, isMain):
        return event.isMainCompleted() if isMain else event.isFullCompleted()


class PM1CardConditionsFormatter(PM1ConditionsFormatter):

    @classmethod
    def _markAsCompleted(cls, event, isMain):
        return (event.isMainCompleted() if isMain else event.isFullCompleted()) and not event.isInProgress()


class PM1BattleConditionsFormatter(PM1CardConditionsFormatter):

    @classmethod
    def _markAsCompleted(cls, event, isMain):
        return False


def _addDummyHeaderProgress(isMain):
    orderType = QUEST_PROGRESS_BASE.ADD_ORDER_TYPE
    key = PERSONAL_MISSIONS.CONDITIONS_UNLIMITED_LABEL_ADD
    if isMain:
        orderType = QUEST_PROGRESS_BASE.MAIN_ORDER_TYPE
        key = PERSONAL_MISSIONS.CONDITIONS_UNLIMITED_LABEL_MAIN
    return {'progressType': DISPLAY_TYPE.NONE,
     'orderType': orderType,
     'header': i18n.makeString(key)}


class PM1ConditionsFormatterAdapter(object):

    def __init__(self, event, conditionsFormatter):
        self.__event = event
        self.__conditionsFormatter = conditionsFormatter

    def bodyFormat(self, isMain=None):
        formatFunc = self.__conditionsFormatter.format
        return formatFunc(self.__event, isMain) if isMain is not None else formatFunc(self.__event, True) + formatFunc(self.__event, False)

    def headerFormat(self, isMain=None):
        return [self.addDummyHeaderProgress(isMain)] if isMain is not None else [self.addDummyHeaderProgress(True), self.addDummyHeaderProgress(False)]

    @classmethod
    def addDummyHeaderProgress(cls, isMain):
        orderType = QUEST_PROGRESS_BASE.MAIN_ORDER_TYPE if isMain else QUEST_PROGRESS_BASE.ADD_ORDER_TYPE
        return {'progressType': DISPLAY_TYPE.NONE,
         'orderType': orderType,
         'header': None}


class PM1CardConditionsFormatterAdapter(PM1ConditionsFormatterAdapter):

    def __init__(self, event):
        super(PM1CardConditionsFormatterAdapter, self).__init__(event, PM1CardConditionsFormatter())


class PM1BattleConditionsFormatterAdapter(PM1ConditionsFormatterAdapter):

    def __init__(self, event):
        super(PM1BattleConditionsFormatterAdapter, self).__init__(event, PM1BattleConditionsFormatter())


class PM1AwardScreenConditionsFormatterAdapter(PM1ConditionsFormatterAdapter):

    def __init__(self, event):
        super(PM1AwardScreenConditionsFormatterAdapter, self).__init__(event, PM1AwardScreenConditionsFormatter())
