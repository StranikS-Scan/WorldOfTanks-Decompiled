# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_preview/tabs/title_model.py
from frameworks.wulf import ViewModel

class TitleModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TitleModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getSkillName(self):
        return self._getString(1)

    def setSkillName(self, value):
        self._setString(1, value)

    def getSkillCustomName(self):
        return self._getString(2)

    def setSkillCustomName(self, value):
        self._setString(2, value)

    def getIconName(self):
        return self._getString(3)

    def setIconName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(TitleModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('skillName', '')
        self._addStringProperty('skillCustomName', '')
        self._addStringProperty('iconName', '')
