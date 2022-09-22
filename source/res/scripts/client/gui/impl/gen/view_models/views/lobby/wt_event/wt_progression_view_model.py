# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_progression_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_progression_level_model import WtProgressionLevelModel

class WtProgressionViewModel(ViewModel):
    __slots__ = ('onAboutClick', 'onFinishedAnimation', 'onLevelsAnimationFinished')

    def __init__(self, properties=9, commands=3):
        super(WtProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def progression(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressionType():
        return WtProgressionLevelModel

    def getPreviousLevel(self):
        return self._getNumber(1)

    def setPreviousLevel(self, value):
        self._setNumber(1, value)

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getTotalLevel(self):
        return self._getNumber(3)

    def setTotalLevel(self, value):
        self._setNumber(3, value)

    def getTotalPoints(self):
        return self._getNumber(4)

    def setTotalPoints(self, value):
        self._setNumber(4, value)

    def getPreviousAllPoints(self):
        return self._getNumber(5)

    def setPreviousAllPoints(self, value):
        self._setNumber(5, value)

    def getCurrentAllPoints(self):
        return self._getNumber(6)

    def setCurrentAllPoints(self, value):
        self._setNumber(6, value)

    def getShowLevelsAnimations(self):
        return self._getBool(7)

    def setShowLevelsAnimations(self, value):
        self._setBool(7, value)

    def getIsCompleted(self):
        return self._getBool(8)

    def setIsCompleted(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(WtProgressionViewModel, self)._initialize()
        self._addViewModelProperty('progression', UserListModel())
        self._addNumberProperty('previousLevel', 0)
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('totalLevel', 0)
        self._addNumberProperty('totalPoints', 0)
        self._addNumberProperty('previousAllPoints', 0)
        self._addNumberProperty('currentAllPoints', 0)
        self._addBoolProperty('showLevelsAnimations', False)
        self._addBoolProperty('isCompleted', False)
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onFinishedAnimation = self._addCommand('onFinishedAnimation')
        self.onLevelsAnimationFinished = self._addCommand('onLevelsAnimationFinished')
