# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/instructor_page/instructor_page_info_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.perk_short_model import PerkShortModel

class InstructorPageInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(InstructorPageInfoModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def getNation(self):
        return self._getString(2)

    def setNation(self, value):
        self._setString(2, value)

    def getBonusExperience(self):
        return self._getNumber(3)

    def setBonusExperience(self, value):
        self._setNumber(3, value)

    def getPerks(self):
        return self._getArray(4)

    def setPerks(self, value):
        self._setArray(4, value)

    def getIsVoiced(self):
        return self._getBool(5)

    def setIsVoiced(self, value):
        self._setBool(5, value)

    def getIsVoiceActivated(self):
        return self._getBool(6)

    def setIsVoiceActivated(self, value):
        self._setBool(6, value)

    def getRequiredSlots(self):
        return self._getNumber(7)

    def setRequiredSlots(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(InstructorPageInfoModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addResourceProperty('description', R.invalid())
        self._addStringProperty('nation', '')
        self._addNumberProperty('bonusExperience', 0)
        self._addArrayProperty('perks', Array())
        self._addBoolProperty('isVoiced', False)
        self._addBoolProperty('isVoiceActivated', False)
        self._addNumberProperty('requiredSlots', 0)
