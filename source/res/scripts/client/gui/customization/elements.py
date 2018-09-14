# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/customization/elements.py
import Math
import time
from collections import namedtuple
from constants import IGR_TYPE
from gui.game_control import getIGRCtrl
from helpers import time_utils
from helpers.i18n import makeString as _ms
from gui.customization.shared import BONUS_ICONS

class QualifierBase(object):

    def getIcon16x16(self):
        raise NotImplementedError

    def getDescription(self):
        raise NotImplementedError

    def getValue(self):
        raise NotImplementedError

    def getType(self):
        raise NotImplementedError

    def getName(self):
        raise NotImplementedError

    def getExtendedName(self):
        raise NotImplementedError

    def getIcon42x42(self):
        raise NotImplementedError

    def getFormattedValue(self):
        return '+{0}%'.format(self.getValue())


class CamouflageQualifier(QualifierBase):

    def __init__(self, camouflageType, bonusValue):
        super(CamouflageQualifier, self).__init__()
        self.__camouflageType = camouflageType
        self.__bonusValue = bonusValue

    def getIcon16x16(self):
        return BONUS_ICONS['16x16']['camouflage']

    def getIcon42x42(self):
        return BONUS_ICONS['42x42']['camouflage']

    def getDescription(self):
        return _ms('#vehicle_customization:qualifier/condition/map_kind_{0}'.format(self.__camouflageType))

    def getValue(self):
        return self.__bonusValue

    def getType(self):
        pass

    def getName(self):
        return _ms('#vehicle_customization:bonusName/camouflage')

    def getExtendedName(self):
        return _ms('#vehicle_customization:bonusName/extended/camouflage')


class Qualifier(QualifierBase):

    def __init__(self, rawData):
        self.__rawData = rawData

    def getIcon16x16(self):
        return BONUS_ICONS['16x16'][self.__rawData.qualifierType].format(self.__rawData.crewRole)

    def getIcon42x42(self):
        return BONUS_ICONS['42x42'][self.__rawData.qualifierType].format(self.__rawData.crewRole)

    def getDescription(self):
        if self.__rawData.conditionDescription:
            return _ms(self.__rawData.conditionDescription)
        else:
            return None
            return None

    def getValue(self):
        return self.__rawData.value

    def getType(self):
        return self.__rawData.crewRole

    def getName(self):
        return _ms('#vehicle_customization:bonusName/{0}'.format(self.__rawData.crewRole))

    def getExtendedName(self):
        return _ms('#vehicle_customization:bonusName/extended/{0}'.format(self.__rawData.crewRole))


class InstalledElement(namedtuple('InstalledElement', 'cType elementID duration installationTime spot')):

    @property
    def numberOfDaysLeft(self):
        timeLeft = (time.time() - self.installationTime) / time_utils.ONE_DAY
        if self.duration == 0:
            return 0
        else:
            return round(self.duration - timeLeft)


class Element(object):
    __slots__ = ('_rawData', '_qualifier', '_price', '__isInDossier', '__isInShop', '__isInQuests', '__itemID', '__nationID', '__allowedVehicles', '__notAllowedVehicles', '__allowedNations', '__notAllowedNations', '__igrReplaced', '__numberOfItems', '__numberOfDays', '__groupName')

    def __init__(self, params):
        self.__isInShop = params['isInShop']
        self.__isInDossier = params['isInDossier']
        self.__isInQuests = params['isInQuests']
        self.__itemID = params['itemID']
        self.__allowedVehicles = params['allowedVehicles']
        self.__notAllowedVehicles = params['notAllowedVehicles']
        self.__allowedNations = params['allowedNations']
        self.__notAllowedNations = params['notAllowedNations']
        self.__igrReplaced = params['isReplacedByIGR']
        self.__nationID = params['nationID']
        self.__groupName = params['readableGroupName']
        self.__numberOfItems = params['numberOfItems']
        self.__numberOfDays = params['numberOfDays']
        self._rawData = params['rawElement']
        self._qualifier = params['qualifier']
        self._price = params['price']

    def getID(self):
        return self.__itemID

    def getNationID(self):
        return self.__nationID

    def getGroupName(self):
        return self.__groupName

    def getTexturePath(self):
        raise NotImplementedError

    def getGroup(self):
        raise NotImplementedError

    def getName(self):
        raise NotImplementedError

    def getDescription(self):
        raise NotImplementedError

    def getIgrType(self):
        raise NotImplementedError

    def getPrice(self, duration):
        return int(round(self._getPrice(duration) * self._getVehiclePriceFactor() * self._getPriceFactor()))

    def getDefaultPrice(self, duration):
        return int(round(self._getDefaultPrice(duration) * self._getDefaultVehiclePriceFactor() * self._getDefaultPriceFactor()))

    def isOnSale(self, duration):
        return self.getDefaultPrice(duration) - self.getPrice(duration) > 0

    @property
    def qualifier(self):
        return self._qualifier

    @property
    def numberOfDays(self):
        return self.__numberOfDays

    @property
    def numberOfItems(self):
        return self.__numberOfItems

    @property
    def isReplacedByIGRItem(self):
        return self.__igrReplaced

    def isAllowedForCurrentVehicle(self, currentVehicle):
        intCD = currentVehicle.item.intCD
        cNationID = currentVehicle.item.descriptor.type.customizationNationID
        if self.__allowedNations and cNationID not in self.__allowedNations:
            return False
        if not self.__allowedVehicles and not self.__notAllowedVehicles:
            return True
        if self.__allowedVehicles:
            if intCD in self.__allowedVehicles:
                return True
            else:
                return False
        if self.__notAllowedVehicles:
            if intCD not in self.__notAllowedVehicles:
                return True
            else:
                return False
        return False

    @property
    def isInDossier(self):
        return self.__isInDossier or self.getIgrType() == getIGRCtrl().getRoomType() and getIGRCtrl().getRoomType() != IGR_TYPE.NONE

    @property
    def isInShop(self):
        return self.__isInShop

    @property
    def isInQuests(self):
        return self.__isInQuests

    @property
    def isFeatured(self):
        return False

    @property
    def allowedVehicles(self):
        return self.__allowedVehicles

    @property
    def notAllowedVehicles(self):
        return self.__notAllowedVehicles

    @property
    def allowedNations(self):
        return self.__allowedNations

    @property
    def notAllowedNations(self):
        return self.__notAllowedNations

    @property
    def isDisplayedFirst(self):
        return False

    def _getPrice(self, duration):
        return self._price['actual']['base'][duration][0]

    def _getDefaultPrice(self, duration):
        return self._price['default']['base'][duration][0]

    def _getPriceFactor(self):
        return self._price['actual']['factor'][self.getGroup()]

    def _getDefaultPriceFactor(self):
        return self._price['default']['factor'].get(self.getGroup(), 1)

    def _getVehiclePriceFactor(self):
        return self._price['actual']['vehicleFactor']

    def _getDefaultVehiclePriceFactor(self):
        return self._price['default']['vehicleFactor']


