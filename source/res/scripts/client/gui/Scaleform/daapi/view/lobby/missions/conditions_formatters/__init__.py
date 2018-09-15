# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/conditions_formatters/__init__.py
import weakref
from collections import namedtuple
import nations
from debug_utils import LOG_ERROR
from gui.Scaleform.genConsts.MISSIONS_ALIASES import MISSIONS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.NATIONS import NATIONS
from gui.server_events import formatters
from gui.server_events.cond_formatters.formatters import ConditionFormatter, ConditionsFormatter
from gui.server_events.conditions import GROUP_TYPE
from gui.server_events.formatters import RELATIONS_SCHEME
from gui.shared.formatters import text_styles
from helpers import i18n
from shared_utils import CONST_CONTAINER
MAX_CONDITIONS_IN_OR_SECTION_SUPPORED = 2

class CONDITION_ICON(CONST_CONTAINER):
    ASSIST_RADIO = 'assist_radio'
    ASSIST_TRACK = 'assist_track'
    ASSIST_STUN = 'assist_stun'
    ASSIST_STUN_DURATION = 'assist_stun_time'
    AWARD = 'award'
    BASE_CAPTURE = 'base_capture'
    BASE_DEF = 'base_def'
    BATTLES = 'battles'
    CREDITS = 'credits'
    DAMAGE = 'damage'
    DAMAGE_BLOCK = 'damage_block'
    DISCOVER = 'discover'
    EXPERIENCE = 'experience'
    FIRE = 'fire'
    GET_DAMAGE = 'get_damage'
    GET_HIT = 'get_hit'
    HIT = 'hit'
    HURT_1SHOT = 'hurt_1shot'
    HURT_VEHICLES = 'hurt_vehicles'
    KILL_1SHOT = 'kill_1shot'
    KILL_VEHICLES = 'kill_vehicles'
    MASTER = 'master'
    METERS = 'meters'
    MODULE_CRIT = 'module_crit'
    SAVE_HP = 'save_hp'
    SEC_ALIVE = 'sec_alive'
    SURVIVE = 'survive'
    TIMES_GET_DAMAGE = 'times_get_damage'
    TOP = 'top'
    WIN = 'win'
    FOLDER = 'folder'
    BARREL_MARK = 'barrel_mark'


UNSUPORTED_BATTLE_RESUTLS_KEYS = ('finishReason', 'gold', 'creditsToDraw', 'orderFreeXPFactor100', 'orderXPFactor100', 'winPoints', 'creditsContributionIn', 'achievementXP', 'igrXPFactor10', 'aogasFactor10', 'originalCreditsContributionIn', 'originalCreditsPenalty', 'originalTMenXP', 'boosterCredits', 'originalGold', 'avatarDamaged', 'team', 'deathCount', 'isAnyHitReceivedWhileCapturing', 'boosterCreditsFactor100', 'premiumCreditsFactor10', 'orderFortResource', 'originalCreditsContributionOut', 'factualXP', 'creditsContributionOut', 'orderTMenXP', 'orderFreeXP', 'boosterXP', 'avatarKills', 'boosterTMenXPFactor100', 'isAnyOurCrittedInnerModules', 'resourceAbsorbed', 'credits', 'tkillRating', 'creditsPenalty', 'percentFromSecondBestDamage', 'avatarDamageDealt', 'factualFreeXP', 'dailyXPFactor10', 'damageRating', 'repair', 'xpPenalty', 'fairplayFactor10', 'subtotalTMenXP', 'boosterXPFactor100', 'refSystemXPFactor10', 'originalXPPenalty', 'orderTMenXPFactor100', 'originalFortResource', 'subtotalXP', 'isEnemyBaseCaptured', 'isNotSpotted', 'originalFreeXP', 'orderXP', 'premiumVehicleXP', 'flagCapture', 'premiumVehicleXPFactor100', 'factualCredits', 'inBattleMaxKillingSeries', 'subtotalFreeXP', 'achievementFreeXP', 'subtotalCredits', 'killsBeforeTeamWasDamaged', 'boosterTMenXP', 'premiumXPFactor10', 'personalFortResource', 'typeCompDescr', 'deathReason', 'damageBeforeTeamWasDamaged', 'achievementCredits', 'isPremium', 'committedSuicide', 'rolloutsCount', 'index', 'subtotalGold', 'appliedPremiumCreditsFactor10', 'orderFortResourceFactor100', 'isTeamKiller', 'firstDamageTime', 'tmenXP', 'boosterFreeXP', 'appliedPremiumXPFactor10', 'boosterFreeXPFactor100', 'subtotalFortResource', 'orderCreditsFactor100', 'battleNum', 'aimerSeries')
POSSIBLE_BATTLE_RESUTLS_KEYS = {'spottedBeforeWeBecameSpotted': CONDITION_ICON.DISCOVER,
 'damagedWhileMoving': CONDITION_ICON.DAMAGE,
 'totalDamaged': CONDITION_ICON.DAMAGE,
 'soloFlagCapture': CONDITION_ICON.BASE_CAPTURE,
 'autoAimedShots': CONDITION_ICON.HIT,
 'movingAvgDamage': CONDITION_ICON.DAMAGE,
 'tdestroyedModules': CONDITION_ICON.MODULE_CRIT}
