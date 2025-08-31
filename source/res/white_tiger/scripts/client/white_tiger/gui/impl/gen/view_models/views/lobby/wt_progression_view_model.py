# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_progression_view_model.py
from frameworks.wulf import ViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_progression_model import WtProgressionModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_quests_model import WtQuestsModel

class WtProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutClicked', 'onIntroVideoClicked', 'onOutroVideoClicked')

    def __init__(self, properties=3, commands=4):
        super(WtProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def dailyQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getDailyQuestsType():
        return WtQuestsModel

    @property
    def progression(self):
        return self._getViewModel(1)

    @staticmethod
    def getProgressionType():
        return WtProgressionModel

    def getIsOutroVideoAvailable(self):
        return self._getBool(2)

    def setIsOutroVideoAvailable(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(WtProgressionViewModel, self)._initialize()
        self._addViewModelProperty('dailyQuests', WtQuestsModel())
        self._addViewModelProperty('progression', WtProgressionModel())
        self._addBoolProperty('isOutroVideoAvailable', False)
        self.onClose = self._addCommand('onClose')
        self.onAboutClicked = self._addCommand('onAboutClicked')
        self.onIntroVideoClicked = self._addCommand('onIntroVideoClicked')
        self.onOutroVideoClicked = self._addCommand('onOutroVideoClicked')