class Emblem(Element):
    __slots__ = ('_rawData', '_qualifier', '_price', '__isInDossier', '__isInShop', '__isInQuests', '__itemID', '__nationID', '__allowedVehicles', '__notAllowedVehicles', '__allowedNations', '__notAllowedNations', '__igrReplaced', '__numberOfItems', '__numberOfDays', '__groupName')

    def __init__(self, params):
        super(Emblem, self).__init__(params)

    def getTexturePath(self):
        return self._rawData[2].replace('gui/maps', '../maps')

    def getGroup(self):
        return self._rawData[0]

    def getName(self):
        return self._rawData[4]

    def getDescription(self):
        return None

    def getIgrType(self):
        return self._rawData[1]

    @property
    def isDisplayedFirst(self):
        return 'displayedFirst' in self._rawData[6]


class Inscription(Element):
    __slots__ = ('_rawData', '_qualifier', '_price', '__isInDossier', '__isInShop', '__isInQuests', '__itemID', '__nationID', '__allowedVehicles', '__notAllowedVehicles', '__allowedNations', '__notAllowedNations', '__igrReplaced', '__numberOfItems', '__numberOfDays', '__groupName')

    def __init__(self, params):
        super(Inscription, self).__init__(params)

    def getTexturePath(self):
        return self._rawData[2].replace('gui/maps', '../maps')

    def getGroup(self):
        return self._rawData[0]

    def getName(self):
        return self._rawData[4]

    def getDescription(self):
        return None

    def getIgrType(self):
        return self._rawData[1]

    @property
    def isFeatured(self):
        return self._rawData[5]

    @property
    def isDisplayedFirst(self):
        return 'displayedFirst' in self._rawData[6]


class Camouflage(Element):
    __slots__ = ('_rawData', '_qualifier', '_price', '__isInDossier', '__isInShop', '__isInQuests', '__itemID', '__nationID', '__allowedVehicles', '__notAllowedVehicles', '__allowedNations', '__notAllowedNations', '__igrReplaced', '__numberOfItems', '__numberOfDays', '__groupName')

    def __init__(self, params):
        super(Camouflage, self).__init__(params)

    def getTexturePath(self):
        colors = self._rawData.get('colors', (0, 0, 0, 0))
        weights = Math.Vector4((colors[0] >> 24) / 255.0, (colors[1] >> 24) / 255.0, (colors[2] >> 24) / 255.0, (colors[3] >> 24) / 255.0)
        return ('img://camouflage,{0:d},{1:d},"{2:>s}",{3[0]:d},{3[1]:d},' + '{3[2]:d},{3[3]:d},{4[0]:n},{4[1]:n},{4[2]:n},{4[3]:n},' + '{5:d}').format(128, 128, self._rawData['texture'], colors, weights, self._rawData.get('armorColor', 0))

    def getGroup(self):
        groupName = self._rawData['groupName']
        if getIGRCtrl().getRoomType() == IGR_TYPE.PREMIUM:
            groupName = groupName[3:] if groupName.startswith('IGR') else groupName
        return groupName

    def getName(self):
        return _ms('{}/label'.format(self._rawData['description']))

    def getDescription(self):
        return _ms('{}/description'.format(self._rawData['description']))

    def getIgrType(self):
        return self._rawData['igrType']

    def _getPriceFactor(self):
        return self._price['actual']['factor'][self.getID()]

    def _getDefaultPriceFactor(self):
        return self._price['default']['factor'][self.getID()]
