# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/filter_popover.py
import logging
import itertools
import constants
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from gui import GUI_NATIONS
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform import getNationsFilterAssetPath, getVehicleTypeAssetPath, getLevelsAssetPath, getButtonsAssetPath
from gui.Scaleform.daapi.view.common.filter_contexts import FilterSetupContext, getFilterPopoverSetupContexts
from gui.Scaleform.daapi.view.meta.TankCarouselFilterPopoverMeta import TankCarouselFilterPopoverMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, VEHICLE_ACTION_GROUPS_LABELS_BY_CLASS, VEHICLE_ACTION_GROUPS_LABELS
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from new_year.ny_constants import NY_FILTER
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from skeletons.gui.game_control import IBattlePassController
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass import BattlePassFilterConsts
_logger = logging.getLogger(__name__)

class _SECTION(CONST_CONTAINER):
    NATIONS, VEHICLE_TYPES, LEVELS, SPECIALS, HIDDEN, PROGRESSIONS, TEXT_SEARCH, ROLES, ROLES_WITH_EXTRA = range(0, 9)


_VEHICLE_LEVEL_FILTERS = [ 'level_{}'.format(level) for level in VEHICLE_LEVELS ]

def _isRoleVisible(role, selectedVehicleTypes):
    if not selectedVehicleTypes:
        return True
    for vehicleType in selectedVehicleTypes:
        if role in VEHICLE_ACTION_GROUPS_LABELS_BY_CLASS[vehicleType]:
            return True

    return False


