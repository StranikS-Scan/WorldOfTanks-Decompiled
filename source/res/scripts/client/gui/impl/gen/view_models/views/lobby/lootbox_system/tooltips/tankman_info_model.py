# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/tooltips/tankman_info_model.py
from frameworks.wulf import Array, ViewModel

class TankmanInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(TankmanInfoModel, self).__init__(properties=properties, commands=commands)

    def getSkills(self):
        return self._getArray(0)

    def setSkills(self, value):
        self._setArray(0, value)

    @staticmethod
    def getSkillsType():
        return unicode

    def _initialize(self):
        super(TankmanInfoModel, self)._initialize()
        self._addArrayProperty('skills', Array())
