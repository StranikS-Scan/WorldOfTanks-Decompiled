# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/reward_path_view_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.reward_path_artefact_view_model import RewardPathArtefactViewModel

class RewardPathViewModel(ViewModel):
    __slots__ = ('onClose', 'onViewLoaded', 'onAbout', 'onShowIntro', 'goToMission')

    def __init__(self, properties=3, commands=5):
        super(RewardPathViewModel, self).__init__(properties=properties, commands=commands)

    def getArtefacts(self):
        return self._getArray(0)

    def setArtefacts(self, value):
        self._setArray(0, value)

    @staticmethod
    def getArtefactsType():
        return RewardPathArtefactViewModel

    def getPoints(self):
        return self._getNumber(1)

    def setPoints(self, value):
        self._setNumber(1, value)

    def getCurrentArtefactID(self):
        return self._getString(2)

    def setCurrentArtefactID(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(RewardPathViewModel, self)._initialize()
        self._addArrayProperty('artefacts', Array())
        self._addNumberProperty('points', 0)
        self._addStringProperty('currentArtefactID', '')
        self.onClose = self._addCommand('onClose')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onAbout = self._addCommand('onAbout')
        self.onShowIntro = self._addCommand('onShowIntro')
        self.goToMission = self._addCommand('goToMission')
