# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileUtils.py
import cPickle as pickle
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR
from constants import CLAN_MEMBER_FLAGS
from helpers import i18n
from dossiers2.custom.config import RECORD_CONFIGS
from dossiers2.ui.achievements import ACHIEVEMENT_SECTION, ACHIEVEMENT_TYPE
from gui.shared import g_itemsCache
from gui.shared.gui_items.dossier import dumpDossier
from gui.shared.gui_items.dossier.achievements import RareAchievement
from gui.shared.gui_items.dossier.stats import _MaxVehicleStatsBlock
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.Scaleform.locale.MENU import MENU
from helpers.i18n import makeString
CLAN_MEMBERS = {CLAN_MEMBER_FLAGS.LEADER: 'leader',
 CLAN_MEMBER_FLAGS.VICE_LEADER: 'vice_leader',
 CLAN_MEMBER_FLAGS.RECRUITER: 'recruiter',
 CLAN_MEMBER_FLAGS.TREASURER: 'treasurer',
 CLAN_MEMBER_FLAGS.DIPLOMAT: 'diplomat',
 CLAN_MEMBER_FLAGS.COMMANDER: 'commander',
 CLAN_MEMBER_FLAGS.PRIVATE: 'private',
 CLAN_MEMBER_FLAGS.RECRUIT: 'recruit'}

class HeaderItemsTypes(object):
    VALUE_PREFIX = 'value_'
    COMMON = 'common'
    RATIO = 'ratio'
    VALUES = 'values'


