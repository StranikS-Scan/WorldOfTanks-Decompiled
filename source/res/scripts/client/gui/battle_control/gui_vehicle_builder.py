# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/gui_vehicle_builder.py
from gui.veh_post_progression.helpers import getInstalledShells, setFeatures, setDisabledSwitches, updateInvInstalled
from helpers import dependency
from items import vehicles
from battle_modifiers_common import EXT_DATA_MODIFIERS_KEY
from post_progression_common import EXT_DATA_PROGRESSION_KEY, EXT_DATA_SLOT_KEY, VehicleState
from skeletons.gui.shared.gui_items import IGuiItemsFactory

class VehicleBuilder(object):
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)

    def __init__(self):
        self.__invData = None
        self.__extData = None
        self.__strCD = None
        return

    def setStrCD(self, strCD):
        self.__strCD = strCD

    def setCrew(self, crewCDs):
        self.__assertNotSet(self.__invData, 'battleCrewCDs')
        self.__setInvData('battleCrewCDs', crewCDs)

    def setShells(self, strCD, vehSetups):
        self.__assertNotSet(self.__invData, {'shells', 'shellsLayout'})
        vehDescr = vehicles.VehicleDescr(compactDescr=strCD)
        gunDescr = vehDescr.gun
        shellsCDs = vehicles.getDefaultAmmoForGun(gunDescr)[::2]
        shellsLayoutKey = (vehDescr.turret.compactDescr, gunDescr.compactDescr)
        self.__updateInvData({'shells': getInstalledShells(shellsCDs, vehSetups['shellsSetups']),
         'shellsLayout': {shellsLayoutKey: vehSetups['shellsSetups']}})

    def setAmmunitionSetups(self, vehSetups, setupIndexes):
        self.__assertNotSet(self.__invData, {'eqsLayout',
         'boostersLayout',
         'devicesLayout',
         'layoutIndexes'})
        setupData = {'eqsLayout': vehSetups['eqsSetups'],
         'boostersLayout': vehSetups['boostersSetups'],
         'devicesLayout': vehSetups['devicesSetups'],
         'layoutIndexes': setupIndexes}
        updateInvInstalled(setupData, setupIndexes)
        self.__updateInvData(setupData)

    def setRoleSlot(self, slotID):
        self.__assertNotSet(self.__extData, EXT_DATA_SLOT_KEY)
        self.__setExtData(EXT_DATA_SLOT_KEY, slotID)

    def setPostProgressionState(self, vehPostProgression, disabledSwitchGroupIDs):
        self.__assertNotSet(self.__extData, EXT_DATA_PROGRESSION_KEY)
        vehState = VehicleState()
        setFeatures(vehState, vehPostProgression)
        setDisabledSwitches(vehState, disabledSwitchGroupIDs)
        self.__setExtData(EXT_DATA_PROGRESSION_KEY, vehState)

    def setModifiers(self, modifiers):
        self.__assertNotSet(self.__extData, EXT_DATA_MODIFIERS_KEY)
        self.__setExtData(EXT_DATA_MODIFIERS_KEY, modifiers)

    def setSettings(self, settings):
        self.__assertNotSet(self.__invData, 'settings')
        self.__setInvData('settings', settings)

    def getResult(self):
        extData = self.__extData.copy() if self.__extData is not None else None
        vehicle = self.__itemsFactory.createVehicle(self.__strCD, extData=extData, invData=self.__invData)
        if self.__extData and EXT_DATA_PROGRESSION_KEY in self.__extData:
            vehicle.installPostProgressionItem(self.__itemsFactory.createVehPostProgression(vehicle.compactDescr, self.__extData[EXT_DATA_PROGRESSION_KEY], vehicle.typeDescr))
        return vehicle

    def __setInvData(self, key, value):
        if self.__invData is None:
            self.__invData = {}
        self.__invData[key] = value
        return

    def __setExtData(self, key, value):
        if self.__extData is None:
            self.__extData = {}
        self.__extData[key] = value
        return

    def __updateInvData(self, source):
        if self.__invData is None:
            self.__invData = {}
        self.__invData.update(source)
        return

    @staticmethod
    def __assertNotSet--- This code section failed: ---

 109       0	LOAD_FAST         'target'
           3	LOAD_CONST        ''
           6	COMPARE_OP        'is'
           9	POP_JUMP_IF_FALSE '16'

 110      12	LOAD_CONST        ''
          15	JUMP_FORWARD      37

 112      16	LOAD_GLOBAL       'isinstance'
          19	LOAD_FAST         'keys'
          22	LOAD_GLOBAL       'set'
          25	CALL_FUNCTION_2   ''
          28	POP_JUMP_IF_FALSE '34'

 113      31	JUMP_FORWARD      '34'
        34_0	COME_FROM         '31'

 115      34	LOAD_CONST        ''
        37_0	COME_FROM         '15'
          37	RETURN_VALUE      ''

Syntax error at or near 'COME_FROM' token at offset 34_0