# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileUtils.py
import BigWorld
from debug_utils import LOG_ERROR
from gui.shared.formatters import text_styles
from helpers import i18n
from gui.shared import g_itemsCache
from gui.shared.gui_items.dossier.stats import _MaxVehicleStatsBlock, _FalloutStatsBlock, _VehiclesStatsBlock
from gui.Scaleform.locale.PROFILE import PROFILE

def _emptyField(targetData, isCurrentUser):
    return None


class _AbstractField(object):

    def __init__(self, label, tooltip):
        super(_AbstractField, self).__init__()
        self._label = label
        self._tooltip = tooltip

    def __call__(self, targetData, isCurrentUser):
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), self._tooltip, self._buildTooltipData(targetData, isCurrentUser))

    def isVisible(self, targetData, isCurrentUser):
        return True

    def _buildData(self, targetData, isCurrentUser):
        return None

    def _buildTooltipData(self, targetData, isCurrentUser):
        return None


class _OnlyAccountField(_AbstractField):

    def isVisible(self, targetData, isCurrentUser):
        return isinstance(targetData, _VehiclesStatsBlock)


class _BattlesCountField(_AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return BigWorld.wg_getIntegralFormat(targetData.getBattlesCount())

    def _buildTooltipData(self, targetData, isCurrentUser):
        lossesCount = targetData.getLossesCount()
        winsCount = targetData.getWinsCount()
        drawsCount = targetData.getDrawsCount()
        drawsStr = BigWorld.wg_getIntegralFormat(drawsCount) if drawsCount >= 0 else ProfileUtils.UNAVAILABLE_SYMBOL
        return ProfileUtils.createToolTipData((BigWorld.wg_getIntegralFormat(winsCount), BigWorld.wg_getIntegralFormat(lossesCount), drawsStr))


class _WinsEfficiencyField(_AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return ProfileUtils.formatFloatPercent(ProfileUtils.getValueOrUnavailable(targetData.getWinsEfficiency()))


class _WinsField(_AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return BigWorld.wg_getIntegralFormat(targetData.getWinsCount())


class _SurvivalField(_AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return ProfileUtils.formatFloatPercent(ProfileUtils.getValueOrUnavailable(targetData.getSurvivalEfficiency()))


class _HitsField(_AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return ProfileUtils.formatFloatPercent(ProfileUtils.getValueOrUnavailable(targetData.getHitsEfficiency()))


class _DamageCoefficientField(_AbstractField):

    def __call__(self, targetData, isCurrentUser):
        tooltip = self._tooltip
        if isinstance(targetData, _FalloutStatsBlock):
            if not isinstance(targetData, _VehiclesStatsBlock):
                tooltip += '/vehicle'
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), tooltip, self._buildTooltipData(targetData, isCurrentUser))

    def _buildData(self, targetData, isCurrentUser):
        return ProfileUtils.formatEfficiency(targetData.getDamageReceived(), targetData.getDamageEfficiency)

    def _buildTooltipData(self, targetData, isCurrentUser):
        damageToolTipData = [BigWorld.wg_getIntegralFormat(targetData.getDamageDealt()), BigWorld.wg_getIntegralFormat(targetData.getDamageReceived())]
        if isinstance(targetData, _FalloutStatsBlock):
            if isinstance(targetData, _VehiclesStatsBlock):
                damageToolTipData.append(BigWorld.wg_getIntegralFormat(targetData.getConsumablesDamageDealt()))
        return ProfileUtils.createToolTipData(damageToolTipData)


class _DestructionCoefficientField(_AbstractField):

    def __call__(self, targetData, isCurrentUser):
        tooltip = self._tooltip
        if isinstance(targetData, _FalloutStatsBlock):
            if not isinstance(targetData, _VehiclesStatsBlock):
                tooltip += '/vehicle'
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), tooltip, self._buildTooltipData(targetData, isCurrentUser))

    def _buildData(self, targetData, isCurrentUser):
        return ProfileUtils.formatEfficiency(targetData.getDeathsCount(), targetData.getFragsEfficiency)

    def _buildTooltipData(self, targetData, isCurrentUser):
        destructionToolTipData = [BigWorld.wg_getIntegralFormat(targetData.getFragsCount()), BigWorld.wg_getIntegralFormat(targetData.getDeathsCount())]
        if isinstance(targetData, _FalloutStatsBlock):
            if isinstance(targetData, _VehiclesStatsBlock):
                destructionToolTipData.append(BigWorld.wg_getIntegralFormat(targetData.getConsumablesFragsCount()))
        return ProfileUtils.createToolTipData(destructionToolTipData)


class _ArmorusingField(_AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        damageBlockedByArmor = targetData.getDamageBlockedByArmor()
        potentialDamageReceived = targetData.getPotentialDamageReceived()
        pResDmg = potentialDamageReceived - damageBlockedByArmor
        return ProfileUtils.formatEfficiency(pResDmg, targetData.getArmorUsingEfficiency)

    def _buildTooltipData(self, targetData, isCurrentUser):
        return ProfileUtils.createToolTipData((ProfileUtils.getAvgDamageBlockedValue(targetData),))


def _avgExpField(targetData, isCurrentUser):
    formatedExp = BigWorld.wg_getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgXP()))
    return DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_AVGEXPERIENCE_SHORT, formatedExp, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGEX_SHORT)


