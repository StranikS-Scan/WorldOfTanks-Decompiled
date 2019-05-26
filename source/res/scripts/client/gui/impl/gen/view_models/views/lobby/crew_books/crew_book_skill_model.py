# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew_books/crew_book_skill_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CrewBookSkillModel(ViewModel):
    __slots__ = ()

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getSkillName(self):
        return self._getString(2)

    def setSkillName(self, value):
        self._setString(2, value)

    def getTankmanInvId(self):
        return self._getNumber(3)

    def setTankmanInvId(self, value):
        self._setNumber(3, value)

    def getIsUnlearned(self):
        return self._getBool(4)

    def setIsUnlearned(self, value):
        self._setBool(4, value)

    def getIsCompact(self):
        return self._getBool(5)

    def setIsCompact(self, value):
        self._setBool(5, value)

    def getIsUndistributedExp(self):
        return self._getBool(6)

    def setIsUndistributedExp(self, value):
        self._setBool(6, value)

    def getIsTooltipEnable(self):
        return self._getBool(7)

    def setIsTooltipEnable(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(CrewBookSkillModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('description', '')
        self._addStringProperty('skillName', '')
        self._addNumberProperty('tankmanInvId', 0)
        self._addBoolProperty('isUnlearned', False)
        self._addBoolProperty('isCompact', False)
        self._addBoolProperty('isUndistributedExp', False)
        self._addBoolProperty('isTooltipEnable', True)
