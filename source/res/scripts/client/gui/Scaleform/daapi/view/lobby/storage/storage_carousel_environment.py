# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/storage_carousel_environment.py
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import ICarouselEnvironment
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import formatCountString
from gui.Scaleform.daapi.view.meta.StorageCarouselEnvironmentMeta import StorageCarouselEnvironmentMeta
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher as shared_events
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms
from gui.shared.formatters import text_styles
_SEARCH_INPUT_MAX_CHARS = 50

class StorageCarouselEnvironment(ICarouselEnvironment, IGlobalListener, StorageCarouselEnvironmentMeta):

    def __init__(self):
        super(StorageCarouselEnvironment, self).__init__()
        self._dataProvider = None
        self.__currentFilteredVehicles = 0
        self.__isFilterCounterShown = False
        return

    def clear(self):
        self._dataProvider = None
        self.__isFilterCounterShown = False
        return

    def setDataProvider(self, dp):
        self._dataProvider = dp
        self.__currentFilteredVehicles = self._dataProvider.getCurrentVehiclesCount()

    @property
    def filter(self):
        return self._dataProvider.filter if self._dataProvider is not None else None

    def applyFilter(self, forceApply=False):
        self._dataProvider.applyFilter(forceApply)
        self.updateCounter()

    def resetFilter(self):
        self.updateSearchInput()
        self.filter.reset()
        self.applyFilter()

    def blinkCounter(self):
        self.updateCounter()

    def formatCountVehicles(self):
        return formatCountString(self._dataProvider.getCurrentVehiclesCount(), self._dataProvider.getTotalVehiclesCount())

    def changeSearchNameVehicle(self, inputText):
        self.filter.update({'searchNameVehicle': inputText}, save=False)
        self.applyFilter()

    def showItemInfo(self, itemId):
        shared_events.showVehicleInfo(itemId)

    def updateCounter(self):
        shouldShow = not self.filter.isDefault()
        totalVehicles = self._dataProvider.getTotalVehiclesCount()
        if shouldShow and totalVehicles > 0:
            filteredVehicles = self._dataProvider.getCurrentVehiclesCount()
            drawAttention = filteredVehicles == 0
            self.as_updateCounterS(shouldShow, formatCountString(filteredVehicles, totalVehicles), drawAttention)
        else:
            self.as_updateCounterS(False, text_styles.stats(totalVehicles), False)

    def updateSearchInput(self, text=''):
        searchInputTooltip = makeTooltip(TANK_CAROUSEL_FILTER.TOOLTIP_SEARCHINPUT_HEADER, _ms(TANK_CAROUSEL_FILTER.TOOLTIP_SEARCHINPUT_BODY, count=_SEARCH_INPUT_MAX_CHARS))
        searchInputLabel = _ms(TANK_CAROUSEL_FILTER.POPOVER_LABEL_SEARCHNAMEVEHICLE)
        self.as_updateSearchS(searchInputLabel, text, searchInputTooltip, _SEARCH_INPUT_MAX_CHARS)