class _AvgDmgField(_AbstractField):

    def __call__(self, targetData, isCurrentUser):
        tooltip = self._tooltip
        if isinstance(targetData, _FalloutStatsBlock):
            if not isinstance(targetData, _VehiclesStatsBlock):
                tooltip += '/vehicle'
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), tooltip, None)

    def _buildData(self, targetData, isCurrentUser):
        return BigWorld.wg_getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgDamage()))


class _AvgReceivedDmgField(_AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return BigWorld.wg_getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgDamageReceived()))


def _avgAssignedDmgField(targetData, isCurrentUser):
    formatedAssignedDmg = ProfileUtils.formatEfficiency(targetData.getBattlesCountVer2(), targetData.getDamageAssistedEfficiency)
    return DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_AVGASSISTEDDAMAGE_SHORTSELF if isCurrentUser else PROFILE.SECTION_STATISTICS_SCORES_AVGASSISTEDDAMAGE_SHORTOTHER, formatedAssignedDmg, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDDAMAGE_SHORTSELF if isCurrentUser else PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDDAMAGE_SHORTOTHER)


def _avgDetectedField(targetData, isCurrentUser):
    formatedDetected = BigWorld.wg_getNiceNumberFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgEnemiesSpotted()))
    return DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_DETAILED_AVGDETECTEDENEMIES, formatedDetected, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDETECTEDENEMIES)


class _AvgDestroyedField(_AbstractField):

    def __call__(self, targetData, isCurrentUser):
        tooltip = self._tooltip
        if isinstance(targetData, _FalloutStatsBlock):
            if not isinstance(targetData, _VehiclesStatsBlock):
                tooltip += '/vehicle'
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), tooltip, None)

    def _buildData(self, targetData, isCurrentUser):
        return BigWorld.wg_getNiceNumberFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgFrags()))


def _maxXPField(targetData, isCurrentUser):
    formatedMaxXP = BigWorld.wg_getIntegralFormat(targetData.getMaxXp())
    maxXpVehicle = None
    if isinstance(targetData, _MaxVehicleStatsBlock):
        maxXpVehicle = g_itemsCache.items.getItemByCD(targetData.getMaxXpVehicle())
    return DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_MAXEXPERIENCE, formatedMaxXP, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEXP, ProfileUtils.getRecordTooltipDataByVehicle(maxXpVehicle))


