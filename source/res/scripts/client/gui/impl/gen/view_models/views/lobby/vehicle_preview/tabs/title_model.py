# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_preview/tabs/title_model.py
from frameworks.wulf import ViewModel

class TitleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(TitleModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getSkillName(self):
        return self._getString(1)

    def setSkillName(self, value):
        self._setString(1, value)

    def getRoleName(self):
        return self._getString(2)

    def setRoleName(self, value):
        self._setString(2, value)

    def getSkillCustomName(self):
        return self._getString(3)

    def setSkillCustomName(self, value):
        self._setString(3, value)

    def getIconName(self):
        return self._getString(4)

    def setIconName(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(TitleModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('skillName', '')
        self._addStringProperty('roleName', '')
        self._addStringProperty('skillCustomName', '')
        self._addStringProperty('iconName', '')
