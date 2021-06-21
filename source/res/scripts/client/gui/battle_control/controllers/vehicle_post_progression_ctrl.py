# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicle_post_progression_ctrl.py
import logging
import BigWorld
import Event
from constants import ARENA_PERIOD
from gui.shared.gui_items.Tankman import isSkillLearnt
from gui.shared.gui_items.vehicle_equipment import VehicleEquipment
from items.components.post_progression_components import getFeatures
from post_progression_common import GROUP_ID_BY_LAYOUT, TANK_SETUP_GROUPS, FEATURE_BY_GROUP_ID, ROLESLOT_FEATURE, TankSetupLayouts, TankSetups
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared.gui_items import checkForTags
from gui.shared.gui_items.artefacts import TAG_OPT_DEVICE_TROPHY_BASIC, TAG_OPT_DEVICE_TROPHY_UPGRADED, TAG_OPT_DEVICE_DELUXE, TAG_CREW_BATTLE_BOOSTER, TAG_EQUEPMENT_BUILTIN
from gui.battle_control.controllers.interfaces import IBattleController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from items import vehicles, EQUIPMENT_TYPES
from skeletons.gui.shared.gui_items import IGuiItemsFactory
_logger = logging.getLogger(__name__)
_SWITCH_SETUP_COOLDOWN = 0.5
_LAYOUT_TO_INSTALLED = ((TankSetupLayouts.SHELLS, 'shells'), (TankSetupLayouts.EQUIPMENT, 'eqs'), (TankSetupLayouts.BATTLE_BOOSTERS, 'boosters'))
_SETUP_NAME_MAP = {TankSetups.OPTIONAL_DEVICES: TankSetupLayouts.OPTIONAL_DEVICES,
 TankSetups.SHELLS: TankSetupLayouts.SHELLS,
 TankSetups.EQUIPMENT: TankSetupLayouts.EQUIPMENT,
 TankSetups.BATTLE_BOOSTERS: TankSetupLayouts.BATTLE_BOOSTERS}

class SetupResponseCode(object):
    SUCCESS, FAILURE, WRONG_ARENA_PERIOD, COOLDOWN, DESTROYED_VEHICLE = range(1, 6)


class _EquipmentItem(object):
    __slots__ = ('_descriptor', '_tags', '_intCD')

    def __init__(self, descriptor, tags):
        super(_EquipmentItem, self).__init__()
        self._descriptor = descriptor
        self._tags = tags
        self._intCD = self._descriptor.compactDescr

    @property
    def descriptor(self):
        return self._descriptor

    @property
    def intCD(self):
        return self._intCD

    @property
    def isBuiltIn(self):
        return TAG_EQUEPMENT_BUILTIN in self._tags

    def clear(self):
        self._descriptor = None
        return

    def getTags(self):
        return self._tags


class _ShellItem(_EquipmentItem):
    __slots__ = ('_count',)

    def __init__(self, descriptor, tags, count):
        super(_ShellItem, self).__init__(descriptor, tags)
        self._count = count

    @property
    def count(self):
        return self._count


class _OptDeviceItem(_EquipmentItem):

    @property
    def isUpgradable(self):
        return checkForTags(self._tags, TAG_OPT_DEVICE_TROPHY_BASIC)

    @property
    def isUpgraded(self):
        return checkForTags(self._tags, TAG_OPT_DEVICE_TROPHY_UPGRADED)

    @property
    def isDeluxe(self):
        return checkForTags(self._tags, TAG_OPT_DEVICE_DELUXE)

    @property
    def isTrophy(self):
        return checkForTags(self._tags, (TAG_OPT_DEVICE_TROPHY_BASIC, TAG_OPT_DEVICE_TROPHY_UPGRADED))

    @property
    def isRegular(self):
        return not checkForTags(self._tags, (TAG_OPT_DEVICE_TROPHY_BASIC, TAG_OPT_DEVICE_TROPHY_UPGRADED, TAG_OPT_DEVICE_DELUXE))


class _BattleBoosterDeviceItem(_EquipmentItem):

    def isAffectsOnVehicle(self, vehicle):
        if self.isCrewBooster():
            return True
        for device in vehicle.optDevices.installed:
            if self.isOptionalDeviceCompatible(device):
                return True

        return False

    def isCrewBooster(self):
        return TAG_CREW_BATTLE_BOOSTER in self._tags

    def isOptionalDeviceCompatible(self, optionalDevice):
        return not self.isCrewBooster() and optionalDevice is not None and self.descriptor.getLevelParamsForDevice(optionalDevice.descriptor) is not None

    def isAffectedSkillLearnt(self, vehicle=None):
        return isSkillLearnt(self.getAffectedSkillName(), vehicle) if vehicle is not None else False

    def getAffectedSkillName(self):
        return self.descriptor.skillName if self.isCrewBooster() else None


