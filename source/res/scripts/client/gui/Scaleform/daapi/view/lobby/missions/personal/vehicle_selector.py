# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/personal/vehicle_selector.py
from account_helpers.AccountSettings import PM_SELECTOR_FILTER, AccountSettings
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.missions.vehicle_selector import MissionVehicleSelector, MissionVehicleSelectorCarousel, _MissionsCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.vehicle_carousel.carousel_data_provider import sortedIndices
from gui.Scaleform.daapi.view.lobby.vehicle_carousel.carousel_filter import CarouselFilter
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.shared.formatters import text_styles
from helpers import dependency
from helpers.i18n import makeString as ms
from skeletons.gui.server_events import IEventsCache

class PersonalMissionVehicleSelector(MissionVehicleSelector):
    """ Vehicle selector for a regular quest.
    Vehicle selector is used to select vehicle among suitable for the quest
    (based on vehicle requirements section in quest).
    """
    eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(PersonalMissionVehicleSelector, self).__init__()
        self.__questID = None
        return

    def setSelectedQuest(self, questID):
        self.__questID = questID

    def _getTitle(self):
        if self.__questID:
            quest = self.eventsCache.personalMissions.getQuests()[self.__questID]
            return text_styles.highTitle(ms(QUESTS.PERSONALMISSION_VEHICLESELECTOR_TITLE, vehType=', '.join([ ms(MENU.classesShort(vehType)) for vehType in quest.getVehicleClasses() ]), minLevel=quest.getVehMinLevel(), maxLevel=quest.getVehMaxLevel()))

    @classmethod
    def _getCarouselAlias(cls):
        return QUESTS_ALIASES.PERSONAL_MISSIONS_VEHICLE_SELECTOR_CAROUSEL_ALIAS


class PersonalVehicleSelectorCarousel(MissionVehicleSelectorCarousel):
    """ Carousel for displaying suitable vehicles for a regular quest.
    """

    def __init__(self):
        super(PersonalVehicleSelectorCarousel, self).__init__()
        self._carouselDPCls = _PersonalMissionsCarouselDataProvider
        self._usedFilters = tuple()
        self._carouselFilterCls = _PMCarouselFilter

    def _setCarouselFilters(self):
        self.as_initCarouselFilterS({'isVisible': False})


class _PMCarouselFilter(CarouselFilter):
    """ Carousel filter for missions vehicle selector.
    
    This filter utilizes same sections as hangar carousel, but has specific
    saving and loading rules.
    """

    def __init__(self):
        super(_PMCarouselFilter, self).__init__()
        self._serverSections += (PM_SELECTOR_FILTER,)

    def load(self):
        filters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            filters.update(AccountSettings.getFilterDefault(section))

        self._filters = filters
        self.update(filters, save=False)

    def save(self):
        pass


class _PersonalMissionsCarouselDataProvider(_MissionsCarouselDataProvider):
    """ Carousel data provider for personal missions vehicle selector.
    """

    @classmethod
    def _vehicleComparisonKey(cls, vehicle):
        """ Get comparison key for a vehicle.
        
        :param vehicle: instance of gui_items.Vehicle
        :return: tuple with comparison keys
        """
        nationsCount = len(GUI_NATIONS_ORDER_INDEX)
        return (vehicle.isFavorite,
         vehicle.level,
         vehicle.isReadyToFight,
         nationsCount - GUI_NATIONS_ORDER_INDEX[vehicle.nationName])

    def _getSortedIndices(self):
        return self._getCachedSortedIndices(True)
