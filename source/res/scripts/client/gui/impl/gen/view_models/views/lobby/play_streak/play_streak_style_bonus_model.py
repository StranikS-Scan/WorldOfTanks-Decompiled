# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/play_streak/play_streak_style_bonus_model.py
from gui.impl.gen.view_models.views.lobby.play_streak.play_streak_icon_bonus_model import PlayStreakIconBonusModel

class PlayStreakStyleBonusModel(PlayStreakIconBonusModel):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(PlayStreakStyleBonusModel, self).__init__(properties=properties, commands=commands)

    def getStyleID(self):
        return self._getNumber(11)

    def setStyleID(self, value):
        self._setNumber(11, value)

    def getBranchID(self):
        return self._getNumber(12)

    def setBranchID(self, value):
        self._setNumber(12, value)

    def getProgressLevel(self):
        return self._getNumber(13)

    def setProgressLevel(self, value):
        self._setNumber(13, value)

    def getLabel(self):
        return self._getString(14)

    def setLabel(self, value):
        self._setString(14, value)

    def getStyleCD(self):
        return self._getNumber(15)

    def setStyleCD(self, value):
        self._setNumber(15, value)

    def getIcon(self):
        return self._getString(16)

    def setIcon(self, value):
        self._setString(16, value)

    def _initialize(self):
        super(PlayStreakStyleBonusModel, self)._initialize()
        self._addNumberProperty('styleID', 0)
        self._addNumberProperty('branchID', 0)
        self._addNumberProperty('progressLevel', 0)
        self._addStringProperty('label', '')
        self._addNumberProperty('styleCD', 0)
        self._addStringProperty('icon', '')
