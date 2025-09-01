# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/gun_installation_components.py
import typing
from constants import DEFAULT_GUN_INSTALLATION_INDEX
if typing.TYPE_CHECKING:
    from items.vehicle_items import Gun

class GunInstallationSlot(object):
    __slots__ = ('installationIndex', 'gun')

    def __init__(self, installationIndex, gun):
        self.installationIndex = installationIndex
        self.gun = gun

    def __deepcopy__(self, memodict={}):
        return self

    def __repr__(self):
        return 'GunInstallationSlot(installationIndex={}, gun={})'.format(self.installationIndex, self.gun)

    def isMainInstallation(self):
        return self.installationIndex == DEFAULT_GUN_INSTALLATION_INDEX
