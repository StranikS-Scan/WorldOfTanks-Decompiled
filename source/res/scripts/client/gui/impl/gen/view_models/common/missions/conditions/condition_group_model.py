# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/missions/conditions/condition_group_model.py
from gui.impl.gen.view_models.common.missions.conditions.condition_base_model import ConditionBaseModel

class ConditionGroupModel(ConditionBaseModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ConditionGroupModel, self).__init__(properties=properties, commands=commands)

    def getItems(self):
        return self._getArray(1)

    def setItems(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(ConditionGroupModel, self)._initialize()
        self._addArrayProperty('items')