class _VehicleGun(object):
    __slots__ = ('_descriptor', '_defaultAmmo', '_maxAmmo')

    def __init__(self, proxy=None, descriptor=None):
        super(_VehicleGun, self).__init__()
        self._descriptor = descriptor
        self._defaultAmmo = self._getDefaultAmmo(proxy)
        self._maxAmmo = self._getMaxAmmo()

    @property
    def defaultAmmo(self):
        return self._defaultAmmo

    @property
    def maxAmmo(self):
        return self._maxAmmo

    def _getDefaultAmmo(self, proxy):
        result = []
        shells = vehicles.getDefaultAmmoForGun(self._descriptor)
        for i in range(0, len(shells), 2):
            descriptor = vehicles.getItemByCompactDescr(shells[i])
            result.append(_ShellItem(descriptor, None, shells[i + 1]))

        return result

    def _getMaxAmmo(self):
        return self._descriptor.maxAmmo


class BattleEquipmentsFactory(IGuiItemsFactory):

    def clear(self):
        pass

    def createGuiItem(self, itemTypeIdx, *args, **kwargs):
        pass

    def createGuiItemFromCompactDescr(self, compactDescr, *args, **kwargs):
        pass

    def createEquipment(self, intCompactDescr, proxy=None, isBoughtForCredits=False):
        descriptor = vehicles.getItemByCompactDescr(intCompactDescr)
        return _BattleBoosterDeviceItem(descriptor, descriptor.tags) if descriptor.equipmentType == EQUIPMENT_TYPES.battleBoosters else _EquipmentItem(descriptor, descriptor.tags)

    def createShell(self, intCompactDescr, count=0, proxy=None, isBoughtForCredits=False):
        descriptor = vehicles.getItemByCompactDescr(intCompactDescr)
        return _ShellItem(descriptor, descriptor.tags, count)

    def createOptionalDevice(self, intCompactDescr, proxy=None):
        descriptor = vehicles.getItemByCompactDescr(intCompactDescr)
        return _OptDeviceItem(descriptor, descriptor.tags)

    def createVehicleGun(self, intCompactDescr, proxy=None, descriptor=None):
        return _VehicleGun(proxy, descriptor)

    def createVehicleChassis(self, intCompactDescr, proxy=None, descriptor=None):
        pass

    def createVehicleTurret(self, intCompactDescr, proxy=None, descriptor=None):
        pass

    def createVehicleEngine(self, intCompactDescr, proxy=None, descriptor=None):
        pass

    def createVehicleRadio(self, intCompactDescr, proxy=None, descriptor=None):
        pass

    def createVehicleFuelTank(self, intCompactDescr, proxy=None, descriptor=None):
        pass

    def createVehicle(self, strCompactDescr=None, inventoryID=-1, typeCompDescr=None, proxy=None, extData=None):
        pass

    def createTankman(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None):
        pass

    def createTankmanDossier(self, tmanDescr, tankmanDossierDescr, extDossier, playerDBID=None, currentVehicleItem=None):
        pass

    def createAccountDossier(self, dossier, playerDBID=None, rated7x7Seasons=None):
        pass

    def createVehicleDossier(self, dossier, vehTypeCompDescr, playerDBID=None):
        pass

    def createBadge(self, descriptor, proxy=None, extraData=None):
        pass

    def createLootBox(self, lootBoxID, lootBoxConfig, count):
        pass

    def createCustomization(self, intCompactDescr, proxy=None):
        pass

    def createOutfit(self, strCompactDescr=None, component=None, vehicleCD=''):
        pass

    def createVehPostProgression(self, vehIntCD, state, vehType):
        pass


class _BattlePostProgression(object):
    __slots__ = ('_features',)

    def __init__(self):
        self._features = None
        return

    def update(self, features):
        self._features = features

    @property
    def isPostProgressionEnabled(self):
        if not ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arenaBonusType, ARENA_BONUS_TYPE_CAPS.SWITCH_SETUPS):
            return False
        for groupID in TANK_SETUP_GROUPS.iterkeys():
            if self.isSetupSwitchAvailable(groupID):
                return True

        return False

    def isSetupSwitchAvailable(self, groupID):
        return FEATURE_BY_GROUP_ID[groupID] in self._features if groupID is not None and self._features is not None else False

    def isFeatureEnabled(self, featureName):
        return featureName in self._features if featureName is not None and self._features is not None else False

    def isRoleSlotAvailable(self):
        return self.isFeatureEnabled(ROLESLOT_FEATURE)


