# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_progression_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.portal_medal_model import PortalMedalModel
from portal.gui.impl.gen.view_models.views.lobby.portal_progression_level_model import PortalProgressionLevelModel

class PortalProgressionModel(ViewModel):
    __slots__ = ('onClose', 'onAboutEventClick')

    def __init__(self, properties=5, commands=2):
        super(PortalProgressionModel, self).__init__(properties=properties, commands=commands)

    def getPointsCurrent(self):
        return self._getNumber(0)

    def setPointsCurrent(self, value):
        self._setNumber(0, value)

    def getCurrentStage(self):
        return self._getNumber(1)

    def setCurrentStage(self, value):
        self._setNumber(1, value)

    def getStages(self):
        return self._getArray(2)

    def setStages(self, value):
        self._setArray(2, value)

    @staticmethod
    def getStagesType():
        return PortalProgressionLevelModel

    def getStampsNeededPerStage(self):
        return self._getNumber(3)

    def setStampsNeededPerStage(self, value):
        self._setNumber(3, value)

    def getMedals(self):
        return self._getArray(4)

    def setMedals(self, value):
        self._setArray(4, value)

    @staticmethod
    def getMedalsType():
        return PortalMedalModel

    def _initialize(self):
        super(PortalProgressionModel, self)._initialize()
        self._addNumberProperty('pointsCurrent', 0)
        self._addNumberProperty('currentStage', 0)
        self._addArrayProperty('stages', Array())
        self._addNumberProperty('stampsNeededPerStage', 0)
        self._addArrayProperty('medals', Array())
        self.onClose = self._addCommand('onClose')
        self.onAboutEventClick = self._addCommand('onAboutEventClick')
