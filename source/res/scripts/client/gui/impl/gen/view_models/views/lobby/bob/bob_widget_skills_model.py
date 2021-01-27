# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bob/bob_widget_skills_model.py
from frameworks.wulf import ViewModel

class BobWidgetSkillsModel(ViewModel):
    __slots__ = ()
    STATE_ACTIVE = 'active'
    STATE_INACTIVE = 'inactive'

    def __init__(self, properties=4, commands=0):
        super(BobWidgetSkillsModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getSkill(self):
        return self._getString(1)

    def setSkill(self, value):
        self._setString(1, value)

    def getTimeLeft(self):
        return self._getString(2)

    def setTimeLeft(self, value):
        self._setString(2, value)

    def getCount(self):
        return self._getNumber(3)

    def setCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(BobWidgetSkillsModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addStringProperty('skill', '')
        self._addStringProperty('timeLeft', '')
        self._addNumberProperty('count', 0)
