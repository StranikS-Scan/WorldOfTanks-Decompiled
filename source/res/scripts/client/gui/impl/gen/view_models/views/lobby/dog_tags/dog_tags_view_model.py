# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/dog_tags_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.dog_tags.dt_dog_tag import DtDogTag
from gui.impl.gen.view_models.views.lobby.dog_tags.dt_grid_section import DtGridSection

class DogTagsViewModel(ViewModel):
    __slots__ = ('onExit', 'onEquip', 'onReset', 'onTabSelect', 'onInfoButtonClick', 'onPlayVideo', 'onOnboardingCloseClick', 'onNewComponentHover')

    def __init__(self, properties=11, commands=8):
        super(DogTagsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def equippedDogTag(self):
        return self._getViewModel(0)

    def getNewEngravingComponentCount(self):
        return self._getNumber(1)

    def setNewEngravingComponentCount(self, value):
        self._setNumber(1, value)

    def getNewBackgroundComponentCount(self):
        return self._getNumber(2)

    def setNewBackgroundComponentCount(self, value):
        self._setNumber(2, value)

    def getNewEngravingDedicationCount(self):
        return self._getNumber(3)

    def setNewEngravingDedicationCount(self, value):
        self._setNumber(3, value)

    def getNewEngravingTriumphCount(self):
        return self._getNumber(4)

    def setNewEngravingTriumphCount(self, value):
        self._setNumber(4, value)

    def getNewEngravingSkillCount(self):
        return self._getNumber(5)

    def setNewEngravingSkillCount(self, value):
        self._setNumber(5, value)

    def getTab(self):
        return self._getNumber(6)

    def setTab(self, value):
        self._setNumber(6, value)

    def getBackgroundGrid(self):
        return self._getArray(7)

    def setBackgroundGrid(self, value):
        self._setArray(7, value)

    def getEngravingGrid(self):
        return self._getArray(8)

    def setEngravingGrid(self, value):
        self._setArray(8, value)

    def getOnboardingEnabled(self):
        return self._getBool(9)

    def setOnboardingEnabled(self, value):
        self._setBool(9, value)

    def getIsTopView(self):
        return self._getBool(10)

    def setIsTopView(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(DogTagsViewModel, self)._initialize()
        self._addViewModelProperty('equippedDogTag', DtDogTag())
        self._addNumberProperty('newEngravingComponentCount', 0)
        self._addNumberProperty('newBackgroundComponentCount', 0)
        self._addNumberProperty('newEngravingDedicationCount', 0)
        self._addNumberProperty('newEngravingTriumphCount', 0)
        self._addNumberProperty('newEngravingSkillCount', 0)
        self._addNumberProperty('tab', 0)
        self._addArrayProperty('backgroundGrid', Array())
        self._addArrayProperty('engravingGrid', Array())
        self._addBoolProperty('onboardingEnabled', False)
        self._addBoolProperty('isTopView', False)
        self.onExit = self._addCommand('onExit')
        self.onEquip = self._addCommand('onEquip')
        self.onReset = self._addCommand('onReset')
        self.onTabSelect = self._addCommand('onTabSelect')
        self.onInfoButtonClick = self._addCommand('onInfoButtonClick')
        self.onPlayVideo = self._addCommand('onPlayVideo')
        self.onOnboardingCloseClick = self._addCommand('onOnboardingCloseClick')
        self.onNewComponentHover = self._addCommand('onNewComponentHover')
