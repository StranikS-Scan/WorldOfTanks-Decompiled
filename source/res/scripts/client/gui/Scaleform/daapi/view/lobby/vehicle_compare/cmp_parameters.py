# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_parameters.py
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control.veh_comparison_basket import CONFIGURATION_TYPES, CREW_TYPES
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.items_parameters import formatters
from gui.shared.items_parameters.comparator import rateParameterState, PARAM_STATE, VehiclesComparator, getParamExtendedData
from gui.shared.items_parameters.formatters import FORMAT_SETTINGS
from gui.shared.items_parameters.params import VehicleParams
from gui.shared.items_parameters.params_helper import VehParamsBaseGenerator
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket
_HEADER_PARAM_COLOR_SCHEME = (text_styles.middleTitle, text_styles.middleBonusTitle, text_styles.middleTitle)
_HEADER_PARAM_NO_COLOR_SCHEME = (text_styles.middleTitle, text_styles.middleTitle, text_styles.middleTitle)
_PARAM_COLOR_SCHEME = (text_styles.main, text_styles.bonusAppliedText, text_styles.main)
_PARAM_NO_COLOR_SCHEME = (text_styles.main, text_styles.main, text_styles.main)
_DELTA_PARAM_COLOR_SCHEME = (text_styles.error, text_styles.main, text_styles.bonusAppliedText)
_NO_COLOR_SCHEMES = (_HEADER_PARAM_NO_COLOR_SCHEME, _PARAM_NO_COLOR_SCHEME)
_COLOR_SCHEMES = (_HEADER_PARAM_COLOR_SCHEME, _PARAM_COLOR_SCHEME)

def _generateFormatSettings():
    space = ' '
    copy = {}
    for originalName, originalSetting in FORMAT_SETTINGS.iteritems():
        settingCopy = originalSetting.copy()
        if 'separator' in settingCopy:
            settingCopy['separator'] = ''.join((space, settingCopy['separator'], space))
        copy[originalName] = settingCopy

    return copy


_CMP_FORMAT_SETTINGS = _generateFormatSettings()

def getUndefinedParam():
    return text_styles.stats('--')


def _reCalcBestParameters(targetCache):
    assert targetCache
    bestParamsDict = {}
    for vcParamData in targetCache:
        params = vcParamData.getParams()
        for pKey, pVal in params.iteritems():
            if isinstance(pVal, (tuple, list)):
                if pKey in bestParamsDict:
                    rateParamsList = rateParameterState(pKey, bestParamsDict[pKey], pVal)
                    for idx, (state, diff) in enumerate(rateParamsList):
                        if state == PARAM_STATE.WORSE:
                            maxVals = bestParamsDict[pKey]
                            if idx == len(maxVals):
                                maxVals.append(pVal[idx])
                            else:
                                maxVals[idx] = pVal[idx]

                else:
                    bestParamsDict[pKey] = list(pVal)
            if pKey in bestParamsDict:
                state, diff = rateParameterState(pKey, bestParamsDict[pKey], pVal)
                if state == PARAM_STATE.WORSE:
                    bestParamsDict[pKey] = pVal
            bestParamsDict[pKey] = pVal

    return bestParamsDict


class _VehParamsValuesGenerator(VehParamsBaseGenerator):

    def __init__(self, headerScheme, bodyScheme):
        super(_VehParamsValuesGenerator, self).__init__()
        self.setColorSchemes(headerScheme, bodyScheme)

    def setColorSchemes(self, header, body):
        self.__headerScheme = header
        self.__bodyScheme = body

    def _makeSimpleParamHeaderVO(self, param, isOpen, comparator):
        data = super(_VehParamsValuesGenerator, self)._makeSimpleParamHeaderVO(param, isOpen, comparator)
        data['text'] = formatters.formatParameter(param.name, param.value, param.state, self.__headerScheme, _CMP_FORMAT_SETTINGS, False)
        return data

    def _makeAdvancedParamVO(self, param):
        data = super(_VehParamsValuesGenerator, self)._makeAdvancedParamVO(param)
        if param.value:
            data['text'] = formatters.formatParameter(param.name, param.value, param.state, self.__bodyScheme, _CMP_FORMAT_SETTINGS, False)
        else:
            data['text'] = getUndefinedParam()
        return data


