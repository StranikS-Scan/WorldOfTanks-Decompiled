# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/cond_formatters/__init__.py
from collections import namedtuple
import nations
from personal_missions_constants import CONDITION_ICON
from soft_exception import SoftException
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.conditions import GROUP_TYPE
from gui.server_events.formatters import RELATIONS_SCHEME, RELATIONS
from gui.shared.formatters import text_styles
from helpers import i18n, int2roman
MAX_CONDITIONS_IN_OR_SECTION_SUPPORED = 2
TOP_RANGE_HIGHEST = 1
TOP_RANGE_LOWEST = 15

class CONDITION_SIZE(object):
    NORMAL = 'normal'
    MINIMIZED = 'minimized'


UNSUPORTED_BATTLE_RESUTLS_KEYS = ('finishReason', 'gold', 'creditsToDraw', 'orderFreeXPFactor100', 'orderXPFactor100', 'winPoints', 'creditsContributionIn', 'achievementXP', 'igrXPFactor10', 'aogasFactor10', 'originalCreditsContributionIn', 'originalCreditsPenalty', 'originalTMenXP', 'boosterCredits', 'originalGold', 'avatarDamaged', 'team', 'deathCount', 'isAnyHitReceivedWhileCapturing', 'boosterCreditsFactor100', 'premiumCreditsFactor10', 'orderFortResource', 'originalCreditsContributionOut', 'factualXP', 'creditsContributionOut', 'orderTMenXP', 'orderFreeXP', 'boosterXP', 'avatarKills', 'boosterTMenXPFactor100', 'resourceAbsorbed', 'credits', 'tkillRating', 'creditsPenalty', 'percentFromSecondBestDamage', 'avatarDamageDealt', 'factualFreeXP', 'dailyXPFactor10', 'damageRating', 'repair', 'xpPenalty', 'fairplayFactor10', 'subtotalTMenXP', 'boosterXPFactor100', 'refSystemXPFactor10', 'originalXPPenalty', 'orderTMenXPFactor100', 'originalFortResource', 'subtotalXP', 'originalFreeXP', 'orderXP', 'premiumVehicleXP', 'flagCapture', 'premiumVehicleXPFactor100', 'factualCredits', 'inBattleMaxKillingSeries', 'subtotalFreeXP', 'achievementFreeXP', 'subtotalCredits', 'killsBeforeTeamWasDamaged', 'boosterTMenXP', 'premiumXPFactor10', 'personalFortResource', 'typeCompDescr', 'deathReason', 'damageBeforeTeamWasDamaged', 'achievementCredits', 'isPremium', 'committedSuicide', 'rolloutsCount', 'index', 'subtotalGold', 'appliedPremiumCreditsFactor10', 'orderFortResourceFactor100', 'isTeamKiller', 'firstDamageTime', 'tmenXP', 'boosterFreeXP', 'appliedPremiumXPFactor10', 'boosterFreeXPFactor100', 'subtotalFortResource', 'orderCreditsFactor100', 'battleNum', 'aimerSeries')
POSSIBLE_BATTLE_RESUTLS_KEYS = {'damagedWhileMoving': CONDITION_ICON.DAMAGE,
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
 'xp': CONDITION_ICON.EXPERIENCE,
 'xpForAttack': CONDITION_ICON.EXPERIENCE,
 'xpForAssist': CONDITION_ICON.EXPERIENCE,
 'xpOther': CONDITION_ICON.EXPERIENCE,
 'spottedBeforeWeBecameSpotted': CONDITION_ICON.DISCOVER,
 'isEnemyBaseCaptured': CONDITION_ICON.BASE_CAPTURE,
 'isAnyOurCrittedInnerModules': CONDITION_ICON.SURVIVE,
 'isNotSpotted': CONDITION_ICON.SURVIVE}
BATTLE_RESULTS_AGGREGATED_KEYS = {tuple(sorted(['damagedVehicleCntAssistedTrack', 'damagedVehicleCntAssistedRadio'])): CONDITION_ICON.ASSIST,
 tuple(sorted(['killsAssistedTrack', 'killsAssistedRadio'])): CONDITION_ICON.ASSIST,
 tuple(sorted(['damageAssistedStun', 'damageAssistedTrack'])): CONDITION_ICON.ASSIST,
 tuple(sorted(['killsAssistedStun', 'killsAssistedTrack'])): CONDITION_ICON.ASSIST,
 tuple(sorted(['damagedVehicleCntAssistedStun', 'damagedVehicleCntAssistedTrack'])): CONDITION_ICON.ASSIST}
VEHICLE_TYPES = {'heavyTank': '#item_types:vehicle/tags/heavy_tank/name',
 'mediumTank': '#item_types:vehicle/tags/medium_tank/name',
 'lightTank': '#item_types:vehicle/tags/light_tank/name',
 'AT-SPG': '#item_types:vehicle/tags/at-spg/name',
 'SPG': '#item_types:vehicle/tags/spg/name'}

class FORMATTER_IDS(object):
    DESCRIPTION = 'descriptionFormatter'
    CUMULATIVE = 'cumulativeFormatter'
    COMPLEX = 'complex'
    RELATION = 'relationFormatter'
    COMPLEX_RELATION = 'complexRelationFormatter'
    SIMPLE_TITLE = 'simpleTitleFormatter'


