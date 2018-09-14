# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_parameters.py
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control import getVehicleComparisonBasketCtrl
from gui.game_control.veh_comparison_basket import CREW_TYPES
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.items_parameters.comparator import rateParameterState, PARAM_STATE, VehiclesComparator, getParamExtendedData
from gui.shared.items_parameters.formatters import FORMAT_SETTINGS
from gui.shared.items_parameters.params import VehicleParams
from gui.shared.items_parameters.params_helper import VehParamsBaseGenerator
from gui.shared.items_parameters import formatters
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
        data['text'] = formatters.formatParameter(param.name, param.value, param.state, self.__headerScheme, _CMP_FORMAT_SETTINGS)
        return data

    def _makeAdvancedParamVO(self, param):
        data = super(_VehParamsValuesGenerator, self)._makeAdvancedParamVO(param)
        if param.value:
            data['text'] = formatters.formatParameter(param.name, param.value, param.state, self.__bodyScheme, _CMP_FORMAT_SETTINGS)
        else:
            data['text'] = getUndefinedParam()
        return data


class _VehCompareParametersData(object):

    def __init__(self, cache, vehIntCD, isInInventory, crewLvl, modulesType, vehicleStrCD, showWarning):
        super(_VehCompareParametersData, self).__init__()
        self.__crewLvl = None
        self.__modulesType = None
        self.__isInInventory = None
        self.__currentVehParams = None
        self.__vehicleStrCD = None
        self.__vehicle = None
        self.__isCrewLvlInvalid = False
        self.__isInInvInvalid = False
        self.__isCurrVehParamsInvalid = False
        self.__vehicleCD = vehIntCD
        self.setIsInInventory(isInInventory)
        self.setVehicleStrCD(vehicleStrCD)
        self.setCrewLvl(crewLvl)
        self.setModulesType(modulesType)
        self.__cache = cache
        self.__paramGenerator = _VehParamsValuesGenerator(*_COLOR_SCHEMES)
        self.__parameters = self.__initParameters(vehIntCD, self.__vehicle, showWarning)
        return

    def setCrewLvl(self, newVal):
        if self.__crewLvl != newVal:
            self.__crewLvl = newVal
            if self.__crewLvl == CREW_TYPES.CURRENT:
                vehicle = g_itemsCache.items.getItemByCD(self.__vehicleCD)
                crewLevels = map(lambda crewData: crewData[1].roleLevel if crewData[1] else None, vehicle.crew)
            else:
                crewLevels = (self.__crewLvl,)
            self.__vehicle.crew = self.__vehicle.getCrewBySkillLevels(*crewLevels)
            self.__isCrewLvlInvalid = True
            self.__isCurrVehParamsInvalid = True
        return self.__isCrewLvlInvalid

    def setVehicleStrCD(self, vehicleStrCD):
        if self.__vehicleStrCD != vehicleStrCD:
            self.__vehicleStrCD = vehicleStrCD
            self.__vehicle = Vehicle(self.__vehicleStrCD)
            self.__isCurrVehParamsInvalid = True
            return True
        return False

    def setModulesType(self, newVal):
        if self.__modulesType != newVal:
            self.__modulesType = newVal
            self.__isModulesTypesInvalid = True
            self.__isCurrVehParamsInvalid = True
        return self.__isModulesTypesInvalid

    def setIsInInventory(self, newVal):
        if self.__isInInventory != newVal:
            self.__isInInventory = newVal
            self.__isInInvInvalid = True
        return self.__isInInvInvalid

    def dispose(self):
        self.__cache = None
        self.__paramGenerator = None
        self.__currentVehParams = None
        self.__parameters = None
        return

    def getFormattedParameters(self, vehMaxParams):
        if self.__isCrewLvlInvalid:
            if self.__isCrewLvlInvalid:
                self.__parameters.update(crewLevelIndx=CREW_TYPES.ALL.index(self.__crewLvl))
                self.__isCrewLvlInvalid = False
        if self.__isInInvInvalid:
            crewListParams = [{'label': VEH_COMPARE.VEHICLECOMPAREVIEW_CREW_SKILL100,
              'id': CREW_TYPES.SKILL_100,
              'showAlert': False,
              'tooltip': None}, {'label': VEH_COMPARE.VEHICLECOMPAREVIEW_CREW_SKILL75,
              'id': CREW_TYPES.SKILL_75}, {'label': VEH_COMPARE.VEHICLECOMPAREVIEW_CREW_SKILL50,
              'id': CREW_TYPES.SKILL_50}]
            if self.__isInInventory:
                crewListParams.append({'label': VEH_COMPARE.VEHICLECOMPAREVIEW_CREW_CURRENT,
                 'id': CREW_TYPES.CURRENT})
            self.__isInInvInvalid = False
            self.__parameters.update(crewLevels=crewListParams, isInHangar=self.__isInInventory)
        if self.__isModulesTypesInvalid:
            self.__parameters.update(elite=self.__vehicle.isElite, moduleType=self._getModuleType(self.__modulesType))
            self.__isModulesTypesInvalid = False
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
            states = pInfo.state
            if isinstance(pInfo.value, (tuple, list)):
                deltaVals = []
                isTheSame = True
                for st in states:
                    diff = st[1]
                    isTheSame = isTheSame and diff == 0
                    deltaVals.append(diff)

                if isTheSame:
                    return None
            else:
                deltaVals = states[1]
            return formatters.formatParameter(pInfo.name, deltaVals, states, _DELTA_PARAM_COLOR_SCHEME, _CMP_FORMAT_SETTINGS)
        else:
            return None

    @classmethod
    def _getModuleType(cls, mType):
        return '#veh_compare:vehicleCompareView/moduleType/{}'.format(mType)

    @classmethod
    def __initParameters(cls, vehCD, vehicle, showWarning):
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
         'isAttention': showWarning,
         'index': -1,
         'isInHangar': False,
         'moduleType': cls._getModuleType(VEH_COMPARE.VEHICLECOMPAREVIEW_MODULETYPE_BASIC),
         'crewLevelIndx': -1,
         'elite': vehicle.isElite,
         'params': [],
         'crewLevels': []}


