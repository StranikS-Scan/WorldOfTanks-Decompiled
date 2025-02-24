# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/profile/profile_utils.py
from gui.Scaleform.daapi.view.lobby.profile import ProfileUtils as commonProfileUtils
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import ProfileUtils, DetailedStatisticsUtils
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.impl import backport

def _avgAssignedDmgComp7Field(targetData, isCurrentUser):
    formatedAssignedDmg = ProfileUtils.formatEfficiency(targetData.getBattlesCountVer2(), targetData.getDamageAssistedEfficiency)
    return DetailedStatisticsUtils.getDetailedDataObject(PROFILE.SECTION_STATISTICS_SCORES_AVGASSISTEDDAMAGE_SHORTSELF if isCurrentUser else PROFILE.SECTION_STATISTICS_SCORES_AVGASSISTEDDAMAGE_SHORTOTHER, formatedAssignedDmg, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDDAMAGE_SHORTSELF_COMP7 if isCurrentUser else PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDDAMAGE_SHORTOTHER)


class _AvgPrestigePointsField(commonProfileUtils._AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return backport.getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgPrestigePoints()))


class _AvgPoiCapturedField(commonProfileUtils._AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return backport.getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgPoiCaptured()))


class _AvgRoleSkillUsedField(commonProfileUtils._AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return backport.getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getAvgRoleSkillUsed()))


class _AvgAssistedStunDmgComp7Field(commonProfileUtils._AvgAssistedStunDmgField):

    @staticmethod
    def _getSelfStrings():
        label = PROFILE.SECTION_STATISTICS_DETAILED_AVGASSISTEDSTUNDAMAGE_SHORTSELF
        tooltip = PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDSTUNDAMAGE_COMP7_SHORTSELF
        return (label, tooltip)

    @staticmethod
    def _getOtherStrings():
        label = PROFILE.SECTION_STATISTICS_DETAILED_AVGASSISTEDSTUNDAMAGE_SHORTOTHER
        tooltip = PROFILE.PROFILE_PARAMS_TOOLTIP_AVGASSISTEDSTUNDAMAGE_COMP7_SHORTOTHER
        return (label, tooltip)


class _MaxPrestigePointsField(commonProfileUtils._AbstractField):

    def __call__(self, targetData, isCurrentUser):
        vehicle = self.__getVehicle(targetData)
        tooltipData = self._buildTooltipData(targetData, isCurrentUser) if vehicle is not None else None
        tooltip = '{}/vehicle'.format(self._tooltip) if vehicle is not None else self._tooltip
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), tooltip, tooltipData)

    def _buildData(self, targetData, isCurrentUser):
        return backport.getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getMaxPrestigePoints()))

    def _buildTooltipData(self, targetData, isCurrentUser):
        vehicle = self.__getVehicle(targetData)
        return ProfileUtils.getRecordTooltipDataByVehicle(vehicle) if vehicle is not None else None

    def __getVehicle(self, targetData):
        vehGetter = getattr(targetData, 'getMaxPrestigePointsVehicle', None)
        return self.itemsCache.items.getItemByCD(vehGetter()) if vehGetter is not None else None


class _MaxWinSeriesField(commonProfileUtils._AbstractField):

    def _buildData(self, targetData, isCurrentUser):
        return '{}/{}'.format(backport.getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getMaxWinSeries())), backport.getIntegralFormat(ProfileUtils.getValueOrUnavailable(targetData.getMaxSquadWinSeries())))


class _MaxEquipmentDamageDealtField(commonProfileUtils._AbstractField):

    def __call__(self, targetData, isCurrentUser):
        vehicle = self.__getVehicle(targetData)
        tooltipData = self._buildTooltipData(targetData, isCurrentUser) if vehicle is not None else None
        tooltip = '{}/vehicle'.format(self._tooltip) if vehicle is not None else self._tooltip
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), tooltip, tooltipData)

    def _buildData(self, targetData, isCurrentUser):
        return backport.getIntegralFormat(targetData.getMaxEquipmentDamageDealt())

    def _buildTooltipData(self, targetData, isCurrentUser):
        vehicle = self.__getVehicle(targetData)
        return ProfileUtils.getRecordTooltipDataByVehicle(vehicle) if vehicle is not None else None

    def __getVehicle(self, targetData):
        vehGetter = getattr(targetData, 'getMaxEquipmentDamageDealtVehicle', None)
        return self.itemsCache.items.getItemByCD(vehGetter()) if vehGetter is not None else None


class _MaxHealthRepairField(commonProfileUtils._AbstractField):

    def __call__(self, targetData, isCurrentUser):
        vehicle = self.__getVehicle(targetData)
        tooltipData = self._buildTooltipData(targetData, isCurrentUser) if vehicle is not None else None
        tooltip = '{}/vehicle'.format(self._tooltip) if vehicle is not None else self._tooltip
        return DetailedStatisticsUtils.getDetailedDataObject(self._label, self._buildData(targetData, isCurrentUser), tooltip, tooltipData)

    def _buildData(self, targetData, isCurrentUser):
        maxValue = targetData.getMaxHealthRepair() or ProfileUtils.UNAVAILABLE_VALUE
        return backport.getIntegralFormat(maxValue)

    def _buildTooltipData(self, targetData, isCurrentUser):
        vehicle = self.__getVehicle(targetData)
        return ProfileUtils.getRecordTooltipDataByVehicle(vehicle) if vehicle is not None else None

    def __getVehicle(self, targetData):
        vehGetter = getattr(targetData, 'getMaxHealthRepairVehicle', None)
        return self.itemsCache.items.getItemByCD(vehGetter()) if vehGetter is not None else None


