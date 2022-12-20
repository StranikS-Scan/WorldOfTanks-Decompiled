# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/skill_model.py
from frameworks.wulf import Array
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_base_model import SkillBaseModel
from frontline.gui.impl.gen.view_models.views.lobby.views.skill_level_model import SkillLevelModel

class SkillModel(SkillBaseModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(SkillModel, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getNumber(3)

    def setPrice(self, value):
        self._setNumber(3, value)

    def getShortDescription(self):
        return self._getString(4)

    def setShortDescription(self, value):
        self._setString(4, value)

    def getLongDescription(self):
        return self._getString(5)

    def setLongDescription(self, value):
        self._setString(5, value)

    def getIsActivated(self):
        return self._getBool(6)

    def setIsActivated(self, value):
        self._setBool(6, value)

    def getIsDisabled(self):
        return self._getBool(7)

    def setIsDisabled(self, value):
        self._setBool(7, value)

    def getLevels(self):
        return self._getArray(8)

    def setLevels(self, value):
        self._setArray(8, value)

    @staticmethod
    def getLevelsType():
        return SkillLevelModel

    def _initialize(self):
        super(SkillModel, self)._initialize()
        self._addNumberProperty('price', 0)
        self._addStringProperty('shortDescription', '')
        self._addStringProperty('longDescription', '')
        self._addBoolProperty('isActivated', False)
        self._addBoolProperty('isDisabled', False)
        self._addArrayProperty('levels', Array())
