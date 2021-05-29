# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/storage/blueprints/blueprints_storage_view.py
import nations
from CurrentVehicle import g_currentVehicle
from blueprints.BlueprintTypes import BlueprintTypes
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.blueprints import BlueprintsStorageCarouselDataProvider, blueprintExitEvent
from gui.Scaleform.daapi.view.lobby.storage.blueprints import BlueprintsStorageCarouselFilter
from gui.Scaleform.daapi.view.lobby.storage.storage_carousel_environment import StorageCarouselEnvironment
from gui.Scaleform.daapi.view.meta.StorageCategoryBlueprintsViewMeta import StorageCategoryBlueprintsViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.impl import backport
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.requesters.blueprints_requester import getNationalFragmentCD
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.STORAGE import STORAGE
from gui import GUI_NATIONS
from WeakMethod import WeakMethodProxy
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

class StorageCategoryBlueprintsView(StorageCategoryBlueprintsViewMeta, StorageCarouselEnvironment):
    __lobbyCtx = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(StorageCategoryBlueprintsView, self).__init__()
        self.__needToResetScrollTo = True

    def navigateToBlueprintScreen(self, itemId):
        self.filter.update({'scroll_to': itemId})
        self.__needToResetScrollTo = False
        shared_events.showBlueprintView(itemId, blueprintExitEvent())

    def selectConvertible(self, value):
        self.filter.update({'can_convert': value})
        self.applyFilter()

    def _populate(self):
        super(StorageCategoryBlueprintsView, self).setDataProvider(self._dataProvider)
        super(StorageCategoryBlueprintsView, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self._dataProvider.setEnvironment(self.app)
        g_clientUpdateManager.addCallbacks({'blueprints': self.__onUpdateBlueprints,
         'serverSettings.blueprints_config.levels': self.__onUpdateBlueprints})
        self.__currentFilteredVehicles = self._dataProvider.getCurrentVehiclesCount()
        self.__isFilterCounterShown = False
        self.__updateUniversalFragments()
        self.updateSearchInput(self.filter.get('searchNameVehicle'))
        self.__updateVehicles()
        self.__restoreCarouselState()
        self.updateCounter()

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__needToResetScrollTo:
            self.filter.update({'can_convert': False})
        super(StorageCategoryBlueprintsView, self)._dispose()
        super(StorageCategoryBlueprintsView, self).clear()

    def _createDataProvider(self):
        return BlueprintsStorageCarouselDataProvider(BlueprintsStorageCarouselFilter(), self._itemsCache, g_currentVehicle, WeakMethodProxy(self.__updateFilterWarning))

    def _onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.CLIENT_UPDATE:
            self._dataProvider.buildList()
            self.updateCounter()
        if GUI_ITEM_TYPE.VEHICLE in diff:
            self.__updateVehicles(diff.get(GUI_ITEM_TYPE.VEHICLE))

    @staticmethod
    def __makeFragmentVO(count, iconName, tooltipData=None):
        style = text_styles.stats if count > 0 else text_styles.main
        label = style(backport.getIntegralFormat(count))
        return {'hasFragments': count > 0,
         'label': label,
         'iconSmall': RES_ICONS.getBlueprintFragment('small', iconName),
         'iconBig': RES_ICONS.getBlueprintFragment('big', iconName),
         'tooltipData': tooltipData}

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.settings is not None and view.settings.alias == VIEW_ALIAS.STORAGE_BLUEPRINTS_FILTER_POPOVER:
            view.setTankCarousel(self)
        return

    def __onUpdateBlueprints(self, _):
        self.__updateVehicles()
        self.updateCounter()
        self.__updateUniversalFragments()

    def __updateVehicles(self, vehicles=None, filterCriteria=None):
        self._dataProvider.updateVehicles(vehicles, filterCriteria)
        hasNoVehicles = self._dataProvider.getTotalVehiclesCount() == 0
        self.as_showDummyScreenS(hasNoVehicles)

    def __updateUniversalFragments(self):
        self.__updateIntelligence()
        self.__updateNationFragments()

    def __updateNationFragments(self):
        result = []
        fragments = self._itemsCache.items.blueprints.getAllNationalFragmentsData()
        for nationName in GUI_NATIONS:
            nationId = nations.INDICES.get(nationName, nations.NONE_INDEX)
            nationTooltipData = getNationalFragmentCD(nationId)
            result.append(self.__makeFragmentVO(fragments.get(nationId, 0), nationName, nationTooltipData))

        self.as_updateNationalFragmentsS(result)

    def __updateIntelligence(self):
        self.as_updateIntelligenceDataS(self.__makeFragmentVO(self._itemsCache.items.blueprints.getIntelligenceCount(), 'intelligence', BlueprintTypes.INTELLIGENCE_DATA))

    def __updateFilterWarning(self):
        hasNoVehicles = self._dataProvider.getTotalVehiclesCount() == 0
        hasNoFilterResults = self._dataProvider.getCurrentVehiclesCount() == 0
        filterWarningVO = None
        if hasNoFilterResults and not hasNoVehicles:
            filterWarningVO = self._makeFilterWarningVO(STORAGE.FILTER_WARNINGMESSAGE, STORAGE.FILTER_NORESULTSBTN_LABEL, TOOLTIPS.STORAGE_FILTER_NORESULTSBTN)
        self.as_showFilterWarningS(filterWarningVO)
        return

    def __restoreCarouselState(self):
        self.as_updateCanConvertS(self.filter.get('can_convert'))
        self.updateSearchInput(self.filter.get('searchNameVehicle'))
        self.applyFilter()
        scrollTo = self.filter.get('scroll_to')
        if scrollTo is not None:
            self.as_scrollToItemS(scrollTo)
        return
