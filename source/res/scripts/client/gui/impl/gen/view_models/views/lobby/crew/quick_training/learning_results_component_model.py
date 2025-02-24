# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/quick_training/learning_results_component_model.py
from gui.impl.gen.view_models.views.lobby.crew.components.component_base_model import ComponentBaseModel

class LearningResultsComponentModel(ComponentBaseModel):
    __slots__ = ('learn', 'cancel')

    def __init__(self, properties=3, commands=2):
        super(LearningResultsComponentModel, self).__init__(properties=properties, commands=commands)

    def getCrewXpAmount(self):
        return self._getNumber(1)

    def setCrewXpAmount(self, value):
        self._setNumber(1, value)

    def getPersonalXpAmount(self):
        return self._getNumber(2)

    def setPersonalXpAmount(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(LearningResultsComponentModel, self)._initialize()
        self._addNumberProperty('crewXpAmount', 0)
        self._addNumberProperty('personalXpAmount', 0)
        self.learn = self._addCommand('learn')
        self.cancel = self._addCommand('cancel')
