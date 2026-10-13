# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_progression_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from portal.gui.impl.gen.view_models.views.lobby.portal_medal_model import PortalMedalModel
from portal.gui.impl.gen.view_models.views.lobby.portal_progression_level_model import PortalProgressionLevelModel

class PortalProgressionModel(ViewModel):
    __slots__ = ('onIntroVideoClick', 'onOutroVideoClick', 'onClose')

    def __init__(self, properties=5, commands=3):
        super(PortalProgressionModel, self).__init__(properties=properties, commands=commands)

    def getPointsCurrent(self):
        return self._getNumber(0)

    def setPointsCurrent(self, value):
        self._setNumber(0, value)

    def getCurrentStage(self):
        return self._getNumber(1)

    def setCurrentStage(self, value):
        self._setNumber(1, value)

    def getIsOutroLocked(self):
        return self._getBool(2)

    def setIsOutroLocked(self, value):
        self._setBool(2, value)

    def getStages(self):
        return self._getArray(3)

    def setStages(self, value):
        self._setArray(3, value)

    @staticmethod
    def getStagesType():
        return PortalProgressionLevelModel

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
        self._addBoolProperty('isOutroLocked', False)
        self._addArrayProperty('stages', Array())
        self._addArrayProperty('medals', Array())
        self.onIntroVideoClick = self._addCommand('onIntroVideoClick')
        self.onOutroVideoClick = self._addCommand('onOutroVideoClick')
        self.onClose = self._addCommand('onClose')
