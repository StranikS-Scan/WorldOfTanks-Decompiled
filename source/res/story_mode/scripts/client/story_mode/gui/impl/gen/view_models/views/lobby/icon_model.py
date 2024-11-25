# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/icon_model.py
from frameworks.wulf import ViewModel

class IconModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(IconModel, self).__init__(properties=properties, commands=commands)

    def getSmall(self):
        return self._getString(0)

    def setSmall(self, value):
        self._setString(0, value)

    def getBig(self):
        return self._getString(1)

    def setBig(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(IconModel, self)._initialize()
        self._addStringProperty('small', '')
        self._addStringProperty('big', '')