class _PoiCapturedField(commonProfileUtils._OnlyAccountField):

    def _buildData(self, targetData, isCurrentUser):
        return backport.getIntegralFormat(targetData.getPoiCaptured())


COMMON_SECTION_COMP7_FIELDS = (commonProfileUtils._BattlesCountField(PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
 commonProfileUtils._WinsEfficiencyField(PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS),
 commonProfileUtils._SurvivalField(PROFILE.SECTION_STATISTICS_SCORES_SURVIVAL, PROFILE.PROFILE_PARAMS_TOOLTIP_SURVIVAL),
 commonProfileUtils._HitsField(PROFILE.SECTION_STATISTICS_SCORES_HITS, PROFILE.PROFILE_PARAMS_TOOLTIP_HITS),
 commonProfileUtils._emptyField,
 commonProfileUtils._DamageCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DAMAGECOEFF),
 commonProfileUtils._DestructionCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DESTRUCTIONCOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DESTROYCOEFF),
 commonProfileUtils._ArmorusingField(PROFILE.SECTION_STATISTICS_SCORES_ARMORUSING, PROFILE.PROFILE_PARAMS_TOOLTIP_ARMORUSING),
 commonProfileUtils._CapturePointsField(PROFILE.SECTION_STATISTICS_SCORES_CAPTUREPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_CAPTUREPOINTS),
 commonProfileUtils._DroppedPointsField(PROFILE.SECTION_STATISTICS_SCORES_DROPPEDCAPTUREPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_DROPPEDCAPTUREPOINTS),
 _PoiCapturedField(PROFILE.SECTION_STATISTICS_SCORES_POICAPTURED, PROFILE.PROFILE_PARAMS_TOOLTIP_POICAPTURED))
COMMON_SECTION_COMP7_VEHICLE_FIELDS = (commonProfileUtils._BattlesCountField(PROFILE.SECTION_STATISTICS_SCORES_TOTALBATTLES, PROFILE.PROFILE_PARAMS_TOOLTIP_BATTLESCOUNT),
 commonProfileUtils._WinsEfficiencyField(PROFILE.SECTION_STATISTICS_SCORES_TOTALWINS, PROFILE.PROFILE_PARAMS_TOOLTIP_WINS),
 commonProfileUtils._SurvivalField(PROFILE.SECTION_STATISTICS_SCORES_SURVIVAL, PROFILE.PROFILE_PARAMS_TOOLTIP_SURVIVAL),
 commonProfileUtils._HitsField(PROFILE.SECTION_STATISTICS_SCORES_HITS, PROFILE.PROFILE_PARAMS_TOOLTIP_HITS),
 commonProfileUtils._emptyField,
 commonProfileUtils._DamageCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DAMAGECOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DAMAGECOEFF),
 commonProfileUtils._DestructionCoefficientField(PROFILE.SECTION_STATISTICS_DETAILED_DESTRUCTIONCOEFFICIENT, PROFILE.PROFILE_PARAMS_TOOLTIP_DESTROYCOEFF),
 commonProfileUtils._ArmorusingField(PROFILE.SECTION_STATISTICS_SCORES_ARMORUSING, PROFILE.PROFILE_PARAMS_TOOLTIP_ARMORUSING))
AVERAGE_SECTION_COMP7_FIELDS = (_AvgPrestigePointsField(PROFILE.SECTION_STATISTICS_DETAILED_AVGPRESTIGEPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGPRESTIGEPOINTS),
 commonProfileUtils._avgExpField,
 commonProfileUtils._emptyField,
 commonProfileUtils._AvgDmgField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDMG_SHORT),
 commonProfileUtils._AvgReceivedDmgField(PROFILE.SECTION_STATISTICS_DETAILED_AVGRECEIVEDDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGRECEIVEDDAMAGE),
 commonProfileUtils._AvgHealthRepairField(PROFILE.SECTION_STATISTICS_DETAILED_AVGHEALTHREPAIRED, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGHEALTHREPAIR),
 commonProfileUtils._AvgStunNumberField(PROFILE.SECTION_TECHNIQUE_STATISTICS_AVGSTUNNUMBER, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGSTUNNUMBER_COMP7),
 _avgAssignedDmgComp7Field,
 _AvgAssistedStunDmgComp7Field(),
 commonProfileUtils._emptyField,
 commonProfileUtils._AvgEnemiesSpottedField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDETECTEDENEMIES, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDETECTEDENEMIES_COMP7),
 commonProfileUtils._AvgDestroyedField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDESTROYEDVEHICLES, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDESTROYEDVEHICLES_COMP7),
 _AvgPoiCapturedField(PROFILE.SECTION_STATISTICS_DETAILED_AVGPOICAPTURED, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGPOICAPTURED),
 _AvgRoleSkillUsedField(PROFILE.SECTION_STATISTICS_DETAILED_AVGROLESKILLUSED, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGROLESKILLUSED))