BATTLE_RESULTS_KEYS = {'capturePoints': CONDITION_ICON.BASE_CAPTURE,
 'critsCount': CONDITION_ICON.MODULE_CRIT,
 'damageAssistedRadio': CONDITION_ICON.ASSIST_RADIO,
 'damageAssistedRadioWhileInvisible': CONDITION_ICON.ASSIST_RADIO,
 'damageAssistedStun': CONDITION_ICON.ASSIST_STUN,
 'damageAssistedStunWhileInvisible': CONDITION_ICON.ASSIST_STUN,
 'damageAssistedTrack': CONDITION_ICON.ASSIST_TRACK,
 'damageAssistedTrackWhileInvisible': CONDITION_ICON.ASSIST_TRACK,
 'damageBlockedByArmor': CONDITION_ICON.DAMAGE_BLOCK,
 'damaged': CONDITION_ICON.HURT_VEHICLES,
 'damageDealt': CONDITION_ICON.DAMAGE,
 'damagedVehicleCntAssistedRadio': CONDITION_ICON.ASSIST_RADIO,
 'damagedVehicleCntAssistedStun': CONDITION_ICON.ASSIST_STUN,
 'damagedVehicleCntAssistedTrack': CONDITION_ICON.ASSIST_TRACK,
 'damagedWhileEnemyMoving': CONDITION_ICON.DAMAGE,
 'damageReceived': CONDITION_ICON.GET_DAMAGE,
 'directEnemyHits': CONDITION_ICON.HIT,
 'directHits': CONDITION_ICON.HIT,
 'directHitsReceived': CONDITION_ICON.GET_HIT,
 'directTeamHits': CONDITION_ICON.HIT,
 'droppedCapturePoints': CONDITION_ICON.BASE_DEF,
 'explosionEnemyHits': CONDITION_ICON.HIT,
 'explosionHits': CONDITION_ICON.HIT,
 'explosionHitsReceived': CONDITION_ICON.GET_HIT,
 'fortResource': CONDITION_ICON.FOLDER,
 'freeXP': CONDITION_ICON.EXPERIENCE,
 'health': CONDITION_ICON.SAVE_HP,
 'inBattleMaxPiercingSeries': CONDITION_ICON.HIT,
 'inBattleMaxSniperSeries': CONDITION_ICON.HIT,
 'innerModuleCritCount': CONDITION_ICON.MODULE_CRIT,
 'innerModuleDestrCount': CONDITION_ICON.MODULE_CRIT,
 'killedAndDamagedByAllSquadmates': CONDITION_ICON.KILL_VEHICLES,
 'kills': CONDITION_ICON.KILL_VEHICLES,
 'killsAssistedRadio': CONDITION_ICON.ASSIST_RADIO,
 'killsAssistedStun': CONDITION_ICON.ASSIST_STUN,
 'killsAssistedTrack': CONDITION_ICON.ASSIST_TRACK,
 'lifeTime': CONDITION_ICON.SEC_ALIVE,
 'markOfMastery': CONDITION_ICON.MASTER,
 'marksOnGun': CONDITION_ICON.BARREL_MARK,
 'mileage': CONDITION_ICON.METERS,
 'noDamageDirectHitsReceived': CONDITION_ICON.DAMAGE_BLOCK,
 'originalCredits': CONDITION_ICON.CREDITS,
 'originalXP': CONDITION_ICON.EXPERIENCE,
 'percentFromTotalTeamDamage': CONDITION_ICON.DAMAGE,
 'piercingEnemyHits': CONDITION_ICON.DAMAGE,
 'piercings': CONDITION_ICON.DAMAGE,
 'piercingsReceived': CONDITION_ICON.TIMES_GET_DAMAGE,
 'potentialDamageDealt': CONDITION_ICON.DAMAGE,
 'potentialDamageReceived': CONDITION_ICON.GET_DAMAGE,
 'shots': CONDITION_ICON.HIT,
 'sniperDamageDealt': CONDITION_ICON.DAMAGE,
 'soloHitsAssisted': CONDITION_ICON.ASSIST_RADIO,
 'spotted': CONDITION_ICON.DISCOVER,
 'spottedAndDamagedSPG': CONDITION_ICON.DISCOVER,
 'stunDuration': CONDITION_ICON.ASSIST_STUN_DURATION,
 'stunned': CONDITION_ICON.ASSIST_STUN,
 'stunNum': CONDITION_ICON.ASSIST_STUN,
 'tdamageDealt': CONDITION_ICON.DAMAGE,
 'tkills': CONDITION_ICON.KILL_VEHICLES,
 'xp': CONDITION_ICON.EXPERIENCE}