class COMPLEX_CONDITION_BLOCK(object):
    ACHIEVEMENT = 'achievement'
    VEHICLES_LIST = 'vehicles_list'
    VEHICLES_FILTERS = 'vehicles_filters'


FormattableField = namedtuple('FormattableField', 'formatterID args')

def packDescriptionField(description):
    return FormattableField(FORMATTER_IDS.DESCRIPTION, (i18n.makeString(description),))


def packSimpleTitle(title):
    return FormattableField(FORMATTER_IDS.SIMPLE_TITLE, (i18n.makeString(title),))


def packText(label):
    return {'text': label}


def intersperse(sequence, item):
    result = []
    for element in sequence:
        result.append(element)
        result.append(item)

    if result:
        result.pop()
    return result


def getSeparator(groupType=GROUP_TYPE.AND):
    return i18n.makeString('#quests:details/groups/or') if groupType == GROUP_TYPE.OR else ''


def getSeparatorBlock(groupType=GROUP_TYPE.AND):
    label = getSeparator(groupType)
    if label:
        item = packText(text_styles.standard(label))
        item.update(isSeparator=True)
        return item
    else:
        return None


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


def getFiltersLabel(labelKey, condition):
    _, fNations, fLevels, fClasses = condition.parseFilters()
    keys, kwargs = [], {}
    if fNations:
        keys.append('nation')
        kwargs['nation'] = ', '.join((i18n.makeString('#menu:nations/%s' % nations.NAMES[idx]) for idx in fNations))
    if fClasses:
        keys.append('type')
        kwargs['type'] = ', '.join([ i18n.makeString('#menu:classes/%s' % name) for name in fClasses ])
    if fLevels:
        keys.append('level')
        kwargs['level'] = ', '.join([ int2roman(lvl) for lvl in fLevels ])
    labelKey = '%s/%s' % (labelKey, '_'.join(keys))
    if condition.relationValue is None and condition.isNegative:
        labelKey = '%s/not' % labelKey
    return i18n.makeString(labelKey, **kwargs)


def getResultsData(condition):

    def _makeStr(i18nKey, *args, **kwargs):
        if condition.isNegative():
            i18nKey = '%s/not' % i18nKey
        return i18n.makeString(i18nKey, *args, **kwargs)

    key = ''
    if condition.keyName:
        key = i18n.makeString('#quests:details/conditions/cumulative/%s' % condition.keyName)
    else:
        labels = [ i18n.makeString('#quests:details/conditions/cumulative/%s' % key) for key in condition.getAggregatedKeys() ]
        aggregated = '\n'.join(labels)
        if aggregated:
            key = '\n'.join([i18n.makeString(QUESTS.DETAILS_CONDITIONS_CUMULATIVE_AGGREGATED), aggregated])
    labelKey = '#quests:details/conditions/results'
    topRangeUpper, topRangeLower = condition.getMaxRange()
    if topRangeLower < TOP_RANGE_LOWEST:
        labelKey = '%s/%s/%s' % (labelKey, condition.localeKey, 'bothTeams' if condition.isTotal() else 'halfTeam')
        if topRangeUpper == TOP_RANGE_HIGHEST:
            label = _makeStr('%s/top' % labelKey, param=key, count=topRangeLower)
        elif topRangeLower == topRangeUpper:
            label = _makeStr('%s/position' % labelKey, param=key, position=topRangeUpper)
        else:
            label = _makeStr('%s/range' % labelKey, param=key, high=topRangeUpper, low=topRangeLower)
    elif condition.isAvg():
        label = i18n.makeString('#quests:details/conditions/results/%s/avg' % condition.localeKey, param=key)
    else:
        label = i18n.makeString('#quests:details/conditions/results/%s/simple' % condition.localeKey, param=key)
    value, relation, relationI18nType = condition.relationValue, condition.relation, RELATIONS_SCHEME.DEFAULT
    if condition.keyName == 'markOfMastery':
        relationI18nType = RELATIONS_SCHEME.ALTERNATIVE
        if condition.relationValue == 0:
            if condition.relation in (RELATIONS.EQ, RELATIONS.LSQ):
                i18nLabelKey = '#quests:details/conditions/cumulative/markOfMastery0'
            else:
                if condition.relation in (RELATIONS.LS,):
                    raise SoftException('Mark of mastery 0 can be used with greater or equal relation types')
                i18nLabelKey = '#quests:details/conditions/cumulative/markOfMastery0/not'
            label, value, relation = i18n.makeString(i18nLabelKey), None, None
        else:
            i18nValueKey = '#quests:details/conditions/cumulative/markOfMastery%d' % int(condition.relationValue)
            i18nLabel = i18n.makeString('#quests:details/conditions/cumulative/markOfMastery')
            label, value, relation = i18nLabel, i18n.makeString(i18nValueKey), condition.relation
    return (label,
     relation,
     relationI18nType,
     value)


def _get128CondIcon(iconKey):
    return RES_ICONS.get128ConditionIcon(iconKey)


def _get90CondIcon(iconKey):
    return RES_ICONS.get90ConditionIcon(iconKey)


def getCondIconBySize(size, iconKey):
    return _get128CondIcon(iconKey) if size == CONDITION_SIZE.NORMAL else _get90CondIcon(iconKey)
