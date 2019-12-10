# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_info_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel

class NewYearInfoViewModel(ViewModel):
    __slots__ = ('onVideoClicked', 'onButtonClick')
    LEVELS = 'levels'
    STYLES = 'styles'
    BIGBOXES = 'bigBoxes'
    SMALLBOXES = 'smallBoxes'

    def __init__(self, properties=8, commands=2):
        super(NewYearInfoViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def giftList(self):
        return self._getViewModel(0)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getCreditsBonus(self):
        return self._getReal(2)

    def setCreditsBonus(self, value):
        self._setReal(2, value)

    def getMaxBonus(self):
        return self._getReal(3)

    def setMaxBonus(self, value):
        self._setReal(3, value)

    def getUsualMaxBonus(self):
        return self._getReal(4)

    def setUsualMaxBonus(self, value):
        self._setReal(4, value)

    def getSingleMegaBonus(self):
        return self._getReal(5)

    def setSingleMegaBonus(self, value):
        self._setReal(5, value)

    def getMaxMegaBonus(self):
        return self._getReal(6)

    def setMaxMegaBonus(self, value):
        self._setReal(6, value)

    def getCooldownValue(self):
        return self._getNumber(7)

    def setCooldownValue(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(NewYearInfoViewModel, self)._initialize()
        self._addViewModelProperty('giftList', UserListModel())
        self._addStringProperty('title', '')
        self._addRealProperty('creditsBonus', 0.0)
        self._addRealProperty('maxBonus', 0.0)
        self._addRealProperty('usualMaxBonus', 0.0)
        self._addRealProperty('singleMegaBonus', 0.0)
        self._addRealProperty('maxMegaBonus', 0.0)
        self._addNumberProperty('cooldownValue', 0)
        self.onVideoClicked = self._addCommand('onVideoClicked')
        self.onButtonClick = self._addCommand('onButtonClick')
