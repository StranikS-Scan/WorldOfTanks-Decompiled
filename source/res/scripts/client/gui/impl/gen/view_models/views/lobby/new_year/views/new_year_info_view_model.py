# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_info_view_model.py
from frameworks.wulf import ViewModel

class NewYearInfoViewModel(ViewModel):
    __slots__ = ('onVideoClicked', 'onButtonClick')
    LEVELS = 'levels'
    STYLES = 'styles'
    SMALLBOXES = 'smallBoxes'
    CELEBRITY = 'celebrity'
    BIGBOXES = 'bigBoxes'
    GUARANTEED_REWARDS = 'guaranteedRewards'
    STREAM_BOX = 'streamBox'

    def __init__(self, properties=11, commands=2):
        super(NewYearInfoViewModel, self).__init__(properties=properties, commands=commands)

    def getRealm(self):
        return self._getString(0)

    def setRealm(self, value):
        self._setString(0, value)

    def getLanguage(self):
        return self._getString(1)

    def setLanguage(self, value):
        self._setString(1, value)

    def getMaxBonus(self):
        return self._getReal(2)

    def setMaxBonus(self, value):
        self._setReal(2, value)

    def getUsualMaxBonus(self):
        return self._getReal(3)

    def setUsualMaxBonus(self, value):
        self._setReal(3, value)

    def getSingleMegaBonus(self):
        return self._getReal(4)

    def setSingleMegaBonus(self, value):
        self._setReal(4, value)

    def getMaxMegaBonus(self):
        return self._getReal(5)

    def setMaxMegaBonus(self, value):
        self._setReal(5, value)

    def getRegularSlotCooldownValue(self):
        return self._getNumber(6)

    def setRegularSlotCooldownValue(self, value):
        self._setNumber(6, value)

    def getExtraSlotCooldownValue(self):
        return self._getNumber(7)

    def setExtraSlotCooldownValue(self, value):
        self._setNumber(7, value)

    def getQuestsToGetExtraSlot(self):
        return self._getNumber(8)

    def setQuestsToGetExtraSlot(self, value):
        self._setNumber(8, value)

    def getIsExternalBuyBox(self):
        return self._getBool(9)

    def setIsExternalBuyBox(self, value):
        self._setBool(9, value)

    def getIsLootBoxEnabled(self):
        return self._getBool(10)

    def setIsLootBoxEnabled(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(NewYearInfoViewModel, self)._initialize()
        self._addStringProperty('realm', '')
        self._addStringProperty('language', '')
        self._addRealProperty('maxBonus', 0.0)
        self._addRealProperty('usualMaxBonus', 0.0)
        self._addRealProperty('singleMegaBonus', 0.0)
        self._addRealProperty('maxMegaBonus', 0.0)
        self._addNumberProperty('regularSlotCooldownValue', 0)
        self._addNumberProperty('extraSlotCooldownValue', 0)
        self._addNumberProperty('questsToGetExtraSlot', 0)
        self._addBoolProperty('isExternalBuyBox', False)
        self._addBoolProperty('isLootBoxEnabled', False)
        self.onVideoClicked = self._addCommand('onVideoClicked')
        self.onButtonClick = self._addCommand('onButtonClick')
