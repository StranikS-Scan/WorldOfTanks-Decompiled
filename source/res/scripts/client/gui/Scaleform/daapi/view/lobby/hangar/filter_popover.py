# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/filter_popover.py
import itertools
import constants
from gui import GUI_NATIONS
from gui.Scaleform import getNationsFilterAssetPath, getVehicleTypeAssetPath, getLevelsAssetPath
from gui.Scaleform.daapi.view.meta.TankCarouselFilterPopoverMeta import TankCarouselFilterPopoverMeta
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER
from gui.shared.formatters import text_styles, icons
from gui.shared.utils.functions import makeTooltip
from helpers.i18n import makeString as _ms
from shared_utils import CONST_CONTAINER

class _SECTIONS(CONST_CONTAINER):
    NATION = 0
    VEHICLE_TYPE = 1
    LEVELS = 2
    SPECIAL_LEFT = 3
    SPECIAL_RIGHT = 4
    RENT_VEHICLE = 5


_VEHICLE_LEVEL_FILTERS = [ 'level_{}'.format(level) for level in VEHICLE_LEVELS ]
_SECTIONS_MAP = {_SECTIONS.NATION: GUI_NATIONS,
 _SECTIONS.VEHICLE_TYPE: VEHICLE_TYPES_ORDER,
 _SECTIONS.SPECIAL_LEFT: ('premium',),
 _SECTIONS.SPECIAL_RIGHT: ('elite',),
 _SECTIONS.LEVELS: _VEHICLE_LEVEL_FILTERS,
 _SECTIONS.RENT_VEHICLE: ('hideRented',)}
if constants.IS_KOREA:
    _SECTIONS_MAP[_SECTIONS.SPECIAL_LEFT] = _SECTIONS_MAP[_SECTIONS.SPECIAL_LEFT] + ('igr',)
_POPOVER_FILERS = set(itertools.chain.from_iterable(_SECTIONS_MAP.values()))

def _getInitialVO(filters, hasRentedVehicles):
    dataVO = {'nationTypeId': _SECTIONS.NATION,
     'vehicleTypeId': _SECTIONS.VEHICLE_TYPE,
     'specialTypesLeftId': _SECTIONS.SPECIAL_LEFT,
     'specialTypesRightId': _SECTIONS.SPECIAL_RIGHT,
     'levelTypesId': _SECTIONS.LEVELS,
     'rentVehicleId': _SECTIONS.RENT_VEHICLE,
     'titleLabel': text_styles.highTitle('#tank_carousel_filter:filter/popover/title'),
     'nationLabel': text_styles.standard('#tank_carousel_filter:filter/popover/label/nation'),
     'vehicleTypeLabel': text_styles.standard('#tank_carousel_filter:filter/popover/label/vehicle'),
     'vehicleLevelLabel': text_styles.standard('#tank_carousel_filter:filter/popover/label/vehicleLevel'),
     'vehicleEliteTypeLabel': text_styles.standard('#tank_carousel_filter:filter/popover/label/vehicleEliteType'),
     'btnDefaultTooltip': makeTooltip('#tank_carousel_filter:filter/popover/tooltip/defaultBtn/header', '#tank_carousel_filter:filter/popover/tooltip/defaultBtn/body'),
     'btnDefaultLabel': _ms('#tank_carousel_filter:filter/popover/label/defaultBtn'),
     'specialTypeLeft': [{'label': text_styles.standard('#tank_carousel_filter:filter/popover/checkBox/Premium'),
                          'tooltip': makeTooltip('#tank_carousel_filter:filter/popover/tooltip/premium/header', '#tank_carousel_filter:filter/popover/tooltip/premium/body'),
                          'selected': filters['premium']}],
     'specialTypeRight': [{'label': text_styles.standard('#tank_carousel_filter:filter/popover/checkBox/Elite'),
                           'tooltip': makeTooltip('#tank_carousel_filter:filter/popover/tooltip/elite/header', '#tank_carousel_filter:filter/popover/tooltip/elite/body'),
                           'selected': filters['elite']}],
     'nationsType': [],
     'vehicleType': [],
     'levelsType': [],
     'hasRentedVehicles': hasRentedVehicles,
     'rentCheckBox': {'label': text_styles.standard('#tank_carousel_filter:filter/popover/label/vehicleLease'),
                      'selected': filters['hideRented'],
                      'enabled': not filters['igr'] if constants.IS_KOREA else True}}
    if constants.IS_KOREA:
        dataVO['specialTypeLeft'].append({'label': icons.premiumIgrSmall(),
         'selected': filters['igr']})
    for nation in GUI_NATIONS:
        dataVO['nationsType'].append({'value': getNationsFilterAssetPath(nation),
         'tooltip': makeTooltip(_ms('#nations:%s' % nation), _ms('#tank_carousel_filter:filter/popover/tooltip/nation/body')),
         'selected': filters[nation]})

    for level in VEHICLE_LEVELS:
        dataVO['levelsType'].append({'value': getLevelsAssetPath(level),
         'selected': filters['level_%d' % level]})

    for vehicleType in VEHICLE_TYPES_ORDER:
        dataVO['vehicleType'].append({'value': getVehicleTypeAssetPath(vehicleType),
         'tooltip': makeTooltip(_ms('#menu:carousel_tank_filter/%s' % vehicleType), _ms('#tank_carousel_filter:filter/popover/tooltip/vehicleType/body')),
         'selected': filters[vehicleType]})

    return dataVO