class _MaxDamageField(_AbstractField):

    def __init__(self, label, tooltip, unavailableTooltip):
        super(_MaxDamageField, self).__init__(label, tooltip)
        self._unavailableTooltip = unavailableTooltip

    def __call__(self, targetData, isCurrentUser):
        tooltip = self._unavailableTooltip
        tooltipData = None
        if targetData.getBattlesCountVer3() > 0:
            tooltip = self._tooltip
            if isinstance(targetData, _MaxVehicleStatsBlock):
                tooltipData = self._buildTooltipData(targetData, isCurrentUser)
            elif isinstance(targetData, _FalloutStatsBlock):
                if not isinstance(targetData, _VehiclesStatsBlock):
                    tooltip = self._tooltip + '/vehicle'
            else:
                tooltipData = ProfileUtils.createToolTipData(None)
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), tooltip, tooltipData)

    def _buildData(self, targetData, isCurrentUser):
        if targetData.getBattlesCountVer3() > 0:
            return BigWorld.wg_getIntegralFormat(targetData.getMaxDamage())
        return ProfileUtils.UNAVAILABLE_VALUE

    def _buildTooltipData(self, targetData, isCurrentUser):
        maxDamageVehicle = g_itemsCache.items.getItemByCD(targetData.getMaxDamageVehicle())
        return ProfileUtils.getRecordTooltipDataByVehicle(maxDamageVehicle)


class _MaxDestroyedField(_AbstractField):

    def __call__(self, targetData, isCurrentUser):
        tooltip = self._tooltip
        tooltipData = None
        if isinstance(targetData, _MaxVehicleStatsBlock):
            tooltipData = self._buildTooltipData(targetData, isCurrentUser)
        elif isinstance(targetData, _FalloutStatsBlock):
            if not isinstance(targetData, _VehiclesStatsBlock):
                tooltip = self._tooltip + '/vehicle'
        else:
            tooltipData = ProfileUtils.createToolTipData(None)
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), tooltip, tooltipData)

    def _buildData(self, targetData, isCurrentUser):
        return BigWorld.wg_getIntegralFormat(targetData.getMaxFrags())

    def _buildTooltipData(self, targetData, isCurrentUser):
        maxFragsVehicle = g_itemsCache.items.getItemByCD(targetData.getMaxFragsVehicle())
        return ProfileUtils.getRecordTooltipDataByVehicle(maxFragsVehicle)


class _CapturePointsField(_OnlyAccountField):

    def _buildData(self, targetData, isCurrentUser):
        return BigWorld.wg_getIntegralFormat(targetData.getCapturePoints())


class _DroppedPointsField(_OnlyAccountField):

    def _buildData(self, targetData, isCurrentUser):
        return BigWorld.wg_getIntegralFormat(targetData.getDroppedCapturePoints())


class _TotalVehiclesField(_OnlyAccountField):

    def _buildData(self, targetData, isCurrentUser):
        return BigWorld.wg_getIntegralFormat(targetData.getTotalVehicles())


def _totalVehiclesField(targetData, isCurrentUser):
    formattedVehicles = BigWorld.wg_getIntegralFormat(targetData.getTotalVehicles())
    return DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_TOTALVEHS, formattedVehicles, PROFILE.PROFILE_PARAMS_TOOLTIP_TOTALVEHS)


def _flagsDeliveredField(targetData, isCurrentUser):
    formattedDelivered = BigWorld.wg_getIntegralFormat(targetData.getFlagsDelivered())
    return DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FLAGSDELIVERED, formattedDelivered, PROFILE.PROFILE_PARAMS_TOOLTIP_FLAGSDELIVERED)


def _flagsAbsorbedField(targetData, isCurrentUser):
    formattedAbsorbed = BigWorld.wg_getIntegralFormat(targetData.getFlagsAbsorbed())
    return DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_FLAGSABSORBED, formattedAbsorbed, PROFILE.PROFILE_PARAMS_TOOLTIP_FLAGSABSORBED)


