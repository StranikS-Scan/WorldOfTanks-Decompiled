# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/post_progression_common.py
from typing import Dict, Set, List, Callable, Optional, TYPE_CHECKING
from copy import copy
if TYPE_CHECKING:
    from items.components.post_progression_components import ProgressionTree
SERVER_SETTINGS_KEY = 'vehicle_post_progression_config'
EXT_DATA_SLOT_KEY = 'customRoleSlotTypeId'
EXT_DATA_PROGRESSION_KEY = 'vehPostProgression'
SETUPS_FEATURES = ('shells_consumables_switch', 'opt_dev_boosters_switch')
ROLESLOT_FEATURE = 'roleSlot'
FEATURES_NAMES = SETUPS_FEATURES + (ROLESLOT_FEATURE,)
ID_THRESHOLD = 16384

class ACTION_TYPES:
    MODIFICATION = 1
    PAIR_MODIFICATION = 2
    FEATURE = 3


class PAIR_TYPES:
    NOT_SET = 0
    FIRST = 1
    SECOND = 2


class TankSetupLayouts(object):
    OPTIONAL_DEVICES = 'devicesLayout'
    EQUIPMENT = 'eqsLayout'
    SHELLS = 'shellsLayout'
    BATTLE_BOOSTERS = 'boostersLayout'


class TankSetups(object):
    OPTIONAL_DEVICES = 'devicesSetups'
    EQUIPMENT = 'eqsSetups'
    SHELLS = 'shellsSetups'
    BATTLE_BOOSTERS = 'boostersSetups'


class TankSetupGroupsId(object):
    EQUIPMENT_AND_SHELLS = 1
    OPTIONAL_DEVICES_AND_BOOSTERS = 2


TANK_SETUP_GROUPS = {TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS: (TankSetupLayouts.OPTIONAL_DEVICES, TankSetupLayouts.BATTLE_BOOSTERS),
 TankSetupGroupsId.EQUIPMENT_AND_SHELLS: (TankSetupLayouts.EQUIPMENT, TankSetupLayouts.SHELLS)}
MAX_LAYOUTS_NUMBER_ON_VEHICLE = {TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS: 2,
 TankSetupGroupsId.EQUIPMENT_AND_SHELLS: 2}
GROUP_ID_BY_LAYOUT = {layout:groupName for groupName, layouts in TANK_SETUP_GROUPS.iteritems() for layout in layouts}
FEATURE_BY_GROUP_ID = {TankSetupGroupsId.EQUIPMENT_AND_SHELLS: 'shells_consumables_switch',
 TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS: 'opt_dev_boosters_switch'}

def extractSelectedSetup(setups, setupsIndexes):
    selectedSetup = {}
    for tankSetupId, tankSetupGroup in TANK_SETUP_GROUPS.iteritems():
        chosenIndex = setupsIndexes.get(tankSetupId, 0)
        for tankSetupLayout in tankSetupGroup:
            tankSetups = tankSetupLayout.replace('Layout', 'Setups')
            layout = setups[tankSetups]
            selectedSetup[tankSetups] = layout[chosenIndex] if chosenIndex < len(layout) else []

    return selectedSetup


def makeActionCompDescr(actionType, itemId, subId=0):
    actionType = int(actionType)
    return subId << 18 | itemId << 4 | actionType


def makeDefaultSetupsIndexes():
    return {TankSetupGroupsId.OPTIONAL_DEVICES_AND_BOOSTERS: 0,
     TankSetupGroupsId.EQUIPMENT_AND_SHELLS: 0}


def makeDefaultSetupsInVehicle():
    return {TankSetups.SHELLS: [[]],
     TankSetups.BATTLE_BOOSTERS: [[]],
     TankSetups.EQUIPMENT: [[]],
     TankSetups.OPTIONAL_DEVICES: [[]]}


def parseActionCompDescr(compDescr):
    actionType = compDescr & 15
    itemID = compDescr >> 4 & ID_THRESHOLD - 1
    subId = compDescr >> 18 & ID_THRESHOLD - 1
    return (actionType, itemID, subId)