VEHICLE_TYPES = {'heavyTank': '#item_types:vehicle/tags/heavy_tank/name',
 'mediumTank': '#item_types:vehicle/tags/medium_tank/name',
 'lightTank': '#item_types:vehicle/tags/light_tank/name',
 'AT-SPG': '#item_types:vehicle/tags/at-spg/name',
 'SPG': '#item_types:vehicle/tags/spg/name'}

class FORMATTER_IDS:
    DESCRIPTION = 'descriptionFormatter'
    CUMULATIVE = 'cumulativeFormatter'
    COMPLEX = 'complex'
    RELATION = 'relationFormatter'
    COMPLEX_RELATION = 'complexRelationFormatter'
    SIMPLE_TITLE = 'simpleTitleFormatter'


class COMPLEX_CONDITION_BLOCK:
    ACHIEVEMENT = 'achievement'
    VEHICLES_LIST = 'vehicleIDs'
    VEHICLES_FILTERS = 'vehicles_filters'


FormattableField = namedtuple('FormattableField', 'formatterID args')

def packDescriptionField(description):
    return FormattableField(FORMATTER_IDS.DESCRIPTION, (description,))


def packText(label):
    return {'text': label}


def intersperse(sequence, item):
    """ Insert item in between each pair in the sequence.
    
    E.g.: intersperse([1, 2, 3], 0) -> [1, 0, 2, 0, 3]
    """
    result = []
    for element in sequence:
        result.append(element)
        result.append(item)

    if result:
        result.pop()
    return result


def getSeparator(groupType=GROUP_TYPE.AND):
    """
    Create a separator for the specified group type
    """
    if groupType == GROUP_TYPE.OR:
        return i18n.makeString('#quests:details/groups/or')
    else:
        return ''


def packTokenProgress(tokenId, questId, title, image, gotCount, needCount, isBigSize=False):
    if gotCount == needCount:
        tokensGot = text_styles.bonusAppliedText(gotCount)
    else:
        tokensGot = text_styles.stats(gotCount)
    tokensNeed = text_styles.standard(needCount)
    counterText = text_styles.disabled('{} / {}'.format(tokensGot, tokensNeed))
    return {'tokenId': tokenId,
     'questId': questId,
     'titleText': title,
     'isNormalSize': not isBigSize,
     'imgSrc': image,
     'countText': counterText}


class MissionFormatter(ConditionFormatter):
    """
    Base condition formatter for mission's GUI.
    Gets pre formatted data list for condition (typing.List[PreFormattedCondition]) ,
    which later used in cards formatter to get final view
    """

    @classmethod
    def _getTitle(cls, *args, **kwargs):
        return FormattableField(FORMATTER_IDS.SIMPLE_TITLE, (i18n.makeString(QUESTS.DETAILS_CONDITIONS_TARGET_TITLE),))

    def _getDescription(self, condition):
        raise NotImplementedError

    @classmethod
    def _getIconKey(cls, condition=None):
        return CONDITION_ICON.FOLDER

    def _packGui(self, *args, **kwargs):
        """
        Gets pre formatted data object PreFormatted condition, which used as data holder for final formatting.
        """
        raise NotImplementedError


