# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_challenge_action_model.py
from frameworks.wulf import ViewModel

class NewYearChallengeActionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NewYearChallengeActionModel, self).__init__(properties=properties, commands=commands)

    def getIsSeparator(self):
        return self._getBool(0)

    def setIsSeparator(self, value):
        self._setBool(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(NewYearChallengeActionModel, self)._initialize()
        self._addBoolProperty('isSeparator', False)
        self._addStringProperty('type', 'action_empty')
