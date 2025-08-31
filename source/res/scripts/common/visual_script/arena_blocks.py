# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/arena_blocks.py
import Math
from soft_exception import SoftException
from visual_script.block import Meta, Block, InitParam, buildStrKeysValue
from visual_script.misc import errorVScript, ASPECT, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE, arrayOf

class ArenaMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass


class GetUDOByNameBase(Block, ArenaMeta):
    _UDOTypes = []

    def __init__(self, *args, **kwargs):
        super(GetUDOByNameBase, self).__init__(*args, **kwargs)
        self._nameType, self._type, self._exclude = self._getInitParams()
        if self._nameType == 'single name':
            self._name = self._makeDataInputSlot('name', SLOT_TYPE.STR)
        elif self._nameType == 'multiple names':
            self._names = self._makeDataInputSlot('names', arrayOf(SLOT_TYPE.STR))
        elif self._nameType == 'any names':
            pass
        else:
            errorVScript(self, 'Unsupported name reference')
        self._UDOs = self._makeDataOutputSlot(self._type + 's', arrayOf(self._type), self._getAll)
        self._firstUDO = self._makeDataOutputSlot('first' + self._type, self._type, self._getFirst)

    @classmethod
    def initParams(cls):
        return [InitParam('UDO names', SLOT_TYPE.STR, buildStrKeysValue('single name', 'multiple names', 'any names'), EDITOR_TYPE.STR_KEY_SELECTOR), InitParam('UDO type', SLOT_TYPE.STR, buildStrKeysValue(*cls._UDOTypes), EDITOR_TYPE.STR_KEY_SELECTOR), InitParam('Exclude Names', SLOT_TYPE.BOOL, False)]

    @classmethod
    def blockIcon(cls):
        pass

    def captionText(self):
        if self._nameType == 'any names':
            return 'Get UDO'
        elif self._exclude:
            return 'Get UDO Excluding Name'
        else:
            return 'Get UDO By Name'

    def _getAll(self):
        self._UDOs.setValue(self._allValidUDOs())

    def _getFirst(self):
        udos = self._allValidUDOs()
        if udos:
            self._firstUDO.setValue(self._allValidUDOs()[0])
        else:
            raise SoftException("GetUDOByName block can't find a referred UDO by it name")

    def _getUDOsOfType(self, typeName):
        raise SoftException('Using the base GetUDOByNameBase class directly')

    def _allValidUDOs(self):
        allUDOs = self._getUDOsOfType(self._type)
        if self._nameType == 'single name':
            names = [self._name.getValue()]
        elif self._nameType == 'multiple names':
            names = self._names.getValue()
        else:
            if self._nameType == 'any names':
                return allUDOs
            return []
        if self._exclude:
            return [ udo for udo in allUDOs if udo.name not in names ]
        return [ udo for udo in allUDOs if udo.name in names ]


class GetDataFromStorageBase(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(GetDataFromStorageBase, self).__init__(*args, **kwargs)
        self.componentName, self._valueType = self._getInitParams()
        self.componentSlot = self._makeDataInputSlot('componentProperty', SLOT_TYPE.STR)
        self.componentSlot.setDefaultValue(self.componentName)
        if self.componentName == 'globalGoal':
            self._keySlot = self._makeDataInputSlot('key', SLOT_TYPE.STR)
        if self._valueType == SLOT_TYPE.STR:
            self._valueSlot = self._makeDataOutputSlot('value', SLOT_TYPE.STR, self._exec)
        elif self._valueType == SLOT_TYPE.INT:
            self._valueSlot = self._makeDataOutputSlot('value', SLOT_TYPE.INT, self._exec)
        elif self._valueType == SLOT_TYPE.FLOAT:
            self._valueSlot = self._makeDataOutputSlot('value', SLOT_TYPE.FLOAT, self._exec)

    @classmethod
    def initParams(cls):
        return [InitParam('Component property name', SLOT_TYPE.STR, buildStrKeysValue('globalGoal'), EDITOR_TYPE.STR_KEY_SELECTOR), InitParam('Value Types', SLOT_TYPE.STR, buildStrKeysValue(SLOT_TYPE.STR, SLOT_TYPE.FLOAT, SLOT_TYPE.INT), EDITOR_TYPE.STR_KEY_SELECTOR)]

    def _exec(self):
        storage = self.arena.arenaInfo.mapsTrainingStorageComponent
        if self.componentName == 'globalGoal':
            self._valueSlot.setValue(storage.getGlobalGoal(self._keySlot.getValue()))


class GetFlyDirection(Block, ArenaMeta):

    def __init__(self, *args, **kwargs):
        super(GetFlyDirection, self).__init__(*args, **kwargs)
        self._arena = self._makeDataInputSlot('arena', SLOT_TYPE.ARENA)
        self._teamID = self._makeDataInputSlot('teamID', SLOT_TYPE.INT)
        self._res = self._makeDataOutputSlot('flyDirection', SLOT_TYPE.VECTOR3, self._exec)

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]

    def _exec(self):
        arena = self._arena.getValue()
        teamID = self._teamID.getValue()
        direction = None
        arenaType = arena.arenaType
        reconSettings = getattr(arenaType, 'recon')
        if reconSettings is not None:
            direction = reconSettings.flyDirections.get(teamID)
        if direction is None:
            errorVScript(self, 'Missing flyDirection for arena [geometryName={}, gameplayName={}]; teamID={}'.format(arenaType.geometryName, arenaType.gameplayName, teamID))
            direction = Math.Vector3(1.0, 0.0, 0.0)
        self._res.setValue(direction)
        return