AVERAGE_SECTION_COMP7_VEHICLE_FIELDS = (_AvgPrestigePointsField(PROFILE.SECTION_STATISTICS_DETAILED_AVGPRESTIGEPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGPRESTIGEPOINTS),
 commonProfileUtils._avgExpField,
 commonProfileUtils._emptyField,
 commonProfileUtils._AvgDmgField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDMG_SHORT),
 commonProfileUtils._AvgReceivedDmgField(PROFILE.SECTION_STATISTICS_DETAILED_AVGRECEIVEDDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGRECEIVEDDAMAGE),
 commonProfileUtils._AvgHealthRepairField(PROFILE.SECTION_STATISTICS_DETAILED_AVGHEALTHREPAIRED, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGHEALTHREPAIR),
 commonProfileUtils._AvgStunNumberField(PROFILE.SECTION_TECHNIQUE_STATISTICS_AVGSTUNNUMBER, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGSTUNNUMBER_COMP7),
 _avgAssignedDmgComp7Field,
 _AvgAssistedStunDmgComp7Field(),
 commonProfileUtils._emptyField,
 commonProfileUtils._AvgEnemiesSpottedField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDETECTEDENEMIES, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDETECTEDENEMIES_COMP7),
 commonProfileUtils._AvgDestroyedField(PROFILE.SECTION_STATISTICS_DETAILED_AVGDESTROYEDVEHICLES, PROFILE.PROFILE_PARAMS_TOOLTIP_AVGDESTROYEDVEHICLES_COMP7))
RECORD_SECTION_COMP7_FIELDS = (_MaxPrestigePointsField(PROFILE.SECTION_STATISTICS_SCORES_MAXPRESTIGEPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXPRESTIGEPOINTS),
 commonProfileUtils._MaxXPField(PROFILE.SECTION_STATISTICS_SCORES_MAXEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEXP),
 commonProfileUtils._MaxDamageField(PROFILE.SECTION_STATISTICS_SCORES_MAXDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLEMAXDAMAGE),
 _MaxEquipmentDamageDealtField(PROFILE.SECTION_STATISTICS_SCORES_MAXEQUIPMENTDAMAGEDEALT, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEQUIPMENTDAMAGEDEALT),
 _MaxHealthRepairField(PROFILE.PROFILE_SECTION_STATISTICS_SCORES_MAXHEALTHREPAIR, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXHEALTHREPAIR),
 commonProfileUtils._MaxDestroyedField(PROFILE.SECTION_STATISTICS_DETAILED_MAXDESTROYEDVEHICLES, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXDESTROYED),
 _MaxWinSeriesField(PROFILE.SECTION_STATISTICS_SCORES_MAXWINSERIES, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXWINSERIES))
RECORD_SECTION_COMP7_VEHICLE_FIELDS = (_MaxPrestigePointsField(PROFILE.SECTION_STATISTICS_SCORES_MAXPRESTIGEPOINTS, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXPRESTIGEPOINTS),
 commonProfileUtils._MaxXPField(PROFILE.SECTION_STATISTICS_SCORES_MAXEXPERIENCE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEXP),
 commonProfileUtils._MaxDamageField(PROFILE.SECTION_STATISTICS_SCORES_MAXDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXDAMAGE, PROFILE.PROFILE_PARAMS_TOOLTIP_UNAVAILABLEMAXDAMAGE),
 _MaxEquipmentDamageDealtField(PROFILE.SECTION_STATISTICS_SCORES_MAXEQUIPMENTDAMAGEDEALT, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXEQUIPMENTDAMAGEDEALT),
 _MaxHealthRepairField(PROFILE.PROFILE_SECTION_STATISTICS_SCORES_MAXHEALTHREPAIR, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXHEALTHREPAIR),
 commonProfileUtils._MaxDestroyedField(PROFILE.SECTION_STATISTICS_DETAILED_MAXDESTROYEDVEHICLES, PROFILE.PROFILE_PARAMS_TOOLTIP_MAXDESTROYED))
COMP7_STATISTICS_LAYOUT = ((PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_COMMON, COMMON_SECTION_COMP7_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_AVERAGE, AVERAGE_SECTION_COMP7_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_RECORD, RECORD_SECTION_COMP7_FIELDS))
COMP7_VEHICLE_STATISTICS_LAYOUT = ((PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_COMMON, COMMON_SECTION_COMP7_VEHICLE_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_AVERAGE, AVERAGE_SECTION_COMP7_VEHICLE_FIELDS), (PROFILE.SECTION_STATISTICS_BODYPARAMS_LABEL_RECORD, RECORD_SECTION_COMP7_VEHICLE_FIELDS))