class _VehCompareParametersData(object):

    def __init__(self, cache, vehIntCD, isInInventory, crewData, configurationType, vehData):
        super(_VehCompareParametersData, self).__init__()
        self.__crewLvl = None
        self.__skills = None
        self.__configurationType = None
        self.__isInInventory = None
        self.__currentVehParams = None
        self.__vehicleStrCD = None
        self.__equipment = []
        self.__hasCamouflage = False
        self.__selectedShellIdx = 0
        self.__vehicle = None
        self.__isCrewInvalid = False
        self.__isInInvInvalid = False
        self.__isCurrVehParamsInvalid = False
        self.__vehicleIntCD = vehIntCD
        self.setIsInInventory(isInInventory)
        self.setVehicleData(*vehData)
        self.setCrewData(*crewData)
        self.setConfigurationType(configurationType)
        self.__cache = cache
        self.__paramGenerator = _VehParamsValuesGenerator(*_COLOR_SCHEMES)
        self.__parameters = self.__initParameters(vehIntCD, self.__vehicle)
        return

    def setCrewData(self, crewLvl, skills):
        """
        Updates crew information
        :param crewLvl: int, one of gui.game_control.veh_comparison_basket.CREW_TYPES
        :param skills: set, [skillName, ...]
        :return: bool, True if new incoming data is not similar as existed, otherwise - False
        """
        if self.__crewLvl != crewLvl or self.__skills != skills:
            self.__crewLvl = crewLvl
            self.__skills = skills
            skillsDict = {}
            skillsByRoles = cmp_helpers.getVehicleCrewSkills(self.__vehicle)
            for idx, (role, skillsSet) in enumerate(skillsByRoles):
                sameSkills = skillsSet.intersection(self.__skills)
                if sameSkills:
                    skillsDict[idx] = sameSkills

            if crewLvl == CREW_TYPES.CURRENT:
                levelsByIndexes, nativeVehiclesByIndexes = cmp_helpers.getVehCrewInfo(self.__vehicle.intCD)
                defRoleLevel = None
            else:
                levelsByIndexes = {}
                defRoleLevel = self.__crewLvl
                nativeVehiclesByIndexes = None
            self.__vehicle.crew = self.__vehicle.getCrewBySkillLevels(defRoleLevel, skillsDict, levelsByIndexes, nativeVehiclesByIndexes)
            self.__isCrewInvalid = True
            self.__isCurrVehParamsInvalid = True
        return self.__isCrewInvalid

    def setVehicleData(self, vehicleStrCD, equipment, hasCamouflage, selectedShellIdx):
        isDifferent = False
        camouflageInvalid = self.__hasCamouflage != hasCamouflage
        equipInvalid = equipment != self.__equipment
        shellInvalid = selectedShellIdx != self.__selectedShellIdx
        if vehicleStrCD != self.__vehicleStrCD:
            self.__vehicleStrCD = vehicleStrCD
            self.__vehicle = Vehicle(self.__vehicleStrCD)
            self.__isCurrVehParamsInvalid = True
            isDifferent = True
            equipInvalid = True
            camouflageInvalid = True
        if equipInvalid:
            for i, eq in enumerate(equipment):
                cmp_helpers.installEquipmentOnVehicle(self.__vehicle, eq, i)

            self.__equipment = equipment
            isDifferent = True
        if camouflageInvalid:
            cmp_helpers.applyCamouflage(self.__vehicle, hasCamouflage)
            self.__hasCamouflage = hasCamouflage
            isDifferent = True
        if shellInvalid:
            self.__vehicle.descriptor.activeGunShotIndex = selectedShellIdx
            self.__selectedShellIdx = selectedShellIdx
            isDifferent = True
        return isDifferent

    def setConfigurationType(self, newVal):
        if self.__configurationType != newVal:
            self.__configurationType = newVal
            self.__isConfigurationTypesInvalid = True
            self.__isCurrVehParamsInvalid = True
        return self.__isConfigurationTypesInvalid

    def setIsInInventory(self, newVal):
        if self.__isInInventory != newVal:
            self.__isInInventory = newVal
            self.__isInInvInvalid = True
        return self.__isInInvInvalid

    def dispose(self):
        self.__skills = None
        self.__vehicleStrCD = None
        self.__equipment = None
        self.__cache = None
        self.__paramGenerator = None
        self.__currentVehParams = None
        self.__parameters = None
        return

    def getVehicleIntCD(self):
        return self.__vehicleIntCD

    def getFormattedParameters(self, vehMaxParams):
        if self.__isCrewInvalid:
            if self.__isCrewInvalid:
                self.__isCrewInvalid = False
        if self.__isInInvInvalid:
            self.__isInInvInvalid = False
            self.__parameters.update(isInHangar=self.__isInInventory)
        if self.__isConfigurationTypesInvalid:
            self.__parameters.update(elite=self.__vehicle.isElite, moduleType=self._getConfigurationType(self.__configurationType), showRevertBtn=self.__showRevertButton())
            self.__isConfigurationTypesInvalid = False
        if vehMaxParams:
            currentDataIndex = self.__cache.index(self)
            if currentDataIndex == 0:
                scheme = _NO_COLOR_SCHEMES if len(self.__cache) == 1 else _COLOR_SCHEMES
                self.__paramGenerator.setColorSchemes(*scheme)
            self.__parameters.update(params=self.__paramGenerator.getFormattedParams(VehiclesComparator(self.getParams(), vehMaxParams)), index=currentDataIndex)
        return self.__parameters

    def getParams(self):
        if self.__isCurrVehParamsInvalid:
            self.__isCurrVehParamsInvalid = False
            self.__currentVehParams = VehicleParams(self.__vehicle).getParamsDict()
        return self.__currentVehParams

    def getDeltaParams(self, paramName, paramValue):
        """
        Calculates delta and return it in formatted HTML string
        :param paramName: parameter name as string ('damage', 'turretArmor', etc...)
        :param paramValue: parameter value
        :return: formatted HTML string
        """
        params = self.getParams()
        if paramName in params:
            pInfo = getParamExtendedData(paramName, params[paramName], paramValue)
            return formatters.formatParameterDelta(pInfo, _DELTA_PARAM_COLOR_SCHEME, _CMP_FORMAT_SETTINGS)

    @classmethod
    def _getConfigurationType(cls, mType):
        format_style = text_styles.neutral if mType == CONFIGURATION_TYPES.CUSTOM else text_styles.main
        return format_style('#veh_compare:vehicleCompareView/configurationType/{}'.format(mType))

    @classmethod
    def __initParameters(cls, vehCD, vehicle):
        """
        Generates some constant data for vehicle
        :return: vo as dict
        """
        return {'id': vehCD,
         'nation': vehicle.nationID,
         'image': vehicle.icon,
         'label': text_styles.main(vehicle.shortUserName),
         'level': vehicle.level,
         'premium': vehicle.isPremium,
         'tankType': vehicle.type,
         'isAttention': False,
         'index': -1,
         'isInHangar': False,
         'moduleType': cls._getConfigurationType(VEH_COMPARE.VEHICLECOMPAREVIEW_CONFIGURATIONTYPE_BASIC),
         'elite': vehicle.isElite,
         'params': [],
         'showRevertBtn': False}

    def __showRevertButton(self):
        return self.__configurationType == CONFIGURATION_TYPES.CUSTOM