class VehiclePostProgressionBattleController(IBattleController):
    __slots__ = ('__vehID', '__vehicle', '__invData', '__setups', '__setupsIndexes', '__postProgression', '__setupEquipments', '__switchCallbackID', 'onSetupUpdated')
    __guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, setup):
        super(VehiclePostProgressionBattleController, self).__init__()
        self.__vehID = None
        self.__vehicle = None
        self.__setups = None
        self.__setupsIndexes = None
        self.__invData = None
        self.__setupEquipments = None
        self.__postProgression = None
        self.__switchCallbackID = None
        self.onSetupUpdated = Event.Event()
        return

    @property
    def setupEquipments(self):
        return self.__setupEquipments

    @property
    def playerVehicle(self):
        return self.__vehicle

    @property
    def postProgression(self):
        return self.__postProgression

    def getControllerID(self):
        return BATTLE_CTRL_ID.VEHICLE_POST_PROGRESSION_CTRL

    def startControl(self):
        self.__postProgression = _BattlePostProgression()

    def stopControl(self):
        self.clear()

    def clear(self):
        if self.__switchCallbackID is not None:
            BigWorld.cancelCallback(self.__switchCallbackID)
            self.__switchCallbackID = None
        self.__postProgression = None
        self.__setupEquipments = None
        self.__vehicle = None
        if self.__setups:
            self.__setups.clear()
        if self.__invData:
            self.__invData.clear()
        return

    def setupVehicle(self, vID):
        if self.__vehID == vID:
            return
        else:
            self.__vehID = vID
            vehicle = BigWorld.entity(vID)
            if vehicle is not None:
                self.__vehicle = vehicle
                self.__updateSetupsData()
            return

    def setSetups(self, setups):
        self.__setups = {_SETUP_NAME_MAP.get(key, key):value for key, value in setups.iteritems()}
        self.__updateSetupsData()

    def setIndexes(self, setupsIndexes):
        self.__setupsIndexes = setupsIndexes
        self.__updateSetupsData()

    def setPostProgressionStatus(self, vehPostProgression):
        if vehPostProgression is not None:
            vppCache = vehicles.g_cache.postProgression()
            self.__postProgression.update(getFeatures(vehPostProgression, vppCache))
            self.__updateSetup()
        return

    def switchLayout(self, groupID, layoutIdx):
        avatar = BigWorld.player()
        responseCode = self.__canActivate(avatar)
        if responseCode == SetupResponseCode.SUCCESS:
            avatar.vehicle.cell.switchSetup(groupID, layoutIdx)
            return True
        return False

    def __canActivate(self, avatar):
        if avatar is None:
            return SetupResponseCode.FAILURE
        else:
            ctrl = self.__guiSessionProvider.shared.arenaPeriod
            if ctrl.getPeriod() != ARENA_PERIOD.PREBATTLE:
                return SetupResponseCode.WRONG_ARENA_PERIOD
            vehicle = avatar.vehicle
            if not vehicle or avatar.vehicle.health <= 0:
                return SetupResponseCode.DESTROYED_VEHICLE
            ctrl = self.__guiSessionProvider.shared.vehicleState
            if avatar.isObserver() or ctrl.isInPostmortem:
                return SetupResponseCode.DESTROYED_VEHICLE
            if self.__switchCallbackID is not None:
                return SetupResponseCode.COOLDOWN
            self.__switchCallbackID = BigWorld.callback(_SWITCH_SETUP_COOLDOWN, self.__switchCooldownCompleted)
            return SetupResponseCode.SUCCESS

    def __switchCooldownCompleted(self):
        self.__switchCallbackID = None
        return

    def __updateSetupsData(self):
        if self.__setups is None or self.__setupsIndexes is None or self.__vehicle is None:
            return
        else:
            self.__invData = self.__setups.copy()
            self.__invData.update({'layoutIndexes': self.__setupsIndexes})
            for layoutID, equipmentType in _LAYOUT_TO_INSTALLED:
                self.__updateInstalled(self.__invData, equipmentType, layoutID)

            shellsLayout = self.__invData.get(TankSetupLayouts.SHELLS, None)
            if shellsLayout is not None:
                vehDescr = self.__vehicle.typeDescriptor
                shellsLayoutKey = (vehDescr.turret.compactDescr, vehDescr.gun.compactDescr)
                self.__invData[TankSetupLayouts.SHELLS] = {shellsLayoutKey: shellsLayout}
            self.__updateSetup()
            return

    def __updateInstalled(self, invData, key, layoutName):
        groupID = GROUP_ID_BY_LAYOUT.get(layoutName, 0)
        setupIdx = invData['layoutIndexes'].get(groupID, 0)
        data = invData[layoutName]
        installed = data[setupIdx] if setupIdx < len(data) else []
        installed = installed[:]
        if layoutName == TankSetupLayouts.SHELLS:
            for idx in range(0, len(installed), 2):
                shell = installed[idx]
                count = 0
                for layout in data:
                    if shell in layout:
                        count = max(count, layout[layout.index(shell) + 1])

                installed[idx + 1] = count

        invData.update({key: installed})

    def __updateSetup(self):
        if self.__postProgression.isPostProgressionEnabled is False or self.__vehicle is None or self.__invData is None:
            return
        else:
            vehDescr = self.__vehicle.typeDescriptor
            factory = BattleEquipmentsFactory()
            self.__setupEquipments = VehicleEquipment(None, vehDescr, self.__invData, factory)
            self.onSetupUpdated()
            return