class VehiclesFilterPopover(TankCarouselFilterPopoverMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(VehiclesFilterPopover, self).__init__()
        self._carousel = None
        self._isRanked = False
        self._isFrontline = False
        if ctx and 'data' in ctx:
            data = ctx['data']
            self._isRanked = getattr(data, 'isRanked', False)
            self._isFrontline = getattr(data, 'isFrontline', False)
        self.__mapping = {}
        self.__usedFilters = ()
        return

    def setTankCarousel(self, carousel):
        self.__mapping = self._generateMapping(carousel.hasRentedVehicles() or not carousel.filter.isDefault(('rented',)), carousel.hasEventVehicles() or not carousel.filter.isDefault(('event',)), carousel.hasRoles(), carousel.hasBattleRoyaleVehicles())
        self.__usedFilters = list(itertools.chain.from_iterable(self.__mapping.itervalues()))
        self._carousel = carousel
        self._carousel.setPopoverCallback(self.__onCarouselSwitched)
        self._update(isInitial=True)

    def changeFilter(self, sectionId, itemId):
        if self._carousel is not None and self._carousel.filter is not None:
            self._carousel.filter.switch(self.__mapping[sectionId][itemId], save=False)
            self._update()
        return

    def changeSearchNameVehicle(self, inputText):
        self._carousel.filter.update({'searchNameVehicle': inputText}, save=False)
        self._update()

    def _getUpdateVO(self, filters):
        mapping = self.__mapping
        selectedTypes = [ vehType for vehType in mapping[_SECTION.VEHICLE_TYPES] if filters[vehType] ]
        return {'nations': [ filters[key] for key in mapping[_SECTION.NATIONS] ],
         'vehicleTypes': [ filters[key] for key in mapping[_SECTION.VEHICLE_TYPES] ],
         'levels': [ filters[key] for key in mapping[_SECTION.LEVELS] ],
         'specials': [ filters[key] for key in mapping[_SECTION.SPECIALS] ],
         'hidden': [ filters[key] for key in mapping[_SECTION.HIDDEN] ],
         'progressions': [ filters[key] for key in mapping[_SECTION.PROGRESSIONS] ],
         'roles': [ {'selected': filters[key],
                   'visible': _isRoleVisible(key, selectedTypes)} for key in mapping[_SECTION.ROLES] ]}

    def _getInitialVO(self, filters, xpRateMultiplier):
        mapping = self.__mapping
        dataVO = {'nationsSectionId': _SECTION.NATIONS,
         'vehicleTypesSectionId': _SECTION.VEHICLE_TYPES,
         'levelsSectionId': _SECTION.LEVELS,
         'specialSectionId': _SECTION.SPECIALS,
         'hiddenSectionId': _SECTION.HIDDEN,
         'progressionsSectionId': _SECTION.PROGRESSIONS,
         'rolesSectionId': _SECTION.ROLES_WITH_EXTRA,
         'titleLabel': text_styles.highTitle('#tank_carousel_filter:popover/title'),
         'nationsLabel': text_styles.standard('#tank_carousel_filter:popover/label/nations'),
         'vehicleTypesLabel': text_styles.standard('#tank_carousel_filter:popover/label/vehicleTypes'),
         'levelsLabel': text_styles.standard('#tank_carousel_filter:popover/label/levels'),
         'specialsLabel': text_styles.standard('#tank_carousel_filter:popover/label/specials'),
         'hiddenLabel': text_styles.standard('#tank_carousel_filter:popover/label/hidden'),
         'progressionsLabel': text_styles.standard('#tank_carousel_filter:popover/label/progressions'),
         'rolesLabel': text_styles.main('#tank_carousel_filter:popover/label/roles'),
         'searchInputLabel': backport.text(R.strings.tank_carousel_filter.popover.label.searchNameVehicle()),
         'searchInputName': filters.get('searchNameVehicle') or '',
         'searchInputTooltip': makeTooltip('#tank_carousel_filter:tooltip/searchInput/header', backport.text(R.strings.tank_carousel_filter.tooltip.searchInput.body(), count=50)),
         'searchInputMaxChars': 50,
         'nations': [],
         'vehicleTypes': [],
         'levels': [],
         'specials': [],
         'hidden': [],
         'progressions': [],
         'roles': [],
         'hiddenSectionVisible': True,
         'specialSectionVisible': True,
         'tankTierSectionVisible': True,
         'searchSectionVisible': True,
         'progressionsSectionVisible': False,
         'rolesSectionVisible': False,
         constants.ROLES_COLLAPSE: False,
         'changeableArrowDirection': False}

        def isSelected(entry):
            return filters.get(entry, False)

        for entry in mapping[_SECTION.NATIONS]:
            dataVO['nations'].append({'value': getNationsFilterAssetPath(entry),
             'tooltip': makeTooltip('#nations:{}'.format(entry), '#tank_carousel_filter:tooltip/nations/body'),
             'selected': isSelected(entry)})

        for entry in mapping[_SECTION.LEVELS]:
            dataVO['levels'].append({'value': getLevelsAssetPath(entry),
             'selected': isSelected(entry)})

        for entry in mapping[_SECTION.VEHICLE_TYPES]:
            dataVO['vehicleTypes'].append({'value': getVehicleTypeAssetPath(entry),
             'tooltip': makeTooltip('#menu:carousel_tank_filter/{}'.format(entry), '#tank_carousel_filter:tooltip/vehicleTypes/body'),
             'selected': isSelected(entry)})

        for entry in mapping[_SECTION.HIDDEN]:
            dataVO['hidden'].append({'label': text_styles.standard('#tank_carousel_filter:popover/checkbox/{}'.format(entry)),
             'tooltip': makeTooltip('#tank_carousel_filter:tooltip/{}/header'.format(entry), '#tank_carousel_filter:tooltip/{}/body'.format(entry)),
             'selected': isSelected(entry)})

        for entry in mapping[_SECTION.SPECIALS]:
            contexts = getFilterPopoverSetupContexts(xpRateMultiplier)
            filterCtx = contexts.get(entry, FilterSetupContext())
            tooltipRes = R.strings.tank_carousel_filter.tooltip.dyn(entry)
            dataVO['specials'].append({'value': getButtonsAssetPath(filterCtx.asset or entry),
             'tooltip': makeTooltip(backport.text(tooltipRes.header()) if tooltipRes else '', backport.text(tooltipRes.body(), **filterCtx.ctx)) if tooltipRes else '',
             'selected': isSelected(entry),
             'enabled': not (entry == 'bonus' and self._isFrontline)})

        for entry in mapping[_SECTION.PROGRESSIONS]:
            contexts = getFilterPopoverSetupContexts(xpRateMultiplier)
            filterCtx = contexts.get(entry, FilterSetupContext())
            tooltipRes = R.strings.tank_carousel_filter.tooltip.dyn(entry)
            dataVO['progressions'].append({'value': getButtonsAssetPath(filterCtx.asset or entry),
             'tooltip': makeTooltip(backport.text(tooltipRes.header()) if tooltipRes else '', backport.text(tooltipRes.body(), **filterCtx.ctx)) if tooltipRes else '',
             'selected': isSelected(entry)})

        selectedTypes = [ vehType for vehType in mapping[_SECTION.VEHICLE_TYPES] if isSelected(vehType) ]
        for entry in mapping[_SECTION.ROLES]:
            dataVO['roles'].append({'label': text_styles.mainSmall(backport.text(R.strings.menu.roleExp.actionsGroup.dyn(entry)())),
             'selected': isSelected(entry),
             'visible': _isRoleVisible(entry, selectedTypes)})

        if not dataVO['hidden']:
            dataVO['hiddenSectionVisible'] = False
        if not dataVO['specials']:
            dataVO['specialSectionVisible'] = False
        if self._isRanked:
            dataVO['rolesSectionVisible'] = True
            dataVO[constants.ROLES_COLLAPSE] = isSelected(constants.ROLES_COLLAPSE)
        return dataVO

    def _dispose(self):
        if self._carousel is not None and self._carousel.filter is not None:
            self._carousel.filter.save()
            self._carousel.blinkCounter()
        if self._carousel is not None:
            self._carousel.setPopoverCallback(None)
            self._carousel = None
        self.__mapping = {}
        self.__usedFilters = ()
        super(VehiclesFilterPopover, self)._dispose()
        return

    def _update(self, isInitial=False):
        filters = self._carousel.filter.getFilters(self.__usedFilters)
        xpRateMultiplier = self.itemsCache.items.shop.dailyXPFactor
        if isInitial:
            self.as_setInitDataS(self._getInitialVO(filters, xpRateMultiplier))
        else:
            self.as_setStateS(self._getUpdateVO(filters))
        self._carousel.applyFilter()
        self.as_showCounterS(text_styles.main(backport.text(R.strings.tank_carousel_filter.popover.counter(), count=self._carousel.formatCountVehicles())))

    @classmethod
    def _generateMapping(cls, hasRented, hasEvent, hasRoles, isBattleRoyaleEnabled=False):
        mapping = {_SECTION.NATIONS: GUI_NATIONS,
         _SECTION.VEHICLE_TYPES: VEHICLE_TYPES_ORDER,
         _SECTION.LEVELS: _VEHICLE_LEVEL_FILTERS,
         _SECTION.SPECIALS: [],
         _SECTION.HIDDEN: [],
         _SECTION.PROGRESSIONS: [],
         _SECTION.ROLES: VEHICLE_ACTION_GROUPS_LABELS if hasRoles else [],
         _SECTION.ROLES_WITH_EXTRA: VEHICLE_ACTION_GROUPS_LABELS + [constants.ROLES_COLLAPSE] if hasRoles else [],
         _SECTION.TEXT_SEARCH: ['searchNameVehicle']}
        if isBattleRoyaleEnabled:
            mapping[_SECTION.HIDDEN].append('battleRoyale')
        elif hasEvent:
            mapping[_SECTION.HIDDEN].append('event')
        if isBattleRoyaleEnabled and hasEvent:
            _logger.warning('It is not correct to show event and battleRoyale filters once')
        return mapping

    def __onCarouselSwitched(self):
        self.destroy()


class TankCarouselFilterPopover(VehiclesFilterPopover):
    _nyController = dependency.descriptor(INewYearController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, ctx):
        super(TankCarouselFilterPopover, self).__init__(ctx)
        setting = self.__settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
        self.__carouselRowCount = setting.get()

    def switchCarouselType(self, selected):
        setting = self.__settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
        self.__carouselRowCount = setting.CAROUSEL_TYPES.index(setting.OPTIONS.DOUBLE if selected else setting.OPTIONS.SINGLE)
        self._carousel.setRowCount(self.__carouselRowCount + 1)

    def _getInitialVO(self, filters, xpRateMultiplier):
        dataVO = super(TankCarouselFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        dataVO.update({'toggleSwitchCarouselTooltip': makeTooltip('#tank_carousel_filter:tooltip/toggleSwitchCarousel/header', '#tank_carousel_filter:tooltip/toggleSwitchCarousel/body'),
         'toggleSwitchCarouselIcon': RES_ICONS.MAPS_ICONS_FILTERS_DOUBLE_CAROUSEL,
         'toggleSwitchCarouselSelected': bool(self.__carouselRowCount)})
        return dataVO

    def _update(self, isInitial=False):
        super(TankCarouselFilterPopover, self)._update(isInitial)
        self._carousel.updateHotFilters()

    def _populate(self):
        super(TankCarouselFilterPopover, self)._populate()
        self._nyController.onStateChanged += self.__onNyStateChanged

    def _dispose(self):
        self._nyController.onStateChanged -= self.__onNyStateChanged
        super(TankCarouselFilterPopover, self)._dispose()
        self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, {settings_constants.GAME.CAROUSEL_TYPE: self.__carouselRowCount})

    @classmethod
    def _generateMapping(cls, hasRented, hasEvent, hasRoles, isBattleRoyaleEnabled=False):
        mapping = super(TankCarouselFilterPopover, cls)._generateMapping(hasRented, hasEvent, hasRoles, isBattleRoyaleEnabled)
        mapping[_SECTION.SPECIALS].extend(cls._getBaseSpecialSection())
        if hasRented:
            mapping[_SECTION.SPECIALS].append('rented')
        if hasEvent:
            mapping[_SECTION.SPECIALS].append('event')
        if constants.IS_KOREA:
            mapping[_SECTION.SPECIALS].append('igr')
        if cls._nyController.isVehicleBranchEnabled():
            mapping[_SECTION.SPECIALS].append(NY_FILTER)
        return mapping

    @classmethod
    def _getBaseSpecialSection(cls):
        return ['bonus',
         'favorite',
         'premium',
         'elite',
         'crystals']

    def __onNyStateChanged(self):
        self.destroy()


class BattlePassCarouselFilterPopover(TankCarouselFilterPopover):
    __battlePassController = dependency.descriptor(IBattlePassController)

    @classmethod
    def _generateMapping(cls, hasRented, hasEvent, hasRoles, isBattleRoyaleEnabled=False):
        mapping = super(BattlePassCarouselFilterPopover, cls)._generateMapping(hasRented, hasEvent, hasRoles)
        if cls.__battlePassController.isVisible():
            mapping[_SECTION.PROGRESSIONS].extend([BattlePassFilterConsts.FILTER_KEY_COMMON])
        return mapping

    def _getInitialVO(self, filters, xpRateMultiplier):
        dataVO = super(BattlePassCarouselFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        dataVO['progressionsSectionVisible'] = self.__battlePassController.isVisible()
        return dataVO


class BattleRoyaleCarouselFilterPopover(TankCarouselFilterPopover):

    @classmethod
    def _getBaseSpecialSection(cls):
        return ['bonus',
         'favorite',
         'premium',
         'elite']


class BattleTankCarouselFilterPopover(TankCarouselFilterPopover):

    def _getInitialVO(self, filters, xpRateMultiplier):
        dataVO = super(BattleTankCarouselFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        dataVO['specialSectionVisible'] = False
        dataVO['tankTierSectionVisible'] = False
        dataVO['searchSectionVisible'] = False
        dataVO['progressionsSectionVisible'] = False
        return dataVO

    def _generateMapping(self, hasRented, hasEvent, hasRoles, isBattleRoyaleEnabled=False):
        mapping = super(BattleTankCarouselFilterPopover, self)._generateMapping(hasRented, hasEvent, hasRoles, isBattleRoyaleEnabled)
        mapping[_SECTION.SPECIALS] = []
        if constants.IS_KOREA:
            mapping[_SECTION.SPECIALS].append('igr')
        return mapping


class StorageBlueprintsFilterPopover(VehiclesFilterPopover):

    def _getInitialVO(self, filters, xpRateMultiplier):
        vo = super(StorageBlueprintsFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        vo['searchSectionVisible'] = False
        vo['hiddenSectionVisible'] = True
        vo['changeableArrowDirection'] = True
        vo['progressionsSectionVisible'] = False
        for entry in vo['hidden']:
            entry['tooltip'] = None

        return vo

    @classmethod
    def _generateMapping(cls, hasRented, hasEvent, hasRoles, isBattleRoyaleEnabled=False):
        mapping = super(StorageBlueprintsFilterPopover, cls)._generateMapping(hasRented, hasEvent, hasRoles, isBattleRoyaleEnabled)
        mapping[_SECTION.HIDDEN].append('unlock_available')
        return mapping
