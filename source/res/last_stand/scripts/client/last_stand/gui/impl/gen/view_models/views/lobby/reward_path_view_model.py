# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/reward_path_view_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.reward_path_artefact_view_model import RewardPathArtefactViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.reward_path_difficulty_view_model import RewardPathDifficultyViewModel

class RewardPathViewModel(ViewModel):
    __slots__ = ('onClose', 'onViewLoaded', 'onAbout', 'onShowIntro', 'goToMission')

    def __init__(self, properties=5, commands=5):
        super(RewardPathViewModel, self).__init__(properties=properties, commands=commands)

    def getArtefacts(self):
        return self._getArray(0)

    def setArtefacts(self, value):
        self._setArray(0, value)

    @staticmethod
    def getArtefactsType():
        return RewardPathArtefactViewModel

    def getDifficulties(self):
        return self._getArray(1)

    def setDifficulties(self, value):
        self._setArray(1, value)

    @staticmethod
    def getDifficultiesType():
        return RewardPathDifficultyViewModel

    def getIsCompleted(self):
        return self._getBool(2)

    def setIsCompleted(self, value):
        self._setBool(2, value)

    def getProgress(self):
        return self._getNumber(3)

    def setProgress(self, value):
        self._setNumber(3, value)

    def getSelectedArtefactID(self):
        return self._getString(4)

    def setSelectedArtefactID(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(RewardPathViewModel, self)._initialize()
        self._addArrayProperty('artefacts', Array())
        self._addArrayProperty('difficulties', Array())
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('progress', 0)
        self._addStringProperty('selectedArtefactID', '')
        self.onClose = self._addCommand('onClose')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onAbout = self._addCommand('onAbout')
        self.onShowIntro = self._addCommand('onShowIntro')
        self.goToMission = self._addCommand('goToMission')
