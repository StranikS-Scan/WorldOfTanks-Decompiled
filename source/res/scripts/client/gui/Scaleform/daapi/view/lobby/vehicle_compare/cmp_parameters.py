# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_parameters.py
import typing
from copy import copy
from gui.impl import backport
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control.veh_comparison_basket import CONFIGURATION_TYPES
from gui.shared.formatters import text_styles
from gui.shared.gui_items import vehicle_adjusters
from gui.shared.gui_items.Tankman import CrewTypes
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.items_parameters import formatters
from gui.shared.items_parameters.comparator import rateParameterState, PARAM_STATE, VehiclesComparator, getParamExtendedData, PARAMS_NORMALIZATION_MAP
from gui.shared.items_parameters.formatters import FORMAT_SETTINGS, shotDispersionAnglePreprocessor
from gui.shared.items_parameters.params import VehicleParams
from gui.shared.items_parameters.params_helper import VehParamsBaseGenerator, isValidEmptyValue
from gui.shared.utils import SHOT_DISPERSION_ANGLE
from helpers import dependency
from post_progression_common import VehicleState
from skeletons.gui.game_control import IVehicleComparisonBasket
_HEADER_PARAM_COLOR_SCHEME = (text_styles.middleTitle, text_styles.middleBonusTitle, text_styles.middleTitle)
_HEADER_PARAM_NO_COLOR_SCHEME = (text_styles.middleTitle, text_styles.middleTitle, text_styles.middleTitle)
_PARAM_COLOR_SCHEME = (text_styles.main, text_styles.bonusAppliedText, text_styles.main)
_PARAM_NO_COLOR_SCHEME = (text_styles.main, text_styles.main, text_styles.main)
_DELTA_PARAM_COLOR_SCHEME = (text_styles.error, text_styles.main, text_styles.bonusAppliedText)
_NO_COLOR_SCHEMES = (_HEADER_PARAM_NO_COLOR_SCHEME, _PARAM_NO_COLOR_SCHEME)
_COLOR_SCHEMES = (_HEADER_PARAM_COLOR_SCHEME, _PARAM_COLOR_SCHEME)

def _generateFormatSettings():
    settings = copy(FORMAT_SETTINGS)
    settings.update({SHOT_DISPERSION_ANGLE: {'preprocessor': shotDispersionAnglePreprocessor,
                             'rounder': backport.getNiceNumberFormat,
                             'skipNone': True}})
    return settings


_CMP_FORMAT_SETTINGS = _generateFormatSettings()

class _BestParamsDict(dict):

    def __init__(self, seq=None, **kwargs):
        if seq is not None:
            super(_BestParamsDict, self).__init__(seq, **kwargs)
        else:
            super(_BestParamsDict, self).__init__(**kwargs)
        self.__lengths = {}
        return

    def addLen(self, key, value):
        if key in self.__lengths:
            self.__lengths[key] = min(self.__lengths[key], len(value))
        else:
            self.__lengths[key] = len(value)

    def toDict(self):
        res = dict(self)
        for k, valuableLength in self.__lengths.iteritems():
            res[k] = self[k][:valuableLength]

        return res


def getUndefinedParam():
    return text_styles.stats('--')


def _hasNormalizeParameters(cache):
    for item in cache:
        vehicle = item.getVehicle()
        if vehicle is None:
            continue
        if vehicle.descriptor.hasDualAccuracy:
            return True

    return False


def _reCalcBestParameters(targetCache):
    bestParamsDict = _BestParamsDict()
    hasNormalization = _hasNormalizeParameters(targetCache)
    for vcParamData in targetCache:
        params = vcParamData.getParams()
        for pKey, pVal in params.iteritems():
            if hasNormalization and pKey in PARAMS_NORMALIZATION_MAP:
                func = PARAMS_NORMALIZATION_MAP[pKey]
                pVal = func(pVal)
            if pVal is None:
                continue
            if isinstance(pVal, (tuple, list)):
                bestParamsDict.addLen(pKey, pVal)
                if pKey in bestParamsDict:
                    rateParamsList = rateParameterState(pKey, bestParamsDict[pKey], pVal)
                    for idx, (state, _) in enumerate(rateParamsList):
                        if state == PARAM_STATE.WORSE:
                            maxVals = bestParamsDict[pKey]
                            if idx == len(maxVals):
                                maxVals.append(pVal[idx])
                            else:
                                maxVals[idx] = pVal[idx]

                else:
                    bestParamsDict[pKey] = list(pVal)
            if pKey in bestParamsDict:
                state, _ = rateParameterState(pKey, bestParamsDict[pKey], pVal)
                if state == PARAM_STATE.WORSE:
                    bestParamsDict[pKey] = pVal
            bestParamsDict[pKey] = pVal

    return bestParamsDict.toDict()


