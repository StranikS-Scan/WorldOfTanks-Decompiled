# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/progression_qualification_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.qualification_battle import QualificationBattle
from gui.impl.gen.view_models.views.lobby.comp7.qualification_model import QualificationModel

class ProgressionQualificationModel(QualificationModel):
    __slots__ = ('onRankRewardsPageOpen',)

    def __init__(self, properties=5, commands=1):
        super(ProgressionQualificationModel, self).__init__(properties=properties, commands=commands)

    def getBattles(self):
        return self._getArray(4)

    def setBattles(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBattlesType():
        return QualificationBattle

    def _initialize(self):
        super(ProgressionQualificationModel, self)._initialize()
        self._addArrayProperty('battles', Array())
        self.onRankRewardsPageOpen = self._addCommand('onRankRewardsPageOpen')
