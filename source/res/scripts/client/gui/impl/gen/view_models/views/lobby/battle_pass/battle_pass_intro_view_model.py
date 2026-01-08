# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_intro_view_model.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.base_intro_view_model import BaseIntroViewModel

class BattlePassIntroViewModel(BaseIntroViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=3):
        super(BattlePassIntroViewModel, self).__init__(properties=properties, commands=commands)

    def getBackground(self):
        return self._getResource(5)

    def setBackground(self, value):
        self._setResource(5, value)

    def getSubTitle(self):
        return self._getResource(6)

    def setSubTitle(self, value):
        self._setResource(6, value)

    def getHasMarathon(self):
        return self._getBool(7)

    def setHasMarathon(self, value):
        self._setBool(7, value)

    def getMarathonChapterStartDate(self):
        return self._getNumber(8)

    def setMarathonChapterStartDate(self, value):
        self._setNumber(8, value)

    def getMarathonChapterEndDate(self):
        return self._getNumber(9)

    def setMarathonChapterEndDate(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(BattlePassIntroViewModel, self)._initialize()
        self._addResourceProperty('background', R.invalid())
        self._addResourceProperty('subTitle', R.invalid())
        self._addBoolProperty('hasMarathon', False)
        self._addNumberProperty('marathonChapterStartDate', 0)
        self._addNumberProperty('marathonChapterEndDate', 0)
