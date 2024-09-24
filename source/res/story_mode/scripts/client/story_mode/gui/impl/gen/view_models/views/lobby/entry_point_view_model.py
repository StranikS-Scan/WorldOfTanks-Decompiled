# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/impl/gen/view_models/views/lobby/entry_point_view_model.py
from frameworks.wulf import ViewModel

class EntryPointViewModel(ViewModel):
    __slots__ = ('onClick', 'onHoverForSetTime', 'onLeaveAfterSetTime')

    def __init__(self, properties=4, commands=3):
        super(EntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getIsNew(self):
        return self._getBool(0)

    def setIsNew(self, value):
        self._setBool(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getSubtitle(self):
        return self._getString(2)

    def setSubtitle(self, value):
        self._setString(2, value)

    def getBgFolderName(self):
        return self._getString(3)

    def setBgFolderName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(EntryPointViewModel, self)._initialize()
        self._addBoolProperty('isNew', False)
        self._addStringProperty('title', '')
        self._addStringProperty('subtitle', '')
        self._addStringProperty('bgFolderName', '')
        self.onClick = self._addCommand('onClick')
        self.onHoverForSetTime = self._addCommand('onHoverForSetTime')
        self.onLeaveAfterSetTime = self._addCommand('onLeaveAfterSetTime')
