# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/battle/battle_page/ammunition_panel/prebattle_ammunition_vehicle_mock.py
import typing
from gui.shared.gui_items.Vehicle import NOT_FULL_AMMO_MULTIPLIER
from gui.shared.gui_items.gui_item import HasIntCD
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from items import vehicles
    from gui.battle_control.controllers.vehicle_post_progression_ctrl import _BattlePostProgression

class PrbAmmunitionVehicleMock(object):
    __slots__ = ('_key', '_layoutIndexes', '_equipments', '_descriptor', '_postProgression', '_intCD', '_isElite', '_inventoryCount', '_itemTypeID')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, key=None):
        super(PrbAmmunitionVehicleMock, self).__init__()
        self._key = None
        self._descriptor = None
        self._layoutIndexes = None
        self._equipments = None
        self._postProgression = None
        self._intCD = None
        self._isElite = False
        self._inventoryCount = 0
        return

    def initialize(self):
        pass

    def finalize(self):
        self._equipments = None
        self._descriptor = None
        self._postProgression = None
        return

    def vehicleUpdate(self, descriptor, eq, vehPostProgression):
        self._descriptor = descriptor
        self._equipments = eq
        self._intCD = HasIntCD(descriptor.type.compactDescr)
        self._postProgression = vehPostProgression

    @property
    def crew(self):
        return []

    def isSetupSwitchAvailable(self, groupID):
        return self.postProgression.isSetupSwitchAvailable(groupID)

    @property
    def setupLayouts(self):
        return self._equipments.setupLayouts

    @property
    def optDevices(self):
        return self._equipments.optDevices

    @property
    def shells(self):
        return self._equipments.shells

    @property
    def consumables(self):
        return self._equipments.consumables

    @property
    def battleBoosters(self):
        return self._equipments.battleBoosters

    @property
    def battleAbilities(self):
        return self._equipments.battleAbilities

    @property
    def level(self):
        arenaDP = self.sessionProvider.getCtx().getArenaDP()
        _, level, __ = arenaDP.getVehicleInfo().getTypeInfo()
        return level

    @property
    def ammoMinSize(self):
        return self._descriptor.gun.maxAmmo * NOT_FULL_AMMO_MULTIPLIER

    @property
    def compactDescr(self):
        return self._descriptor.type.compactDescr

    @property
    def typeDescr(self):
        return self._descriptor.type

    @property
    def postProgression(self):
        return self._postProgression

    @property
    def intCD(self):
        return self._intCD.intCompactDescr if self._intCD is not None else 0

    @property
    def itemTypeID(self):
        return self._intCD.itemTypeID if self._intCD is not None else 0
