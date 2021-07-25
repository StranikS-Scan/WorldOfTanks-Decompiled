# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/common/commander_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.commander_icon_model import CommanderIconModel

class CommanderModel(CommanderIconModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(CommanderModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(3)

    def setName(self, value):
        self._setString(3, value)

    def getIcon(self):
        return self._getResource(4)

    def setIcon(self, value):
        self._setResource(4, value)

    def getNation(self):
        return self._getString(5)

    def setNation(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(CommanderModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('nation', '')
