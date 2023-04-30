# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/missions_completed_visited_model.py
from frameworks.wulf import ViewModel

class MissionsCompletedVisitedModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MissionsCompletedVisitedModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getValue(self):
        return self._getBool(1)

    def setValue(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(MissionsCompletedVisitedModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addBoolProperty('value', False)
