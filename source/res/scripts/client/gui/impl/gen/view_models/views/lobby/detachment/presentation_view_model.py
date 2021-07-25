# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/presentation_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.detachment.common.instructors_category_model import InstructorsCategoryModel
from gui.impl.gen.view_models.views.lobby.detachment.presentation_bonus_model import PresentationBonusModel

class PresentationViewModel(ViewModel):
    __slots__ = ('onBack', 'onNext', 'onDone', 'onClose', 'onVoiceListenClick')
    SCREEN_BOOKS = 'books'
    SCREEN_BUNKS = 'bunks'
    SCREEN_SHEETS = 'sheets'
    SCREEN_BOOSTERS = 'boosters'
    SCREEN_INSTRUCTORS = 'instructors'
    CREW_BOOKS_NATIONAL = 'nationalCrewBooks'
    CREW_BOOKS_UNIVERSAL = 'universalCrewBooks'
    CREW_BOOKS_MIXED = 'mixedCrewBooks'
    TOOLTIP_SUB_HEADER = 'tooltipSubHeader'
    TOOLTIP_ITEM = 'tooltipItem'
    TOOLTIP_ADDITIONAL_REWARDS = 'tooltipAdditionalRewards'

    def __init__(self, properties=7, commands=5):
        super(PresentationViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentScreenIndex(self):
        return self._getNumber(0)

    def setCurrentScreenIndex(self, value):
        self._setNumber(0, value)

    def getAmountOfScreens(self):
        return self._getNumber(1)

    def setAmountOfScreens(self, value):
        self._setNumber(1, value)

    def getScreenKey(self):
        return self._getString(2)

    def setScreenKey(self, value):
        self._setString(2, value)

    def getMoreItemsCount(self):
        return self._getNumber(3)

    def setMoreItemsCount(self, value):
        self._setNumber(3, value)

    def getCrewBooksType(self):
        return self._getString(4)

    def setCrewBooksType(self, value):
        self._setString(4, value)

    def getBonusesList(self):
        return self._getArray(5)

    def setBonusesList(self, value):
        self._setArray(5, value)

    def getInstructorsCategories(self):
        return self._getArray(6)

    def setInstructorsCategories(self, value):
        self._setArray(6, value)

    def _initialize(self):
        super(PresentationViewModel, self)._initialize()
        self._addNumberProperty('currentScreenIndex', 0)
        self._addNumberProperty('amountOfScreens', 0)
        self._addStringProperty('screenKey', '')
        self._addNumberProperty('moreItemsCount', -1)
        self._addStringProperty('crewBooksType', '')
        self._addArrayProperty('bonusesList', Array())
        self._addArrayProperty('instructorsCategories', Array())
        self.onBack = self._addCommand('onBack')
        self.onNext = self._addCommand('onNext')
        self.onDone = self._addCommand('onDone')
        self.onClose = self._addCommand('onClose')
        self.onVoiceListenClick = self._addCommand('onVoiceListenClick')