class VehicleState(object):
    __slots__ = ('_unlocks', '_pairs', '_features')

    def __init__(self, data=None):
        data = data or self.getDefaultState()
        self._unlocks = copy(data['unlocks'])
        self._pairs = copy(data['pairs'])
        self._features = copy(data['features'])

    def __eq__(self, other):
        return self.unlocks == other.unlocks and self.pairs == other.pairs and self.features == other.features

    def __or__(self, other):
        result = VehicleState(self.toRawData())
        for stepID in other.unlocks:
            result.addUnlock(stepID)

        for stepID, pairTypeID in other.pairs.iteritems():
            result.setPair(stepID, pairTypeID)

        for featureID in other.features:
            result.addFeature(featureID)

        return result

    @property
    def unlocks(self):
        return self._unlocks

    @property
    def pairs(self):
        return self._pairs

    @property
    def features(self):
        return self._features

    def isUnlocked(self, stepID):
        return stepID in self._unlocks

    def addUnlock(self, stepID):
        self._unlocks.add(stepID)

    def removeUnlock(self, stepID):
        self._unlocks.discard(stepID)

    def setPair(self, stepID, pairTypeID):
        self._pairs[stepID] = pairTypeID

    def getPair(self, stepID):
        return self._pairs.get(stepID)

    def removePair(self, stepID):
        self._pairs.pop(stepID, None)
        return

    def hasFeature(self, featureID):
        return featureID in self._features

    def addFeature(self, featureID):
        self._features.add(featureID)

    def removeFeature(self, featureID):
        self._features.discard(featureID)

    def clean(self, removeUnlocks=True, removePairs=True, removeFeatures=True):
        if removeUnlocks:
            self._unlocks = VehicleState.__getDefaultUnlocksState()
        if removePairs:
            self._pairs = VehicleState.__getDefaultPairsState()
        if removeFeatures:
            self._features = VehicleState.__getDefaultFeaturesState()

    def isEmpty(self):
        return not self.unlocks and not self.pairs and not self.features

    def toActionCDs(self, tree):
        result = []
        for stepID in self._unlocks:
            actionID, itemID = tree.steps[stepID].action
            subId = self._pairs.get(stepID, PAIR_TYPES.NOT_SET) if actionID == ACTION_TYPES.PAIR_MODIFICATION else 0
            result.append(makeActionCompDescr(actionID, itemID, subId))

        return result

    def toRawData(self):
        return {'unlocks': self._unlocks,
         'pairs': self._pairs,
         'features': self._features}

    @staticmethod
    def getDefaultState():
        return {'unlocks': VehicleState.__getDefaultUnlocksState(),
         'pairs': VehicleState.__getDefaultPairsState(),
         'features': VehicleState.__getDefaultFeaturesState()}

    @staticmethod
    def __getDefaultUnlocksState():
        return set()

    @staticmethod
    def __getDefaultPairsState():
        return dict()

    @staticmethod
    def __getDefaultFeaturesState():
        return set()


class VehiclesPostProgression(object):
    __slots__ = ('__data', '__dataW')
    ROOT_KEY = 'postProgression'

    def __init__(self, data, syncData=None):
        self.__data = data
        self.__dataW = syncData

    @property
    def _storage(self):
        return self.__data[self.ROOT_KEY]

    @property
    def _storageW(self):
        return self.__dataW()[self.ROOT_KEY]

    def getVehicleState(self, vehTypeCD):
        return VehicleState(self._storage.get(vehTypeCD))

    def setVehicleState(self, vehTypeCD, vehicleState):
        if vehicleState.isEmpty():
            self._storageW.pop(vehTypeCD, None)
        else:
            self._storage[vehTypeCD] = vehicleState.toRawData()
            self._storageW[vehTypeCD].reset()
        return

    def removeVehicleState(self, vehTypeCD):
        self._storageW.pop(vehTypeCD, None)
        return

    def clean(self):
        self.__dataW()[self.ROOT_KEY] = self.getDefaultStorage()

    @staticmethod
    def getDefaultStorage():
        return dict()
