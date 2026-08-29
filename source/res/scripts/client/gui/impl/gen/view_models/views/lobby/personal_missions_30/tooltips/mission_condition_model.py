# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/tooltips/mission_condition_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen import R

class MissionConditionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MissionConditionModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getText(self):
        return self._getString(1)

    def setText(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(MissionConditionModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('text', '')