class ProfileUtils(object):
    UNAVAILABLE_VALUE = -1
    VIEW_TYPE_TABLES = 0
    VIEW_TYPE_CHARTS = 1

    def __init__(self):
        super(ProfileUtils, self).__init__()

    @staticmethod
    def packProfileDossierInfo(targetData):
        outcome = ProfileUtils.packProfileCommonInfo(targetData)
        vehicle = g_itemsCache.items.getItemByCD(targetData.getMaxXpVehicle())
        outcome['maxXPByVehicle'] = vehicle.shortUserName if vehicle is not None else ''
        outcome['marksOfMastery'] = targetData.getMarksOfMastery()[3]
        outcome['totalUserVehiclesCount'] = len(targetData.getVehicles())
        return outcome

    @staticmethod
    def packProfileCommonInfo(targetData):
        outcome = {}
        outcome['battlesCount'] = targetData.getBattlesCount()
        outcome['lossesCount'] = targetData.getLossesCount()
        outcome['winsCount'] = targetData.getWinsCount()
        outcome['hitsEfficiency'] = ProfileUtils.getValueOrUnavailable(targetData.getHitsEfficiency())
        outcome['maxXP'] = targetData.getMaxXp()
        outcome['avgXP'] = ProfileUtils.getValueOrUnavailable(targetData.getAvgXP())
        return outcome

    @staticmethod
    def packAchievementList(target, dossier, isDossierForCurrentUser):
        return [ ProfileUtils.packAchievement(a, dossier, isDossierForCurrentUser) for a in target ]

    @staticmethod
    def packAchievement(achievement, dossier, isDossierForCurrentUser):
        isRare = isinstance(achievement, RareAchievement)
        rareIconID = None
        if isRare:
            rareIconID = achievement.requestImageID()
        atype = achievement.getType()
        section = achievement.getSection()
        icons = achievement.getIcons()
        minRecordValue = -1
        if atype == ACHIEVEMENT_TYPE.SERIES and section == ACHIEVEMENT_SECTION.SPECIAL:
            minRecordValue = RECORD_CONFIGS.get(achievement.getName())
        return {'name': str(achievement.getName()),
         'block': achievement.getBlock(),
         'value': achievement.getValue(),
         'localizedValue': achievement.getI18nValue(),
         'section': section,
         'type': atype,
         'dossierCompDescr': dumpDossier(dossier),
         'rareIconId': rareIconID,
         'isRare': isRare,
         'isDone': achievement.isDone(),
         'lvlUpTotalValue': achievement.getLevelUpTotalValue(),
         'lvlUpValue': achievement.getLevelUpValue(),
         'isDossierForCurrentUser': isDossierForCurrentUser,
         'description': achievement.getUserDescription(),
         'userName': achievement.getUserName(),
         'icon': {'big': icons['180x180'],
                  'small': icons['67x71']},
         'dossierType': dossier.getDossierType(),
         'isInDossier': achievement.isInDossier(),
         'minValueForRecord': minRecordValue,
         'hasCounter': achievement.hasCounter()}

    @staticmethod
    def getIconPath(icon):
        return '../maps/icons/library/dossier/' + icon

    @staticmethod
    def formatFloatPercent(value):
        if value != ProfileUtils.UNAVAILABLE_VALUE:
            value = value * 100
            value = BigWorld.wg_getNiceNumberFormat(value) + '%'
        return str(value)

    @staticmethod
    def formatEfficiency(coeff2, valueReceiveFunction):
        if coeff2 > 0:
            return BigWorld.wg_getNiceNumberFormat(valueReceiveFunction())
        else:
            return ProfileUtils.UNAVAILABLE_VALUE

    @staticmethod
    def packLditItemData(text, description, tooltip, icon, additionalData = None, viewType = HeaderItemsTypes.COMMON):
        return {'type': viewType,
         'text': text,
         'description': i18n.makeString(description),
         'iconPath': ProfileUtils.getIconPath(icon),
         'tooltip': tooltip,
         'additionalData': additionalData}

    @staticmethod
    def getValueOrUnavailable(targetValue):
        if targetValue is not None:
            return targetValue
        else:
            return ProfileUtils.UNAVAILABLE_VALUE

    @staticmethod
    def getLabelDataObject(label, data):
        return {'label': i18n.makeString(label),
         'data': data}

    @staticmethod
    def getLabelViewTypeDataObject(label, data, viewType):
        if viewType != ProfileUtils.VIEW_TYPE_TABLES and viewType != ProfileUtils.VIEW_TYPE_CHARTS:
            LOG_ERROR('Unknown view type', viewType)
            return None
        else:
            result = ProfileUtils.getLabelDataObject(label, data)
            result['viewType'] = viewType
            return result

    @staticmethod
    def createToolTipData(bodyParamsList):
        result = {}
        bodyData = None
        if bodyParamsList is not None:
            bodyData = {}
            for i in range(0, len(bodyParamsList)):
                bodyData[HeaderItemsTypes.VALUE_PREFIX + str(i)] = '<b>' + str(bodyParamsList[i]) + '</b>'

        result['body'] = bodyData
        result['header'] = {}
        result['note'] = None
        return result

    @staticmethod
    def getVehicleRecordTooltipData(getValueMethod):
        return ProfileUtils.getRecordTooltipDataByVehicle(g_itemsCache.items.getItemByCD(getValueMethod()))

    @staticmethod
    def getRecordTooltipDataByVehicle(vehicle):
        if vehicle is not None:
            return ProfileUtils.createToolTipData([vehicle.shortUserName])
        else:
            return ProfileUtils.createToolTipData(None)

    @staticmethod
    def getAvgDamageBlockedValue(targetData):
        value = ProfileUtils.formatEfficiency(targetData.getBattlesCountVer3(), targetData.getAvgDamageBlocked)
        if value != -1:
            return value
        return '--'


