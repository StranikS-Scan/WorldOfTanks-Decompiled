# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/filter_popover.py
import itertools
import constants
from gui import makeHtmlString, GUI_NATIONS
from gui.Scaleform import getNationsFilterAssetPath, getVehicleTypeAssetPath, getLevelsAssetPath
from gui.Scaleform.daapi.view.meta.TankCarouselFilterPopoverMeta import TankCarouselFilterPopoverMeta
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.shared import g_itemsCache
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms
from shared_utils import CONST_CONTAINER

class _SECTION(CONST_CONTAINER):
    NATIONS = 0
    VEHICLE_TYPES = 1
    LEVELS = 2
    SPECIALS = 3
    HIDDEN = 4


_VEHICLE_LEVEL_FILTERS = [ 'level_{}'.format(level) for level in VEHICLE_LEVELS ]

def _getInitialVO(filters, mapping, xpRateMultiplier):
    dataVO = {'nationsSectionId': _SECTION.NATIONS,
     'vehicleTypesSectionId': _SECTION.VEHICLE_TYPES,
     'levelsSectionId': _SECTION.LEVELS,
     'specialSectionId': _SECTION.SPECIALS,
     'hiddenSectionId': _SECTION.HIDDEN,
     'titleLabel': text_styles.highTitle('#tank_carousel_filter:popover/title'),
     'nationsLabel': text_styles.standard('#tank_carousel_filter:popover/label/nations'),
     'vehicleTypesLabel': text_styles.standard('#tank_carousel_filter:popover/label/vehicleTypes'),
     'levelsLabel': text_styles.standard('#tank_carousel_filter:popover/label/levels'),
     'specialsLabel': text_styles.standard('#tank_carousel_filter:popover/label/specials'),
     'hiddenLabel': text_styles.standard('#tank_carousel_filter:popover/label/hidden'),
     'defaultButtonLabel': _ms('#tank_carousel_filter:popover/label/defaultButton'),
     'nations': [],
     'vehicleTypes': [],
     'levels': [],
     'specials': [],
     'hidden': [],
     'defaultButtonTooltip': makeTooltip('#tank_carousel_filter:tooltip/defaultButton/header', '#tank_carousel_filter:tooltip/defaultButton/body'),
     'hiddenSectionVisible': True}
    for entry in mapping[_SECTION.NATIONS]:
        dataVO['nations'].append({'value': getNationsFilterAssetPath(entry),
         'tooltip': makeTooltip('#nations:{}'.format(entry), '#tank_carousel_filter:tooltip/nations/body'),
         'selected': filters[entry]})

    for entry in mapping[_SECTION.LEVELS]:
        dataVO['levels'].append({'value': getLevelsAssetPath(entry),
         'selected': filters[entry]})

    for entry in mapping[_SECTION.VEHICLE_TYPES]:
        dataVO['vehicleTypes'].append({'value': getVehicleTypeAssetPath(entry),
         'tooltip': makeTooltip('#menu:carousel_tank_filter/{}'.format(entry), '#tank_carousel_filter:tooltip/vehicleTypes/body'),
         'selected': filters[entry]})

    for entry in mapping[_SECTION.HIDDEN]:
        dataVO['hidden'].append({'label': text_styles.standard('#tank_carousel_filter:popover/checkbox/{}'.format(entry)),
         'tooltip': makeTooltip('#tank_carousel_filter:tooltip/{}/header'.format(entry), '#tank_carousel_filter:tooltip/{}/body'.format(entry)),
         'selected': filters[entry]})

    for entry in mapping[_SECTION.SPECIALS]:
        if entry == 'bonus':
            ctx = {'multiplier': xpRateMultiplier}
        else:
            ctx = {}
        dataVO['specials'].append({'label': makeHtmlString('html_templates:lobby/carousel_filter/popover', entry, ctx),
         'tooltip': makeTooltip('#tank_carousel_filter:tooltip/{}/header'.format(entry), _ms('#tank_carousel_filter:tooltip/{}/body'.format(entry), **ctx)),
         'selected': filters[entry]})

    if not dataVO['hidden']:
        dataVO['hiddenSectionVisible'] = False
    return dataVO