def _maxWinPointsField(targetData, isCurrentUser):
    formatedMaxWP = BigWorld.wg_getIntegralFormat(targetData.getMaxVictoryPoints())
    return DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_MAXVICTORYPOINTS, formatedMaxWP, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXVICTORYPOINTS)


COMMON_SECTION_FIELDS = (_BattlesCountField(PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
 _WinsEfficiencyField(PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS),
 _SurvivalField(PROFILE.SECTION_STATISTICS_SCORES_SURVIVAL, PROFILE.PROFILE_PARAMS_TOOLTIP_SURVIVAL),
 _HitsField(PROFILE.SECTION_STATISTICS_SCORES_HITS, PROFILE.PROFILE_PARAMS_TOOLTIP_HITS),
 _emptyField,
 _DamageCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DAMAGECOEFF),
 _DestructionCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DESTRUCTIONCOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DESTROYCOEFF),
 _ArmorusingField(PROFILE.SECTION_STATISTICS_SCORES_ARMORUSING, PROFILE.PROFILE_PARAMS_TOOLTIP_ARMORUSING),
 _CapturePointsField(PROFILE.SECTION_STATISTICS_SCORES_CAPTUREPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_CAPTUREPOINTS),
 _DroppedPointsField(PROFILE.SECTION_STATISTICS_SCORES_DROPPEDCAPTUREPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_DROPPEDCAPTUREPOINTS))
COMMON_SECTION_FORT_FIELDS = (_BattlesCountField(PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FORT_BATTLESCOUNT),
 _WinsEfficiencyField(PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS),
 _SurvivalField(PROFILE.SECTION_STATISTICS_SCORES_SURVIVAL, PROFILE.PROFILE_PARAMS_TOOLTIP_SURVIVAL),
 _HitsField(PROFILE.SECTION_STATISTICS_SCORES_HITS, PROFILE.PROFILE_PARAMS_TOOLTIP_HITS),
 _emptyField,
 _DamageCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DAMAGECOEFF),
 _DestructionCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DESTRUCTIONCOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DESTROYCOEFF),
 _ArmorusingField(PROFILE.SECTION_STATISTICS_SCORES_ARMORUSING, PROFILE.PROFILE_PARAMS_TOOLTIP_ARMORUSING))
COMMON_SECTION_FALLOUT_FIELDS = (_BattlesCountField(PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_BATTLESCOUNT),
 _WinsField(PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_WINS),
 _HitsField(PROFILE.SECTION_STATISTICS_SCORES_HITS, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_HITS),
 _DamageCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_DAMAGECOEFF),
 _DestructionCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DESTRUCTIONCOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_DESTROYCOEFF),
 _ArmorusingField(PROFILE.SECTION_STATISTICS_SCORES_ARMORUSING, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_ARMORUSING),
 _TotalVehiclesField(PROFILE.SECTION_STATISTICS_SCORES_TOTALVEHS, PROFILE.PROFILE_PARAMS_TOOLTIP_TOTALVEHS),
 _emptyField,
 _flagsDeliveredField,
 _flagsAbsorbedField)
AVERAGE_SECTION_FIELDS = (_avgExpField,
 _emptyField,
 _AvgDmgField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDMG_SHORT),
 _AvgReceivedDmgField(PROFILE.SECTION_STATISTICS_DETAILED_AVGRECEIVEDDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGRECEIVEDDAMAGE),
 _avgAssignedDmgField,
 _emptyField,
 _avgDetectedField,
 _AvgDestroyedField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDESTROYEDVEHICLES, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDESTROYEDVEHICLES))
AVERAGE_SECTION_FALLOUT_FIELDS = (_avgExpField,
 _emptyField,
 _AvgDmgField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_AVGDMG_SHORT),
 _AvgReceivedDmgField(PROFILE.SECTION_STATISTICS_DETAILED_AVGRECEIVEDDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_AVGRECEIVEDDAMAGE),
 _emptyField,
 _AvgDestroyedField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDESTROYEDVEHICLES, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_AVGDESTROYEDVEHICLES))
