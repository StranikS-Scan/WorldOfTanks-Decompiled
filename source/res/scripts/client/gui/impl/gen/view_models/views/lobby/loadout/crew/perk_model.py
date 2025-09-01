# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/crew/perk_model.py
from frameworks.wulf import ViewModel

class PerkModel(ViewModel):
    __slots__ = ()
    NEW_STATE = 'new'
    FREE_STATE = 'free'
    LEARNING_STATE = 'learning'
    LEARNED_STATE = 'learned'
    IRRELEVANT_STATE = 'irrelevant'

    def __init__(self, properties=2, commands=0):
        super(PerkModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getState(self):
        return self._getString(1)

    def setState(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(PerkModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('state', '')