def _getUpdateVO(filters, mapping):
    return {'nations': [ filters[key] for key in mapping[_SECTION.NATIONS] ],
     'vehicleTypes': [ filters[key] for key in mapping[_SECTION.VEHICLE_TYPES] ],
     'levels': [ filters[key] for key in mapping[_SECTION.LEVELS] ],
     'specials': [ filters[key] for key in mapping[_SECTION.SPECIALS] ],
     'hidden': [ filters[key] for key in mapping[_SECTION.HIDDEN] ]}


class FilterPopover(TankCarouselFilterPopoverMeta):
    """ Tank carousel filter popover with additional filters.
    
    There is a sections mechanism in this class. The main idea is that
    all the filters are placed in different sections (like, nations section,
    vehicles section, levels section, etc), and each section has its own id
    (defined in _SECTIONS). Each filter option (item) inside section has an
    id too (i.e. index).
    
    Flash sends updates in form of (sectionId, itemId), without the value,
    and we simply switch corresponding filter.
    
    The mapping (belongings of filters to sections) is calculated on runtime
    during popover initialization (because content of sections may vary).
    """

    def __init__(self, ctx=None):
        super(FilterPopover, self).__init__()
        self.__tankCarousel = None
        self.__mapping = {}
        self.__usedFilters = ()
        return

    def setTankCarousel(self, tankCarousel):
        """ Set tank carousel to the popover.
        
        This method is called on popover view load and substitutes _populate method,
        because all necessery data comes from carousel.
        
        :param tankCarousel: instance of TankCarousel.
        """
        self.__generateMapping(tankCarousel.hasRentedVehicles(), tankCarousel.hasEventVehicles())
        self.__tankCarousel = tankCarousel
        self.__update(isInitial=True)

    def changeFilter(self, sectionId, itemId):
        """Switch boolean value of the filter entry.
        
        :param sectionId: id of the section defined in _SECTION
        :param itemId: index of the filter inside self._mapping
        """
        self.__filter.switch(self.__mapping[sectionId][itemId], save=False)
        self.__update()

    def setDefaultFilter(self):
        """ Reset popover filters (without touching carousel filters).
        """
        self.__filter.reset(self.__usedFilters, save=False)
        self.__update()

    def _dispose(self):
        if self.__tankCarousel is not None and self.__tankCarousel.filter is not None:
            self.__filter.save()
            self.__tankCarousel.blinkCounter()
            self.__tankCarousel = None
        self.__mapping = {}
        self.__usedFilters = ()
        super(FilterPopover, self)._dispose()
        return

    def __generateMapping(self, hasRented, hasEvent):
        """ Generate mapping of currently used filters to the sections in popover.
        
        :param hasRented: boolean, specifies whether rented checkbox should appear in popover
        :param hasEvent: boolean, specifies whether event checkbox should appear in popover
        """
        self.__mapping = {_SECTION.NATIONS: GUI_NATIONS,
         _SECTION.VEHICLE_TYPES: VEHICLE_TYPES_ORDER,
         _SECTION.LEVELS: _VEHICLE_LEVEL_FILTERS,
         _SECTION.SPECIALS: ['elite',
                             'premium',
                             'favorite',
                             'bonus'],
         _SECTION.HIDDEN: []}
        if hasRented:
            self.__mapping[_SECTION.HIDDEN].append('hideRented')
        if hasEvent:
            self.__mapping[_SECTION.HIDDEN].append('hideEvent')
        if constants.IS_KOREA:
            self.__mapping[_SECTION.SPECIALS].append('igr')
        self.__usedFilters = list(itertools.chain.from_iterable(self.__mapping.itervalues()))

    def __update(self, isInitial=False):
        """ Update state of the flash.
        
        :param isInitial: boolean, specifies whether flash should be initialized or updated
        """
        filters = self.__filter.getFilters(self.__usedFilters)
        isDefault = self.__filter.isDefault(self.__usedFilters)
        xpRateMultiplier = g_itemsCache.items.shop.dailyXPFactor
        if isInitial:
            self.as_setInitDataS(_getInitialVO(filters, self.__mapping, xpRateMultiplier))
        else:
            self.as_setStateS(_getUpdateVO(filters, self.__mapping))
        self.as_enableDefBtnS(not isDefault)
        self.__tankCarousel.applyFilter()
        self.__tankCarousel.updateHotFilters()

    @property
    def __filter(self):
        return self.__tankCarousel.filter
