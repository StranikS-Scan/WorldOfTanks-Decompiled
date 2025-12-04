# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet_story_view_model.py
from frameworks.wulf import ViewModel

class PetStoryViewModel(ViewModel):
    __slots__ = ('onClose', 'onCardInteract')

    def __init__(self, properties=2, commands=2):
        super(PetStoryViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentStep(self):
        return self._getNumber(0)

    def setCurrentStep(self, value):
        self._setNumber(0, value)

    def getIsVideoCardClosed(self):
        return self._getBool(1)

    def setIsVideoCardClosed(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(PetStoryViewModel, self)._initialize()
        self._addNumberProperty('currentStep', 1)
        self._addBoolProperty('isVideoCardClosed', False)
        self.onClose = self._addCommand('onClose')
        self.onCardInteract = self._addCommand('onCardInteract')