class _VehParamsValuesGenerator(VehParamsBaseGenerator):

    def __init__(self, headerScheme, bodyScheme):
        super(_VehParamsValuesGenerator, self).__init__()
        self.setColorSchemes(headerScheme, bodyScheme)

    def setColorSchemes(self, header, body):
        self.__headerScheme = header
        self.__bodyScheme = body

    def _makeSimpleParamHeaderVO(self, param, isOpen, comparator):
        data = super(_VehParamsValuesGenerator, self)._makeSimpleParamHeaderVO(param, isOpen, comparator)
        data['text'] = formatters.formatParameter(param.name, param.value, param.state, self.__headerScheme, FORMAT_SETTINGS, False)
        return data

    def _makeAdvancedParamVO(self, param, parent, highlight):
        data = super(_VehParamsValuesGenerator, self)._makeAdvancedParamVO(param, parent, highlight)
        if param.value or isValidEmptyValue(param.name, param.value):
            data['text'] = formatters.formatParameter(param.name, param.value, param.state, self.__bodyScheme, _CMP_FORMAT_SETTINGS, False)
        else:
            data['text'] = getUndefinedParam()
        return data


class _VehCompareParametersData(object):

    def __init__(self, cache, vehCompareData):
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
        self.__battleBooster = None
        self.__dynSlotType = None
        self.__postProgressionState = VehicleState()
        self.__isCrewInvalid = False
        self.__isInInvInvalid = False
        self.__isConfigurationTypesInvalid = False
        self.__isCurrVehParamsInvalid = False
        self.__vehicleIntCD = vehCompareData.getVehicleCD()
        self.setIsInInventory(vehCompareData.isInInventory())
        self.setVehicleData(vehCompareData)
        self.setCrewData(*vehCompareData.getCrewData())
        self.setConfigurationType(vehCompareData.getConfigurationType())
        self.__cache = cache
        self.__paramGenerator = _VehParamsValuesGenerator(*_COLOR_SCHEMES)
        self.__parameters = self.__initParameters(vehCompareData.getVehicleCD(), self.__vehicle)
        return

    def setCrewData(self, crewLvl, skills):
        if self.__crewLvl != crewLvl or self.__skills != skills:
            self.__crewLvl = crewLvl
            self.__skills = skills
            skillsDict = {}
            skillsByRoles = cmp_helpers.getVehicleCrewSkills(self.__vehicle)
            for idx, (_, skillsSet) in enumerate(skillsByRoles):
                sameSkills = skillsSet.intersection(self.__skills)
                if sameSkills:
                    skillsDict[idx] = sameSkills

            if crewLvl == CrewTypes.CURRENT:
                levelsByIndexes, nativeVehiclesByIndexes = cmp_helpers.getVehCrewInfo(self.__vehicle.intCD)
                defRoleLevel = None
            else:
                levelsByIndexes = {}
                defRoleLevel = self.__crewLvl
                nativeVehiclesByIndexes = None
            self.__vehicle.crew = self.__vehicle.getCrewBySkillLevels(defRoleLevel, skillsDict, levelsByIndexes, nativeVehiclesByIndexes, activateBrotherhood=True)
            self.__isCrewInvalid = True
            self.__isCurrVehParamsInvalid = True
        return self.__isCrewInvalid

    def setVehicleData(self, vehCompareData):
        vehicleStrCD = vehCompareData.getVehicleStrCD()
        equipment = vehCompareData.getEquipment()
        hasCamouflage = vehCompareData.hasCamouflage()
        selectedShellIdx = vehCompareData.getSelectedShellIndex()
        battleBooster = vehCompareData.getBattleBooster()
        dynSlotType = vehCompareData.getDynSlotType()
        postProgressionState = vehCompareData.getPostProgressionState()
        isDifferent = False
        camouflageInvalid = self.__hasCamouflage != hasCamouflage
        equipInvalid = equipment != self.__equipment
        shellInvalid = selectedShellIdx != self.__selectedShellIdx
        battleBoosterInvalid = battleBooster != self.__battleBooster
        dynSlotsInvalid = dynSlotType != self.__dynSlotType
        postProgressionInvalid = postProgressionState != self.__postProgressionState
        if vehicleStrCD != self.__vehicleStrCD:
            self.__vehicleStrCD = vehicleStrCD
            self.__vehicle = Vehicle(self.__vehicleStrCD)
            self.__isCurrVehParamsInvalid = True
            isDifferent = True
            equipInvalid = True
            camouflageInvalid = True
            dynSlotsInvalid = True
            postProgressionInvalid = True
        if equipInvalid:
            for i, eq in enumerate(equipment):
                vehicle_adjusters.installEquipment(self.__vehicle, eq, i)

            self.__equipment = equipment
            isDifferent = True
        if battleBoosterInvalid:
            self.__battleBooster = battleBooster
            intCD = battleBooster.intCD if battleBooster else None
            vehicle_adjusters.installBattleBoosterOnVehicle(self.__vehicle, intCD)
            isDifferent = True
        if camouflageInvalid:
            cmp_helpers.applyCamouflage(self.__vehicle, hasCamouflage)
            self.__hasCamouflage = hasCamouflage
            isDifferent = True
        if shellInvalid:
            self.__vehicle.descriptor.activeGunShotIndex = selectedShellIdx
            self.__selectedShellIdx = selectedShellIdx
            isDifferent = True
        if dynSlotsInvalid:
            self.__dynSlotType = dynSlotType
            self.__vehicle.optDevices.dynSlotType = dynSlotType
            self.__isCurrVehParamsInvalid = True
            isDifferent = True
        if postProgressionInvalid:
            self.__postProgressionState = postProgressionState
            self.__vehicle.installPostProgression(postProgressionState, True)
            self.__isCurrVehParamsInvalid = True
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
        self.__battleBooster = None
        self.__dynSlotType = None
        self.__postProgressionState = None
        return

    def getVehicleIntCD(self):
        return self.__vehicleIntCD

    def getFormattedParameters(self, vehMaxParams):
        self.__isCrewInvalid = False
        if self.__isInInvInvalid:
            self.__isInInvInvalid = False
            self.__parameters['isInHangar'] = self.__isInInventory
        if self.__isConfigurationTypesInvalid:
            self.__parameters.update(elite=self.__vehicle.isElite, moduleType=self._getConfigurationType(self.__configurationType), showRevertBtn=self.__showRevertButton())
            self.__isConfigurationTypesInvalid = False
        if vehMaxParams:
            currentDataIndex = self.__cache.index(self)
            if currentDataIndex == 0:
                scheme = _NO_COLOR_SCHEMES if len(self.__cache) == 1 else _COLOR_SCHEMES
                self.__paramGenerator.setColorSchemes(*scheme)
            self.__parameters.update(params=self.__paramGenerator.getFormattedParams(VehiclesComparator(self.getParams(), vehMaxParams), hasNormalization=True), index=currentDataIndex)
        return self.__parameters

    def getVehicle(self):
        return self.__vehicle

    def getParams(self):
        if self.__isCurrVehParamsInvalid:
            self.__isCurrVehParamsInvalid = False
            self.__currentVehParams = VehicleParams(self.__vehicle).getParamsDict()
        return self.__currentVehParams

    def getDeltaParams(self, paramName, paramValue, hasNormalization=False):
        params = self.getParams()
        if paramName not in params:
            return None
        else:
            otherValue = params[paramName]
            pInfo = getParamExtendedData(paramName, otherValue, paramValue, hasNormalization=hasNormalization)
            return formatters.formatParameterDelta(pInfo, _DELTA_PARAM_COLOR_SCHEME, FORMAT_SETTINGS)

    @classmethod
    def _getConfigurationType(cls, mType):
        format_style = text_styles.neutral if mType == CONFIGURATION_TYPES.CUSTOM else text_styles.main
        return format_style('#veh_compare:vehicleCompareView/configurationType/{}'.format(mType))

    @classmethod
    def __initParameters(cls, vehCD, vehicle):
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
        self.comparisonBasket.onNationChange += self.__onNationChange
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
        self.comparisonBasket.onNationChange -= self.__onNationChange
        return

    def getParametersDelta(self, index, paramName):
        targetItem = self.__cache[index]
        targetParams = targetItem.getParams()
        outcome = []
        if paramName in targetParams:
            targetVal = targetParams[paramName]
            for i in range(0, len(self.__cache)):
                if i == index:
                    outcome.append(None)
                hasNormalization = _hasNormalizeParameters(self.__cache)
                outcome.append(self.__cache[i].getDeltaParams(paramName=paramName, paramValue=targetVal, hasNormalization=hasNormalization))

        return outcome

    def __addParamData(self, index):
        vehCompareData = self.comparisonBasket.getVehicleAt(index)
        paramsData = _VehCompareParametersData(self.__cache, vehCompareData)
        self.__cache.insert(index, paramsData)

    def __rebuildList(self):
        if self.__cache:
            bestParams = _reCalcBestParameters(self.__cache)
            params = [ paramData.getFormattedParameters(bestParams) for paramData in self.__cache ]
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
            crewChanged = paramsVehData.setCrewData(*basketVehData.getCrewData())
            vehicleChanged = paramsVehData.setVehicleData(basketVehData)
            isBestScoreInvalid = isBestScoreInvalid or vehicleChanged or crewChanged

        if self.__cache:
            bestParams = _reCalcBestParameters(self.__cache) if isBestScoreInvalid else None
            params = [ paramData.getFormattedParameters(bestParams) for paramData in self.__cache ]
            self.__view.updateItems(params)
        return

    def __onNationChange(self, vehicleIDxs):
        for i in vehicleIDxs:
            self.__cache[i].dispose()
            del self.__cache[i]
            self.__addParamData(i)

        self.__rebuildList()
