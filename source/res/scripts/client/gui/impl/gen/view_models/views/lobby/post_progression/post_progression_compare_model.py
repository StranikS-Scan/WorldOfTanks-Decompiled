# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/post_progression_compare_model.py
from frameworks.wulf import ViewModel

class PostProgressionCompareModel(ViewModel):
    __slots__ = ('onApplyAction', 'onCancelAction', 'onResetAction')

    def __init__(self, properties=2, commands=3):
        super(PostProgressionCompareModel, self).__init__(properties=properties, commands=commands)

    def getHasChanges(self):
        return self._getBool(0)

    def setHasChanges(self, value):
        self._setBool(0, value)

    def getHasInitChanges(self):
        return self._getBool(1)

    def setHasInitChanges(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(PostProgressionCompareModel, self)._initialize()
        self._addBoolProperty('hasChanges', False)
        self._addBoolProperty('hasInitChanges', False)
        self.onApplyAction = self._addCommand('onApplyAction')
        self.onCancelAction = self._addCommand('onCancelAction')
        self.onResetAction = self._addCommand('onResetAction')