class SimpleMissionsFormatter(MissionFormatter):

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            result.append(self._packGui(condition))
        return result

    def _packGui(self, condition):
        return formatters.packMissionIconCondition(self._getTitle(condition), MISSIONS_ALIASES.NONE, self._getDescription(condition), self._getIconKey(condition))


class MissionsVehicleListFormatter(MissionFormatter):

    def _format(self, condition, event):
        result = []
        if not event.isGuiDisabled():
            result.append(self._formatData(self._getTitle(condition), MISSIONS_ALIASES.NONE, condition))
        return result

    @classmethod
    def _getLabelKey(cls, condition=None):
        pass

    @classmethod
    def _getTitleKey(cls, condition=None):
        return QUESTS.DETAILS_CONDITIONS_TARGET_TITLE

    @classmethod
    def _getTitle(cls, condition):
        if condition.isAnyVehicleAcceptable():
            return FormattableField(FORMATTER_IDS.RELATION, (condition.relationValue,
             condition.relation,
             RELATIONS_SCHEME.DEFAULT,
             cls._getTitleKey(condition)))
        else:
            return FormattableField(FORMATTER_IDS.COMPLEX_RELATION, (condition.relationValue, condition.relation, cls._getTitleKey(condition)))

    @classmethod
    def _getDescription(cls, condition):
        labelKey = cls._getLabelKey(condition)
        if condition.isAnyVehicleAcceptable():
            labelKey = '%s/all' % labelKey
        if condition.isNegative():
            labelKey = '%s/not' % labelKey
        return packDescriptionField(i18n.makeString(labelKey))

    def _getConditionData(self, condition):
        """
        Gets detailed data about vehicle kill or vehicle damage condition description in a specific format,
        Displayed in detailed card view layout on condition click
        or in tooltip on card's condition rollover
        """
        data = {'description': i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_HEADER),
         'list': []}
        if condition.isAnyVehicleAcceptable():
            return None
        elif 'types' not in condition.data:
            _, fNations, fLevels, fClasses = condition.parseFilters()
            data['list'].append({'label': text_styles.standard(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_NATIONS)),
             'typeIcon': RES_ICONS.MAPS_ICONS_FILTERS_NATIONS_ALL,
             'list': self._getConditionNationsList(fNations or []),
             'def': text_styles.main(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_NATIONS_ALL))})
            data['list'].append({'label': text_styles.standard(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_TYPE)),
             'typeIcon': RES_ICONS.MAPS_ICONS_FILTERS_TANKS_ALL,
             'list': self._getConditionClassesList(fClasses or []),
             'def': text_styles.main(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_TYPE_ALL))})
            data['list'].append({'label': text_styles.standard(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_LEVEL)),
             'typeIcon': RES_ICONS.MAPS_ICONS_FILTERS_LEVELS_LEVEL_ALL,
             'list': self._getConditionLevelsList(fLevels or []),
             'def': text_styles.main(i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_LEVEL_ALL))})
            data['rendererLinkage'] = MISSIONS_ALIASES.VEHICLE_TYPE_RENDERER
            return {'data': data}
        else:
            conditions = [ self.__makeVehicleVO(vehicle) for vehicle, _ in condition.getVehiclesData() ]
            while len(conditions) < 6:
                conditions.append({'vehicleName': text_styles.main('---')})

            data['list'] = conditions
            data['rendererLinkage'] = MISSIONS_ALIASES.VEHICLE_ITEM_RENDERER
            return {'data': data}
            return None

    def _getConditionNationsList(self, nationIds):
        result = []
        for idx in nationIds:
            result.append({'icon': '../maps/icons/filters/nations/%s.png' % nations.NAMES[idx],
             'tooltip': i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_NATIONS_TOOLTIP, nation=i18n.makeString(NATIONS.all(nations.NAMES[idx])))})

        return result

    def _getConditionClassesList(self, classNames):
        result = []
        for name in classNames:
            result.append({'icon': '../maps/icons/filters/tanks/%s.png' % name,
             'tooltip': i18n.makeString(QUESTS.MISSIONDETAILS_VEHICLE_CONDITIONS_TYPE_TOOLTIP, type=i18n.makeString(VEHICLE_TYPES[name]))})

        return result

    def _getConditionLevelsList(self, levelNames):
        result = []
        for name in levelNames:
            result.append({'icon': '../maps/icons/filters/levels/level_%s.png' % name})

        return result

    def _formatData(self, title, progressType, condition, current=None, total=None, progressData=None):
        return self._packGui(title, progressType, self._getDescription(condition), current=current, total=total, conditionData=self._getConditionData(condition), progressData=progressData, condition=condition)

    def _packGui(self, title, progressType, label, current=None, total=None, conditionData=None, progressData=None, condition=None):
        return formatters.packMissionIconCondition(title, progressType, label, self._getIconKey(condition), current=current, total=total, conditionData=conditionData, progressData=progressData)

    @staticmethod
    def __makeVehicleVO(vehicle):
        return {'nationIcon': '../maps/icons/filters/nations/%s.png' % vehicle.nationName,
         'typeIcon': '../maps/icons/filters/tanks/%s.png' % vehicle.type,
         'levelIcon': '../maps/icons/filters/levels/level_%s.png' % vehicle.level,
         'vehicleIcon': vehicle.iconSmall,
         'vehicleName': text_styles.vehicleName(vehicle.shortUserName)}


