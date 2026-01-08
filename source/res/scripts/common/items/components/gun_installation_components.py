# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/gun_installation_components.py
import typing
import shared_components
import component_constants
from constants import DEFAULT_GUN_INSTALLATION_INDEX
if typing.TYPE_CHECKING:
    from items.vehicle_items import Gun

class GunInstallationSlot(object):
    __slots__ = ('installationIndex', 'gun', '__objectSlots')

    def __init__(self, installationIndex, gun):
        self.installationIndex = installationIndex
        self.gun = gun
        self.__objectSlots = None
        return

    def __deepcopy__(self, memodict={}):
        return self

    def __repr__(self):
        return 'GunInstallationSlot(installationIndex={}, gun={})'.format(self.installationIndex, self.gun)

    @classmethod
    def isMainInstallationIndex(cls, installationIndex):
        return installationIndex == DEFAULT_GUN_INSTALLATION_INDEX

    @classmethod
    def getPartSlotNameByIndex(cls, installationIndex):
        return 'gun' if cls.isMainInstallationIndex(installationIndex) else 'gun{}'.format(installationIndex)

    @property
    def partSlotName(self):
        return self.getPartSlotNameByIndex(self.installationIndex)

    @property
    def slotPrefabs(self):
        mainPrefabs = self.gun.prefabs.get('default', {}).get('main', ())
        return self.gun.slotPrefabs + ([(self.partSlotName, mainPrefabs[0])] if mainPrefabs else [])

    @property
    def objectSlots(self):
        if self.__objectSlots is None:
            self.__objectSlots = self.__collectObjectSlots()
        return self.__objectSlots

    def isMainInstallation(self):
        return self.isMainInstallationIndex(self.installationIndex)

    def __collectObjectSlots(self):
        if self.isMainInstallation():
            return self.gun.objectSlots
        mainPrefabs = self.gun.prefabs.get('default', {}).get('main', ())
        if not mainPrefabs:
            return self.gun.objectSlots
        objectSlot = shared_components.ObjectSlot(name=self.partSlotName, type=component_constants.ObjectSlotType.ATTACHMENT, position=component_constants.ZERO_VECTOR3, rotation=component_constants.ZERO_VECTOR3)
        return self.gun.objectSlots + [objectSlot]
