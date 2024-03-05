# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/character_widget_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class CharacterWidgetViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CharacterWidgetViewModel, self).__init__(properties=properties, commands=commands)

    def getTankman(self):
        return self._getString(0)

    def setTankman(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getSkills(self):
        return self._getArray(2)

    def setSkills(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSkillsType():
        return unicode

    def getTooltipId(self):
        return self._getString(3)

    def setTooltipId(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(CharacterWidgetViewModel, self)._initialize()
        self._addStringProperty('tankman', '')
        self._addStringProperty('icon', '')
        self._addArrayProperty('skills', Array())
        self._addStringProperty('tooltipId', '')