class GroupFormatter(ConditionFormatter):
    """
    Base formatter for quests condition's groups ('AND' and 'OR' ).
    Collect and format conditions from group.
    May format conditions recursive, has linkage on formatters container.
    """

    def __init__(self, proxy):
        super(GroupFormatter, self).__init__()
        self._proxy = weakref.proxy(proxy)

    def getConditionFormatter(self, conditionName):
        return self._proxy.getConditionFormatter(conditionName)


class OrGroupFormatter(GroupFormatter):

    def __init__(self, proxy):
        super(OrGroupFormatter, self).__init__(proxy)
        self._andFormatter = _InnerAndGroupFormatter(proxy)

    def _format(self, condition, event):
        orResults = []
        conditions = condition.getSortedItems()
        if len(conditions) == MAX_CONDITIONS_IN_OR_SECTION_SUPPORED:
            for cond in conditions:
                formatter = self.getConditionFormatter(cond.getName())
                result = formatter.format(cond, event)
                orResults.append(result)

        else:
            LOG_ERROR('Unsupported conditions count in quest. SSE Bug. Wrong quest xml')
        return orResults

    def getConditionFormatter(self, conditionName):
        if conditionName == 'and':
            return self._andFormatter
        elif conditionName == 'or':
            LOG_ERROR("Unsupported double depth 'OR' in 'OR' in quest conditions. SSE Bug. Wrong quest xml")
            return None
        else:
            return super(OrGroupFormatter, self).getConditionFormatter(conditionName)
            return None


class AndGroupFormatter(GroupFormatter):

    def _format(self, condition, event):
        result = []
        andResults = []
        orGroups = []
        conditions = condition.getSortedItems()
        for cond in conditions:
            formatter = self.getConditionFormatter(cond.getName())
            if formatter:
                if cond.getName() == 'or':
                    orGroups.extend(formatter.format(cond, event))
                else:
                    andResults.extend(formatter.format(cond, event))

        if len(orGroups) == MAX_CONDITIONS_IN_OR_SECTION_SUPPORED:
            for orList in orGroups:
                orList.extend(andResults)
                result.append(orList)

        else:
            if len(orGroups):
                LOG_ERROR("Unsupported double depth 'OR' in 'OR' in quest conditions. SSE Bug. Wrong quest xml")
            result.append(andResults)
        return result


class MissionsBattleConditionsFormatter(ConditionsFormatter):

    def __init__(self, formatters):
        self.__groupConditionsFormatters = {'and': AndGroupFormatter(self),
         'or': OrGroupFormatter(self)}
        super(MissionsBattleConditionsFormatter, self).__init__(formatters)

    def getConditionFormatter(self, conditionName):
        if conditionName in self.__groupConditionsFormatters:
            return self.__groupConditionsFormatters[conditionName]
        else:
            return super(MissionsBattleConditionsFormatter, self).getConditionFormatter(conditionName)

    def format(self, conditions, event):
        result = []
        condition = conditions.getConditions()
        groupFormatter = self.getConditionFormatter(condition.getName())
        if groupFormatter:
            result.extend(groupFormatter.format(condition, event))
        return result


class _InnerAndGroupFormatter(GroupFormatter):

    def _format(self, condition, event):
        andResults = []
        conditions = condition.getSortedItems()
        for cond in conditions:
            formatter = self.getConditionFormatter(cond.getName())
            andResults.extend(formatter.format(cond, event))

        return andResults