class IVehCompareView(object):

    def buildList(self, *args):
        raise NotImplementedError

    def updateItems(self, *args):
        raise NotImplementedError


class VehCompareBasketParamsCache(object):

    def __init__(self, view):
        super(VehCompareBasketParamsCache, self).__init__()
        self.__cache = []
        self.__view = view
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange += self.__onVehCountChanged
        comparisonBasket.onParametersChange += self.__onVehParamsChanged
        for vehInd in range(comparisonBasket.getVehiclesCount()):
            self.__addParamData(vehInd)

        self.__rebuildList()

    def dispose(self):
        self.__view = None
        while self.__cache:
            self.__cache.pop().dispose()

        self.__cache = None
        comparisonBasket = getVehicleComparisonBasketCtrl()
        comparisonBasket.onChange -= self.__onVehCountChanged
        comparisonBasket.onParametersChange -= self.__onVehParamsChanged
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
        vehCompareData = getVehicleComparisonBasketCtrl().getVehicleAt(index)
        paramsData = _VehCompareParametersData(self.__cache, vehCompareData.getVehicleCD(), vehCompareData.isInInventory(), vehCompareData.getCrewLevel(), vehCompareData.getModulesType(), vehCompareData.getVehicleStrCD(), not vehCompareData.isActualModules())
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
            basketVehData = getVehicleComparisonBasketCtrl().getVehicleAt(index)
            paramsVehData = self.__cache[index]
            paramsVehData.setIsInInventory(basketVehData.isInInventory())
            paramsVehData.setModulesType(basketVehData.getModulesType())
            isBestScoreInvalid = isBestScoreInvalid or paramsVehData.setCrewLvl(basketVehData.getCrewLevel())
            isBestScoreInvalid = isBestScoreInvalid or paramsVehData.setVehicleStrCD(basketVehData.getVehicleStrCD())

        if self.__cache:
            bestParams = _reCalcBestParameters(self.__cache) if isBestScoreInvalid else None
            params = map(lambda paramData: paramData.getFormattedParameters(bestParams), self.__cache)
            self.__view.updateItems(params)
        return
