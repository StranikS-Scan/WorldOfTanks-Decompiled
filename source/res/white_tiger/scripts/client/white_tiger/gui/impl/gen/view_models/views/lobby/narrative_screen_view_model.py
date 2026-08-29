# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/narrative_screen_view_model.py
from frameworks.wulf import ViewModel

class NarrativeScreenViewModel(ViewModel):
    __slots__ = ('onClose', 'onVoiceoverToggle')

    def __init__(self, properties=1, commands=2):
        super(NarrativeScreenViewModel, self).__init__(properties=properties, commands=commands)

    def getIsVoiceoverActive(self):
        return self._getBool(0)

    def setIsVoiceoverActive(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(NarrativeScreenViewModel, self)._initialize()
        self._addBoolProperty('isVoiceoverActive', False)
        self.onClose = self._addCommand('onClose')
        self.onVoiceoverToggle = self._addCommand('onVoiceoverToggle')
