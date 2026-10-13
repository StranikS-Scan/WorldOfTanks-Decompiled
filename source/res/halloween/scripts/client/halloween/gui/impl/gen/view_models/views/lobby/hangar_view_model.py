# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/hangar_view_model.py
from halloween.gui.impl.gen.view_models.views.lobby.bestiary_model import BestiaryModel
from halloween.gui.impl.gen.view_models.views.lobby.vehicle_title_view_model import VehicleTitleViewModel
from gui.impl.gen.view_models.views.lobby.common.router_model import RouterModel

class HangarViewModel(RouterModel):
    __slots__ = ('onAboutClick', 'onSlide', 'onPreview', 'onWidgetsUpdate', 'onTasksClick', 'onPacksClick', 'onComparisonClick', 'onAnomaliesClick', 'onViewLoaded', 'onEnemyClick', 'onBestiaryClick')

    def __init__(self, properties=15, commands=13):
        super(HangarViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainGiftVehicle(self):
        return self._getViewModel(2)

    @staticmethod
    def getMainGiftVehicleType():
        return VehicleTitleViewModel

    @property
    def bestiaryInfo(self):
        return self._getViewModel(3)

    @staticmethod
    def getBestiaryInfoType():
        return BestiaryModel

    def getSelectedSlide(self):
        return self._getNumber(4)

    def setSelectedSlide(self, value):
        self._setNumber(4, value)

    def getScrollToSlide(self):
        return self._getNumber(5)

    def setScrollToSlide(self, value):
        self._setNumber(5, value)

    def getSlidesCount(self):
        return self._getNumber(6)

    def setSlidesCount(self, value):
        self._setNumber(6, value)

    def getIsVehicleLocked(self):
        return self._getBool(7)

    def setIsVehicleLocked(self, value):
        self._setBool(7, value)

    def getLockedMissionIndex(self):
        return self._getNumber(8)

    def setLockedMissionIndex(self, value):
        self._setNumber(8, value)

    def getIsVehicleInBattle(self):
        return self._getBool(9)

    def setIsVehicleInBattle(self, value):
        self._setBool(9, value)

    def getIsCompleted(self):
        return self._getBool(10)

    def setIsCompleted(self, value):
        self._setBool(10, value)

    def getIsOpened(self):
        return self._getBool(11)

    def setIsOpened(self, value):
        self._setBool(11, value)

    def getIsInfoPageEnabled(self):
        return self._getBool(12)

    def setIsInfoPageEnabled(self, value):
        self._setBool(12, value)

    def getAreAnomaliesUnlocked(self):
        return self._getBool(13)

    def setAreAnomaliesUnlocked(self, value):
        self._setBool(13, value)

    def getHasNewAnomaly(self):
        return self._getBool(14)

    def setHasNewAnomaly(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(HangarViewModel, self)._initialize()
        self._addViewModelProperty('mainGiftVehicle', VehicleTitleViewModel())
        self._addViewModelProperty('bestiaryInfo', BestiaryModel())
        self._addNumberProperty('selectedSlide', 0)
        self._addNumberProperty('scrollToSlide', 0)
        self._addNumberProperty('slidesCount', 0)
        self._addBoolProperty('isVehicleLocked', False)
        self._addNumberProperty('lockedMissionIndex', 0)
        self._addBoolProperty('isVehicleInBattle', False)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isOpened', False)
        self._addBoolProperty('isInfoPageEnabled', False)
        self._addBoolProperty('areAnomaliesUnlocked', False)
        self._addBoolProperty('hasNewAnomaly', False)
        self.onAboutClick = self._addCommand('onAboutClick')
        self.onSlide = self._addCommand('onSlide')
        self.onPreview = self._addCommand('onPreview')
        self.onWidgetsUpdate = self._addCommand('onWidgetsUpdate')
        self.onTasksClick = self._addCommand('onTasksClick')
        self.onPacksClick = self._addCommand('onPacksClick')
        self.onComparisonClick = self._addCommand('onComparisonClick')
        self.onAnomaliesClick = self._addCommand('onAnomaliesClick')
        self.onViewLoaded = self._addCommand('onViewLoaded')
        self.onEnemyClick = self._addCommand('onEnemyClick')
        self.onBestiaryClick = self._addCommand('onBestiaryClick')
