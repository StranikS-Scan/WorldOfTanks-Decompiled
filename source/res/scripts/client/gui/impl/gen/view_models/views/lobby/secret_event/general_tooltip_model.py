# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/general_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.secret_event.general_tooltip_list_item_model import GeneralTooltipListItemModel

class GeneralTooltipModel(ViewModel):
    __slots__ = ()
    READY = 'ready'
    IN_PLATOON = 'inPlatoon'
    IN_BATTLE = 'inBattle'
    DEFAULT = 'default'
    SHORT = 'short'
    STATIC = 'static'
    RESULT = 'result'

    def __init__(self, properties=12, commands=0):
        super(GeneralTooltipModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getResource(2)

    def setName(self, value):
        self._setResource(2, value)

    def getDescription(self):
        return self._getResource(3)

    def setDescription(self, value):
        self._setResource(3, value)

    def getProgress(self):
        return self._getNumber(4)

    def setProgress(self, value):
        self._setNumber(4, value)

    def getProgressMax(self):
        return self._getNumber(5)

    def setProgressMax(self, value):
        self._setNumber(5, value)

    def getGeneralLevel(self):
        return self._getNumber(6)

    def setGeneralLevel(self, value):
        self._setNumber(6, value)

    def getVehicleType(self):
        return self._getString(7)

    def setVehicleType(self, value):
        self._setString(7, value)

    def getOrderLabel(self):
        return self._getString(8)

    def setOrderLabel(self, value):
        self._setString(8, value)

    def getStatus(self):
        return self._getString(9)

    def setStatus(self, value):
        self._setString(9, value)

    def getVehicleList(self):
        return self._getArray(10)

    def setVehicleList(self, value):
        self._setArray(10, value)

    def getSkillList(self):
        return self._getArray(11)

    def setSkillList(self, value):
        self._setArray(11, value)

    def _initialize(self):
        super(GeneralTooltipModel, self)._initialize()
        self._addStringProperty('type', 'default')
        self._addNumberProperty('id', 0)
        self._addResourceProperty('name', R.invalid())
        self._addResourceProperty('description', R.invalid())
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('progressMax', 0)
        self._addNumberProperty('generalLevel', 0)
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('orderLabel', '')
        self._addStringProperty('status', '')
        self._addArrayProperty('vehicleList', Array())
        self._addArrayProperty('skillList', Array())