RECORD_SECTION_FIELDS = (_maxXPField, _MaxDamageField(PROFILE.SECTION_STATISTICS_SCORES_MAXDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLEMAXDAMAGE), _MaxDestroyedField(PROFILE.SECTION_STATISTICS_DETAILED_MAXDESTROYEDVEHICLES, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXDESTROYED))
RECORD_SECTION_FALLOUT_FIELDS = (_maxXPField,
 _MaxDamageField(PROFILE.SECTION_STATISTICS_SCORES_MAXDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_MAXDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLEMAXDAMAGE),
 _MaxDestroyedField(PROFILE.SECTION_STATISTICS_DETAILED_MAXDESTROYEDVEHICLES, PROFILE.PROFILE_PARAMS_TOOLTIP_DIF_FALLOUT_MAXDESTROYED),
 _maxWinPointsField)
STATISTICS_LAYOUT = ((PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_COMMON, COMMON_SECTION_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_AVERAGE, AVERAGE_SECTION_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_RECORD, RECORD_SECTION_FIELDS))
FORT_STATISTICS_LAYOUT = ((PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_COMMON, COMMON_SECTION_FORT_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_AVERAGE, AVERAGE_SECTION_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_RECORD, RECORD_SECTION_FIELDS))
FALLOUT_STATISTICS_LAYOUT = ((PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_COMMON, COMMON_SECTION_FALLOUT_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_AVERAGE, AVERAGE_SECTION_FALLOUT_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_RECORD, RECORD_SECTION_FALLOUT_FIELDS))

class HeaderItemsTypes(object):
    VALUE_PREFIX = 'value_'
    COMMON = 'common'
    RATIO = 'ratio'
    VALUES = 'values'


