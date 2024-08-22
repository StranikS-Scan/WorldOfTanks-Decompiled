# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_preview/tabs/tankman_preview_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_list_model import CrewSkillListModel

class TankmanPreviewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(TankmanPreviewModel, self).__init__(properties=properties, commands=commands)

    @property
    def skills(self):
        return self._getViewModel(0)

    @staticmethod
    def getSkillsType():
        return CrewSkillListModel

    def getSlotIdx(self):
        return self._getNumber(1)

    def setSlotIdx(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getRoles(self):
        return self._getArray(4)

    def setRoles(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRolesType():
        return unicode

    def _initialize(self):
        super(TankmanPreviewModel, self)._initialize()
        self._addViewModelProperty('skills', CrewSkillListModel())
        self._addNumberProperty('slotIdx', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addArrayProperty('roles', Array())