class IVehCompareView(object):

    def buildList(self, *args):
        raise NotImplementedError

    def updateItems(self, *args):
        raise NotImplementedError


class VehCompareBasketParamsCache(object):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, view):
        super(VehCompareBasketParamsCache, self).__init__()
        self.__cache = []
        self.__view = view
        self.comparisonBasket.onChange += self.__onVehCountChanged
        self.comparisonBasket.onParametersChange += self.__onVehParamsChanged
        for vehInd in range(self.comparisonBasket.getVehiclesCount()):
            self.__addParamData(vehInd)

        self.__rebuildList()

    def dispose(self):
        self.__view = None
        while self.__cache:
            self.__cache.pop().dispose()

        self.__cache = None
        self.comparisonBasket.onChange -= self.__onVehCountChanged
        self.comparisonBasket.onParametersChange -= self.__onVehParamsChanged
        return

    def getParametersDelta(self, index, paramName):
        """
        Generates the list of parameters deltas
        :param index: int index of item in cache
        :param paramName: string name of parameter ('damage', 'turretArmor', ...)
        :return: list of formatted parameters deltas
        """
        targetItem = self.__cache[index]
        targetParams = targetItem.getParams()
        outcome = []
        if paramName in targetParams:
            targetVal = targetParams[paramName]
            for i in range(0, len(self.__cache)):
                if i == index:
                    outcome.append(None)
                outcome.append(self.__cache[i].getDeltaParams(paramName=paramName, paramValue=targetVal))

        return outcome

    def __addParamData(self, index):
        vehCompareData = self.comparisonBasket.getVehicleAt(index)
        paramsData = _VehCompareParametersData(self.__cache, vehCompareData.getVehicleCD(), vehCompareData.isInInventory(), vehCompareData.getCrewData(), vehCompareData.getConfigurationType(), (vehCompareData.getVehicleStrCD(),
         vehCompareData.getEquipment(),
         vehCompareData.hasCamouflage(),
         vehCompareData.getSelectedShellIndex()))
        self.__cache.insert(index, paramsData)

    def __rebuildList(self):
        if self.__cache:
            bestParams = _reCalcBestParameters(self.__cache)
            params = map(lambda paramData: paramData.getFormattedParameters(bestParams), self.__cache)
            self.__view.buildList(params)
        else:
            self.__view.buildList([])

    def __onVehCountChanged(self, changedData):
        if changedData.removedIDXs:
            for i in changedData.removedIDXs:
                self.__cache[i].dispose()
                del self.__cache[i]

        elif changedData.addedIDXs:
            for i in changedData.addedIDXs:
                self.__addParamData(i)

        self.__rebuildList()

    def __onVehParamsChanged(self, data):
        isBestScoreInvalid = False
        for index in data:
            basketVehData = self.comparisonBasket.getVehicleAt(index)
            paramsVehData = self.__cache[index]
            paramsVehData.setIsInInventory(basketVehData.isInInventory())
            paramsVehData.setConfigurationType(basketVehData.getConfigurationType())
            isBestScoreInvalid = isBestScoreInvalid or paramsVehData.setCrewData(*basketVehData.getCrewData())
            isBestScoreInvalid = isBestScoreInvalid or paramsVehData.setVehicleData(basketVehData.getVehicleStrCD(), basketVehData.getEquipment(), basketVehData.hasCamouflage(), basketVehData.getSelectedShellIndex())

        if self.__cache:
            bestParams = _reCalcBestParameters(self.__cache) if isBestScoreInvalid else None
            params = map(lambda paramData: paramData.getFormattedParameters(bestParams), self.__cache)
            self.__view.updateItems(params)
        return