class DetailedStatisticsUtils(object):

    @staticmethod
    def getDetailedDataObject(label, value, tooltip, tooltipData = None):
        dataObject = ProfileUtils.getLabelDataObject(label, value)
        dataObject['tooltip'] = tooltip
        dataObject['tooltipData'] = tooltipData
        return dataObject

    @staticmethod
    def getStatistics(targetData):
        battlesCount = targetData.getBattlesCount()
        lossesCount = targetData.getLossesCount()
        winsCount = targetData.getWinsCount()
        drawsCount = battlesCount - (winsCount + lossesCount)
        battlesToolTipData = [BigWorld.wg_getIntegralFormat(winsCount), BigWorld.wg_getIntegralFormat(lossesCount), BigWorld.wg_getIntegralFormat(drawsCount)]
        formattedBattlesCount = BigWorld.wg_getIntegralFormat(battlesCount)
        winsEfficiency = targetData.getWinsEfficiency()
        formattedWinsEfficiency = ProfileUtils.formatFloatPercent(ProfileUtils.getValueOrUnavailable(winsEfficiency))
        dmgDealt = targetData.getDamageDealt()
        dmgReceived = targetData.getDamageReceived()
        damageBlockedByArmor = targetData.getDamageBlockedByArmor()
        potentialDamageReceived = targetData.getPotentialDamageReceived()
        pResDmg = potentialDamageReceived - damageBlockedByArmor
        avgXP = ProfileUtils.getValueOrUnavailable(targetData.getAvgXP())
        avgDmg = ProfileUtils.getValueOrUnavailable(targetData.getAvgDamage())
        maxXP = targetData.getMaxXp()
        maxXP_formattedStr = BigWorld.wg_getIntegralFormat(maxXP)
        maxXpVehicle = None
        maxDamageVehicle = None
        maxFragsVehicle = None
        if isinstance(targetData, _MaxVehicleStatsBlock):
            maxXpVehicle = g_itemsCache.items.getItemByCD(targetData.getMaxXpVehicle())
            maxDamageVehicle = g_itemsCache.items.getItemByCD(targetData.getMaxDamageVehicle())
            maxFragsVehicle = g_itemsCache.items.getItemByCD(targetData.getMaxFragsVehicle())
        maxExpToolTipData = ProfileUtils.getRecordTooltipDataByVehicle(maxXpVehicle)
        maxDestroyedToolTipData = ProfileUtils.getRecordTooltipDataByVehicle(maxFragsVehicle)
        maxDmg = targetData.getMaxDamage()
        maxDamageToolTipData = None
        if targetData.getBattlesCountVer3() > 0:
            maxDmg_formattedStr = BigWorld.wg_getIntegralFormat(maxDmg)
            maxDamageToolTipData = ProfileUtils.getRecordTooltipDataByVehicle(maxDamageVehicle)
            maxDamageTooltip = PROFILE.PROFILE_PARAMS_TOOLTIP_MAXDAMAGE
        else:
            maxDmg_formattedStr = ProfileUtils.UNAVAILABLE_VALUE
            maxDamageTooltip = PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLEMAXDAMAGE
        return (ProfileUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_COMMON, [DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, formattedBattlesCount, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT, ProfileUtils.createToolTipData(battlesToolTipData)),
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, formattedWinsEfficiency, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS),
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_SURVIVAL, ProfileUtils.formatFloatPercent(ProfileUtils.getValueOrUnavailable(targetData.getSurvivalEfficiency())), PROFILE.PROFILE_PARAMS_TOOLTIP_SURVIVAL),
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_HITS, ProfileUtils.formatFloatPercent(ProfileUtils.getValueOrUnavailable(targetData.getHitsEfficiency())), PROFILE.PROFILE_PARAMS_TOOLTIP_HITS),
          None,
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_DETAILED_DAMAGECOEFFICIENT, ProfileUtils.formatEfficiency(dmgReceived, targetData.getDamageEfficiency), PROFILE.PROFILE_PARAMS_TOOLTIP_DAMAGECOEFF, ProfileUtils.createToolTipData((BigWorld.wg_getIntegralFormat(dmgDealt), BigWorld.wg_getIntegralFormat(dmgReceived)))),
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_DETAILED_DESTRUCTIONCOEFFICIENT, ProfileUtils.formatEfficiency(targetData.getDeathsCount(), targetData.getFragsEfficiency), PROFILE.PROFILE_PARAMS_TOOLTIP_DESTROYCOEFF, ProfileUtils.createToolTipData((BigWorld.wg_getIntegralFormat(targetData.getFragsCount()), BigWorld.wg_getIntegralFormat(targetData.getDeathsCount())))),
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_ARMORUSING, ProfileUtils.formatEfficiency(pResDmg, targetData.getArmorUsingEfficiency), PROFILE.PROFILE_PARAMS_TOOLTIP_ARMORUSING, ProfileUtils.createToolTipData([ProfileUtils.getAvgDamageBlockedValue(targetData)]))]), ProfileUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_AVERAGE, [DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_AVGEXPERIENCE_SHORT, BigWorld.wg_getIntegralFormat(avgXP), PROFILE.PROFILE_PARAMS_TOOLTIP_AVGEX_SHORT),
          None,
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_DETAILED_AVGDAMAGE, BigWorld.wg_getIntegralFormat(avgDmg), PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDMG_SHORT),
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_DETAILED_AVGRECEIVEDDAMAGE, BigWorld.wg_getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgDamageReceived())), PROFILE.PROFILE_PARAMS_TOOLTIP_AVGRECEIVEDDAMAGE),
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_AVGASSISTEDDAMAGE_SHORT, ProfileUtils.formatEfficiency(targetData.getBattlesCountVer2(), targetData.getDamageAssistedEfficiency), PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDDAMAGE_SHORT),
          None,
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_DETAILED_AVGDETECTEDENEMIES, BigWorld.wg_getNiceNumberFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgEnemiesSpotted())), PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDETECTEDENEMIES),
          DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_DETAILED_AVGDESTROYEDVEHICLES, BigWorld.wg_getNiceNumberFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgFrags())), PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDESTROYEDVEHICLES)]), ProfileUtils.getLabelDataObject(PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_RECORD, [DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_MAXEXPERIENCE, maxXP_formattedStr, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEXP, maxExpToolTipData), DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_MAXDAMAGE, maxDmg_formattedStr, maxDamageTooltip, maxDamageToolTipData), DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_DETAILED_MAXDESTROYEDVEHICLES, BigWorld.wg_getIntegralFormat(targetData.getMaxFrags()), PROFILE.PROFILE_PARAMS_TOOLTIP_MAXDESTROYED, maxDestroyedToolTipData)]))


