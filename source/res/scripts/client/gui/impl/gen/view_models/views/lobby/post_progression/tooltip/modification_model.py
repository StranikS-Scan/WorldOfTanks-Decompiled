# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/tooltip/modification_model.py
from frameworks.wulf import ViewModel

class ModificationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ModificationModel, self).__init__(properties=properties, commands=commands)

    def getIconResName(self):
        return self._getString(0)

    def setIconResName(self, value):
        self._setString(0, value)

    def getIsInstalled(self):
        return self._getBool(1)

    def setIsInstalled(self, value):
        self._setBool(1, value)

    def getIsCurrent(self):
        return self._getBool(2)

    def setIsCurrent(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ModificationModel, self)._initialize()
        self._addStringProperty('iconResName', '')
        self._addBoolProperty('isInstalled', False)
        self._addBoolProperty('isCurrent', False)
