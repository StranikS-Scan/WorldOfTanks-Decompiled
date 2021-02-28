# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass3d_style_choice_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tank_style_model import TankStyleModel

class BattlePass3DStyleChoiceViewModel(ViewModel):
    __slots__ = ('onPreviewClick', 'onSelectLevel', 'onConfirmStyle', 'onCloseOverlay')

    def __init__(self, properties=6, commands=4):
        super(BattlePass3DStyleChoiceViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def tankStylesList(self):
        return self._getViewModel(0)

    def getChapterNumber(self):
        return self._getNumber(1)

    def setChapterNumber(self, value):
        self._setNumber(1, value)

    def getCurrentLevel(self):
        return self._getNumber(2)

    def setCurrentLevel(self, value):
        self._setNumber(2, value)

    def getSelectedLevel(self):
        return self._getNumber(3)

    def setSelectedLevel(self, value):
        self._setNumber(3, value)

    def getIsNeedToCloseOverlay(self):
        return self._getBool(4)

    def setIsNeedToCloseOverlay(self, value):
        self._setBool(4, value)

    def getIsChoiceEnabled(self):
        return self._getBool(5)

    def setIsChoiceEnabled(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(BattlePass3DStyleChoiceViewModel, self)._initialize()
        self._addViewModelProperty('tankStylesList', UserListModel())
        self._addNumberProperty('chapterNumber', 0)
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('selectedLevel', 0)
        self._addBoolProperty('isNeedToCloseOverlay', False)
        self._addBoolProperty('isChoiceEnabled', False)
        self.onPreviewClick = self._addCommand('onPreviewClick')
        self.onSelectLevel = self._addCommand('onSelectLevel')
        self.onConfirmStyle = self._addCommand('onConfirmStyle')
        self.onCloseOverlay = self._addCommand('onCloseOverlay')
