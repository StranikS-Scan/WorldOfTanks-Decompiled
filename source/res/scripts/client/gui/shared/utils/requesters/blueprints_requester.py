# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/requesters/blueprints_requester.py
import logging
from collections import namedtuple, defaultdict, OrderedDict
from copy import copy
import BigWorld
import nations
from adisp import adisp_async
from blueprints.BlueprintTypes import BlueprintTypes
from blueprints.FragmentLayouts import Layout
from blueprints.FragmentTypes import NationalBlueprintFragment, IntelligenceDataFragment
from blueprints.FragmentTypes import toIntFragmentCD, getFragmentType
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils.requesters import IBlueprintsRequester
_logger = logging.getLogger(__name__)
_BlueprintData = namedtuple('BlueprintData', ('filledCount', 'totalCount', 'canConvert'))
SPECIAL_BLUEPRINT_LEVEL = frozenset([1])
_DEFAULT_LAYOUT = (1, 1, (1,))

def getFragmentNationID(fragmentCD):
    return fragmentCD >> 4 & 15


def getNationalFragmentCD(nationID):
    return nationID << 4 | BlueprintTypes.NATIONAL


def getVehicleCD(fragmentCD):
    return fragmentCD & 4294967281L


def getVehicleCDForIntelligence(fragmentCD):
    return fragmentCD & 4294967282L if fragmentCD == 1 else fragmentCD & 4294967281L


def getVehicleCDForNational(fragmentCD):
    vehicleCD = fragmentCD & 4294967281L
    return vehicleCD + 1 if vehicleCD else 1


def makeIntelligenceCD(vehicleCD):
    return toIntFragmentCD(IntelligenceDataFragment(vehicleCD))


def makeNationalCD(vehicleCD):
    return toIntFragmentCD(NationalBlueprintFragment(vehicleCD))


def getUniqueBlueprints(blueprints, isFullNationCD=False):
    vehicleFragments = defaultdict(int)
    nationalFragments = defaultdict(int)
    intelligenceData = 0
    for fragmentCD, count in blueprints.iteritems():
        fragmentType = getFragmentType(fragmentCD)
        if fragmentType == BlueprintTypes.VEHICLE:
            vehicleFragments[getVehicleCD(fragmentCD)] += count
        if fragmentType == BlueprintTypes.NATIONAL:
            nationID = fragmentCD & 255 if isFullNationCD else getFragmentNationID(fragmentCD)
            nationalFragments[nationID] += count
        if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
            intelligenceData += count

    return (vehicleFragments, nationalFragments, intelligenceData)


def _isUnsuitableForBlueprints(vehicle):
    return vehicle.isPremium or vehicle.isSecret or vehicle.isEvent or vehicle.isOnlyForEpicBattles or vehicle.isCollectible


