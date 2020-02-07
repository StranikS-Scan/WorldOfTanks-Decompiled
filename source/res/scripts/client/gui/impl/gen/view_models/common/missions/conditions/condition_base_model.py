# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/conditions/condition_base_model.py
from frameworks.wulf import ViewModel

class ConditionBaseModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ConditionBaseModel, self).__init__(properties=properties, commands=commands)

    def getConditionType(self):
        return self._getString(0)

    def setConditionType(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(ConditionBaseModel, self)._initialize()
        self._addStringProperty('conditionType', '')