class ProfileUtils(object):
    UNAVAILABLE_VALUE = -1
    UNAVAILABLE_SYMBOL = '--'
    PERCENT_SYMBOL = '%'
    VIEW_TYPE_TABLES = 0
    VIEW_TYPE_CHARTS = 1
    VIEW_TYPE_TABLE = 2

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
    def getIconPath(icon):
        return '../maps/icons/library/dossier/' + icon

    @staticmethod
    def formatFloatPercent(value):
        if value != ProfileUtils.UNAVAILABLE_VALUE:
            value = value * 100
            value = BigWorld.wg_getNiceNumberFormat(value) + '%'
        return str(value)

    @staticmethod
    def getFormattedWinsEfficiency(targetData):
        winsEfficiency = targetData.getWinsEfficiency()
        formattedWinsEfficiency = ProfileUtils.formatFloatPercent(ProfileUtils.getValueOrUnavailable(winsEfficiency))
        return formattedWinsEfficiency

    @staticmethod
    def formatEfficiency(coeff2, valueReceiveFunction):
        if coeff2 > 0:
            return BigWorld.wg_getNiceNumberFormat(valueReceiveFunction())
        else:
            return ProfileUtils.UNAVAILABLE_VALUE

    @staticmethod
    def getEfficiencyPercent(dividend, delimiter):
        if delimiter != 0:
            return BigWorld.wg_getNiceNumberFormat(float(dividend) / delimiter * 100) + ProfileUtils.PERCENT_SYMBOL
        else:
            return ProfileUtils.UNAVAILABLE_VALUE

    @staticmethod
    def packLditItemData(text, description, tooltip, icon, tooltipData = None):
        finalText = text
        enabled = True
        if text == -1 or text == '-1':
            enabled = False
            finalText = ProfileUtils.UNAVAILABLE_SYMBOL
        return {'text': finalText,
         'description': i18n.makeString(description),
         'iconPath': ProfileUtils.getIconPath(icon),
         'tooltip': tooltip,
         'tooltipData': tooltipData,
         'enabled': enabled}

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
        if viewType != ProfileUtils.VIEW_TYPE_TABLES and viewType != ProfileUtils.VIEW_TYPE_CHARTS and viewType != ProfileUtils.VIEW_TYPE_TABLE:
            LOG_ERROR('Unknown view type', viewType)
            return None
        else:
            result = ProfileUtils.getLabelDataObject(label, data)
            result['viewType'] = viewType
            if viewType == ProfileUtils.VIEW_TYPE_TABLES:
                result['linkage'] = 'DetailedStatisticsView_UI'
            elif viewType == ProfileUtils.VIEW_TYPE_CHARTS:
                result['linkage'] = 'ChartsStatisticsView_UI'
            elif viewType == ProfileUtils.VIEW_TYPE_TABLE:
                result['linkage'] = 'ClanProfileTableStatisticsViewUI'
            return result

    @staticmethod
    def createToolTipData(bodyParamsList):
        result = {}
        bodyData = None
        if bodyParamsList is not None:
            bodyData = {}
            for i in range(0, len(bodyParamsList)):
                bodyData[HeaderItemsTypes.VALUE_PREFIX + str(i)] = text_styles.titleFont(str(bodyParamsList[i]))

        result['body'] = bodyData
        result['header'] = {}
        result['note'] = None
        return result

    @staticmethod
    def getTotalBattlesHeaderParam(targetData, description, tooltip):
        battlesCount = targetData.getBattlesCount()
        lossesCount = targetData.getLossesCount()
        winsCount = targetData.getWinsCount()
        drawsCount = targetData.getDrawsCount()
        drawsStr = BigWorld.wg_getIntegralFormat(drawsCount) if drawsCount >= 0 else ProfileUtils.UNAVAILABLE_SYMBOL
        battlesToolTipData = (BigWorld.wg_getIntegralFormat(winsCount), BigWorld.wg_getIntegralFormat(lossesCount), drawsStr)
        return ProfileUtils.packLditItemData(BigWorld.wg_getIntegralFormat(battlesCount), description, tooltip, 'battles40x32.png', ProfileUtils.createToolTipData(battlesToolTipData))

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
    def getAvailableValueStr(value):
        if value != -1:
            return value
        return ProfileUtils.UNAVAILABLE_SYMBOL

    @staticmethod
    def getAvgDamageBlockedValue(targetData):
        value = ProfileUtils.formatEfficiency(targetData.getBattlesCountVer3(), targetData.getAvgDamageBlocked)
        return ProfileUtils.getAvailableValueStr(value)


class DetailedStatisticsUtils(object):

    @staticmethod
    def getDetailedDataObject(label, value, tooltip, tooltipData = None):
        dataObject = ProfileUtils.getLabelDataObject(label, value)
        dataObject['tooltip'] = tooltip
        dataObject['tooltipData'] = tooltipData
        return dataObject

    @staticmethod
    def getStatistics(targetData, isCurrentUser, layout):
        result = []
        for section, fields in layout:
            sectionFields = []
            for field in fields:
                if not isinstance(field, _AbstractField) or field.isVisible(targetData, isCurrentUser):
                    sectionFields.append(field(targetData, isCurrentUser))

            result.append(ProfileUtils.getLabelDataObject(section, sectionFields))

        return result


def getProfileCommonInfo(userName, dossier):
    lastBattleTimeUserString = None
    if dossier['total']['lastBattleTime']:
        lbt = dossier['total']['lastBattleTime']
        lastBattleTimeUserString = '%s %s' % (BigWorld.wg_getLongDateFormat(lbt), BigWorld.wg_getShortTimeFormat(lbt))
    return {'name': userName,
     'registrationDate': '%s' % BigWorld.wg_getLongDateFormat(dossier['total']['creationTime']),
     'lastBattleDate': lastBattleTimeUserString}