class BlueprintsRequester(AbstractSyncDataRequester, IBlueprintsRequester):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(BlueprintsRequester, self).__init__()
        self.__vehicleFragments = {}
        self.__nationalFragments = {}
        self.__intelligence = defaultdict(int)

    def clear(self):
        self.__nationalFragments = {}
        self.__vehicleFragments = {}
        self.__intelligence = {}

    def getBlueprintCount(self, vehicleCD, vLevel):
        _logger.debug('Extract blueprint count for the vehicle=%s, level=%s ', vehicleCD, vLevel)
        totalCount = self._bpfConfig.getFragmentCount(vLevel)
        if vehicleCD in self.__itemsCache.items.stats.unlocks:
            return (totalCount, totalCount)
        filledCount = self.__vehicleFragments[vehicleCD].filledCount if vehicleCD in self.__vehicleFragments else 0
        return (filledCount, totalCount)

    def getBlueprintData(self, vehicleCD, vLevel):
        _logger.debug('Extract blueprint data for the vehicle=%s, level=%s ', vehicleCD, vLevel)
        if not self._bpfConfig.isBlueprintsAvailable():
            return None
        else:
            vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
            if _isUnsuitableForBlueprints(vehicle):
                return None
            filledCount, totalCount = self.getBlueprintCount(vehicleCD, vLevel)
            canConvert = False
            if filledCount != totalCount:
                canConvert = self.canConvertToVehicleFragment(vehicleCD, vLevel)
            return _BlueprintData(filledCount, totalCount, canConvert)

    def getBlueprintDiscount(self, vehicleCD, vLevel, potentialFilledCount=0):
        _logger.debug('getBlueprintDiscount: vehicle=%s, level=%s ', vehicleCD, vLevel)
        if not potentialFilledCount and (not self.__vehicleFragments or vehicleCD in self.__itemsCache.items.stats.unlocks or vehicleCD not in self.__vehicleFragments):
            return 0
        filledCount, totalCount = self.getBlueprintCount(vehicleCD, vLevel)
        filledCount = potentialFilledCount or filledCount
        if filledCount >= totalCount and filledCount != 0:
            return 100
        discount = self._bpfConfig.getFragmentDiscount(vLevel)
        return int(round(discount * filledCount * 100))

    def getRequiredCountAndDiscount(self, vehicleCD, vLevel):
        filledCount, totalCount = self.getBlueprintCount(vehicleCD, vLevel)
        requiredDiscount = self._bpfConfig.getFragmentDiscount(vLevel)
        if self.isLastFragment(totalCount, filledCount):
            requiredDiscount = 1 - filledCount * requiredDiscount
        return (totalCount, int(round(requiredDiscount * 100)))

    def getFragmentDiscountAndCost(self, vehicleCD, vLevel, xpFullCost):
        _, fragmentDiscount = self.getRequiredCountAndDiscount(vehicleCD, vLevel)
        return (fragmentDiscount, int(round(xpFullCost * fragmentDiscount * 0.01)))

    def getAllNationalFragmentsData(self):
        nationalFragments = {}
        for nationID, fragments in self.__nationalFragments.iteritems():
            nationalFragments[nationID] = sum(fragments.values())

        return nationalFragments

    def calculateCost(self, oldCost, discount):
        return oldCost if not discount else int(round(oldCost * (100 - discount) * 0.01))

    def getNationalFragments(self, fragmentCD):
        if not self.__nationalFragments:
            return 0
        nationID = getFragmentNationID(fragmentCD)
        return sum(self.__nationalFragments[nationID].values()) if nationID in self.__nationalFragments else 0

    def getNationalAllianceFragments(self, fragmentCD, vehicleLevel):
        allianceNationIds = sorted(self.__getAllyConversionCoefs(fragmentCD, vehicleLevel).keys())
        return OrderedDict(((nId, 0) for nId in allianceNationIds)) if not self.__nationalFragments else OrderedDict(((nId, sum(self.__nationalFragments[nId].values()) if nId in self.__nationalFragments else 0) for nId in allianceNationIds))

    def getNationalRequiredOptions(self, vehicleCD, vehicleLevel):
        national, _ = self.getRequiredIntelligenceAndNational(vehicleLevel)
        allyCoefs = self.__getAllyConversionCoefs(vehicleCD, vehicleLevel)
        return OrderedDict(((nId, round(national * allyCoef)) for nId, allyCoef in sorted(allyCoefs.iteritems())))

    def getIntelligenceCount(self):
        return 0 if not self.__intelligence else sum(self.__intelligence.values())

    def getRequiredIntelligenceAndNational(self, vehicleLevel):
        return self._bpfConfig.getRequiredFragmentsForConversion(vehicleLevel)

    def hasUniversalFragments(self):
        return bool(self.__intelligence or self.__nationalFragments)

    def isLastFragment(self, totalCount, filledCount):
        return totalCount - filledCount == 1

    def canConvertToVehicleFragment(self, vehicleCD, vehicleLevel):
        national, intelligence = self.getRequiredIntelligenceAndNational(vehicleLevel)
        if not national and not intelligence:
            return False
        existingIntelligence = self.getIntelligenceCount()
        if existingIntelligence < intelligence:
            return False
        existingAllianceFragments = self.getNationalAllianceFragments(vehicleCD, vehicleLevel)
        allyConversionCoefs = self.__getAllyConversionCoefs(vehicleCD, vehicleLevel)
        return any((existingAllianceFragments[nId] >= round(allyConversionCoefs[nId] * national) for nId in existingAllianceFragments.iterkeys()))

    def getConvertibleFragmentCount(self, vehicleCD, vehicleLevel):
        national, intelligence = self._bpfConfig.getRequiredFragmentsForConversion(vehicleLevel)
        if not national and not intelligence:
            return 0
        existingIntelligence = self.getIntelligenceCount()
        existingAlliance = self.getNationalAllianceFragments(vehicleCD, vehicleLevel)
        filledCount, totalCount = self.getBlueprintCount(vehicleCD, vehicleLevel)
        need = totalCount - filledCount
        availableIntelligence = int(existingIntelligence / intelligence) if intelligence else 0
        allyConversionCoefs = self.__getAllyConversionCoefs(vehicleCD, vehicleLevel)
        availableNational = sum((int(existingAlliance[nId] / round(national * allyConversionCoefs[nId])) for nId in existingAlliance.iterkeys()))
        return min((need, availableNational, availableIntelligence))

    def getLayout(self, vehicleCD, vLevel):
        if self.__vehicleFragments is None or self.__itemsCache.items.getItemByCD(vehicleCD).isPremium:
            return (0, 0, [])
        elif vehicleCD in self.__itemsCache.items.stats.unlocks:
            return self.__createLayoutData(vehicleCD, vLevel, True)
        else:
            layoutObject = self.__vehicleFragments.get(vehicleCD, None)
            if layoutObject is None:
                return self.__createLayoutData(vehicleCD, vLevel, False)
            layout = [ int(position) for position in layoutObject.layoutData ]
            rows = layoutObject.rows
            columns = layoutObject.columns
            return (rows, columns, layout)

    def isBlueprintsAvailable(self):
        return self._bpfConfig.isBlueprintsAvailable()

    def hasBlueprintsOrFragments(self):
        return bool(self.__vehicleFragments) or self.hasUniversalFragments()

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().blueprints.getCache(lambda resID, value: self._response(resID, value, callback))

    @property
    def _bpfConfig(self):
        return self.__lobbyContext.getServerSettings().blueprintsConfig

    def _preprocessValidData(self, data):
        _logger.debug('Preprocess blueprint cache')
        if data is None or 'cache' not in data:
            return data
        else:
            self.clear()
            blueprintsDecodeData = self.__bpfDecoder(data['cache'])
            if blueprintsDecodeData is not None:
                self.__vehicleFragments = blueprintsDecodeData[0]
                self.__nationalFragments = blueprintsDecodeData[1]
                self.__intelligence = blueprintsDecodeData[2]
            return data

    def __getAllyConversionCoefs(self, vehicleCD, vehicleLevel):
        nationId = getFragmentNationID(vehicleCD)
        coefs = copy(self._bpfConfig.getAllianceConversionCoeffs(vehicleLevel).get(nations.NATION_TO_ALLIANCE_IDS_MAP[nationId], {}))
        coefs[nationId] = 1
        return coefs

    def __createLayoutData(self, vehicleCD, vLevel, hasBlueprints):
        allLayout = Layout.LAYOUTS
        if vLevel in SPECIAL_BLUEPRINT_LEVEL:
            return _DEFAULT_LAYOUT
        else:
            fragments, _ = self.getRequiredCountAndDiscount(vehicleCD, vLevel)
            columns = allLayout.get(fragments, None)
            if columns is None:
                return (0, 0, ())
            rows = fragments / columns
            layout = [int(hasBlueprints)] * rows * columns
            return (rows, columns, layout)

    @classmethod
    def __bpfDecoder(cls, blueprintData):
        if blueprintData is None:
            return
        else:
            vehicleFragments = {}
            nationalFragments = {}
            intelligenceData = defaultdict(int)
            for fragmentCD, count in blueprintData.iteritems():
                fragmentType = getFragmentType(fragmentCD)
                if fragmentType == BlueprintTypes.VEHICLE:
                    vehicleCD = getVehicleCD(fragmentCD)
                    layout = Layout.fromInt(count)
                    vehicleFragments[vehicleCD] = layout
                if fragmentType == BlueprintTypes.NATIONAL:
                    vehicleCD = getVehicleCDForNational(fragmentCD)
                    nationID = getFragmentNationID(fragmentCD)
                    if nationID in nationalFragments:
                        nationalFragments[nationID].update({vehicleCD: count})
                    else:
                        nationalFragments[nationID] = {vehicleCD: count}
                if fragmentType == BlueprintTypes.INTELLIGENCE_DATA:
                    vehicleCD = getVehicleCDForIntelligence(fragmentCD)
                    intelligenceData[vehicleCD] += count

            return (vehicleFragments, nationalFragments, intelligenceData)