def _getUpdateVO(filters):
    return {'rentSelected': filters['hideRented'],
     'rentEnabled': not filters['igr'] if constants.IS_KOREA else True,
     'levelsTypeSelected': [ filters[level] for level in _VEHICLE_LEVEL_FILTERS ],
     'nationTypeSelected': [ filters[nation] for nation in GUI_NATIONS ],
     'vehicleTypeSelected': [ filters[vehType] for vehType in VEHICLE_TYPES_ORDER ],
     'specialTypeLeftSelected': [ filters[key] for key in _SECTIONS_MAP[_SECTIONS.SPECIAL_LEFT] ],
     'specialTypeRightSelected': [ filters[key] for key in _SECTIONS_MAP[_SECTIONS.SPECIAL_RIGHT] ]}


class FilterPopover(TankCarouselFilterPopoverMeta):
    """ Tank carousel filter popover with additional filters.
    
    There is a sections mechanism in this class. The main idea is that
    all the filters are placed in different sections (like, nations section,
    vehicles section, levels section, etc), and each section has it's own id
    (defined in _SECTIONS). Each filter option (item) inside section has an id too.
    
    Flash sends the updates in form of (sectionId, itemId), without the value,
    and we simply switch corresponding filter.
    """

    def __init__(self, ctx=None):
        super(FilterPopover, self).__init__()
        self.__tankCarousel = None
        return

    def setTankCarousel(self, tankCarousel):
        self.__tankCarousel = tankCarousel
        self.as_setInitDataS(_getInitialVO(self.__filter.getFilters(_POPOVER_FILERS), self.__tankCarousel.hasRentedVehicles()))
        self.as_enableDefBtnS(not self.__filter.isDefault(_POPOVER_FILERS))

    def changeFilter(self, sectionId, itemId):
        """Switch boolean value of the filter entry
        
        :param sectionId: id of the section with filters (defined in _SECTIONS)
        :param itemId: index number of the filter option
        """
        self.__filter.switch(_SECTIONS_MAP[sectionId][itemId], save=False)
        self.__update()

    def setDefaultFilter(self):
        """ Reset only popover filters
        """
        self.__filter.reset(_POPOVER_FILERS, save=False)
        self.__update()

    def _dispose(self):
        if self.__tankCarousel is not None and self.__tankCarousel.filter is not None:
            self.__filter.save()
            self.__tankCarousel.blinkCounter()
            self.__tankCarousel = None
        super(FilterPopover, self)._dispose()
        return

    def __update(self):
        self.as_setStateS(_getUpdateVO(self.__filter.getFilters(_POPOVER_FILERS)))
        self.as_enableDefBtnS(not self.__filter.isDefault(_POPOVER_FILERS))
        self.__tankCarousel.applyFilter()

    @property
    def __filter(self):
        return self.__tankCarousel.filter