def getProfileCommonInfo(userName, dossier, clanInfo, clanEmblemId):
    clanNameProp = 'clanName'
    clanNameDescrProp = 'clanNameDescr'
    clanJoinTimeProp = 'clanJoinTime'
    clanPositionProp = 'clanPosition'
    clanEmblemProp = 'clanEmblem'
    import cgi
    lastBattleTimeUserString = None
    if dossier['total']['lastBattleTime']:
        lbt = dossier['total']['lastBattleTime']
        lastBattleTimeUserString = '%s %s' % (BigWorld.wg_getLongDateFormat(lbt), BigWorld.wg_getShortTimeFormat(lbt))
    value = {'name': userName,
     'registrationDate': '%s' % BigWorld.wg_getLongDateFormat(dossier['total']['creationTime']),
     'lastBattleDate': lastBattleTimeUserString,
     clanNameProp: '',
     clanNameDescrProp: '',
     clanJoinTimeProp: '',
     clanPositionProp: '',
     clanEmblemProp: 'img://' + clanEmblemId if clanEmblemId is not None else None}

    def getGoldFmt(str):
        return str

    if clanInfo is not None:
        value[clanNameProp] = cgi.escape(clanInfo[1])
        value[clanNameDescrProp] = cgi.escape(clanInfo[0])
        value[clanJoinTimeProp] = makeString(MENU.PROFILE_HEADER_CLAN_JOINDATE) % getGoldFmt(BigWorld.wg_getLongDateFormat(clanInfo[4]))
        clanPosition = makeString('#menu:profile/header/clan/position/%s' % CLAN_MEMBERS[clanInfo[3]] if clanInfo[3] in CLAN_MEMBERS else '')
        value[clanPositionProp] = getGoldFmt(clanPosition) if clanInfo[3] in CLAN_MEMBERS else ''
    return value
