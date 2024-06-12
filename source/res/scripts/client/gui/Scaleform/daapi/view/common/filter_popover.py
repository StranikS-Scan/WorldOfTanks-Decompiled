# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/filter_popover.py
import itertools
import logging
import typing
import constants
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from gui import GUI_NATIONS
from gui.Scaleform import getNationsFilterAssetPath, getVehicleTypeAssetPath, getLevelsAssetPath, getButtonsAssetPath
from gui.Scaleform.daapi.view.common.filter_contexts import FilterSetupContext, getFilterPopoverSetupContexts
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_filter import FILTER_KEYS
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass import BattlePassFilterConsts
from gui.Scaleform.daapi.view.meta.TankCarouselFilterPopoverMeta import TankCarouselFilterPopoverMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.shared.formatters import text_styles
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, VEHICLE_ROLES_LABELS, VEHICLE_ROLES_LABELS_BY_CLASS
from gui.shared.utils.functions import makeTooltip
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from helpers.i18n import makeString as _ms
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import ICarouselEnvironment
_logger = logging.getLogger(__name__)

class FILTER_SECTION(CONST_CONTAINER):
    NATIONS, VEHICLE_TYPES, LEVELS, SPECIALS, HIDDEN, PROGRESSIONS, TEXT_SEARCH, ROLES, ROLES_WITH_EXTRA = range(0, 9)


_VEHICLE_LEVEL_FILTERS = [ 'level_{}'.format(level) for level in VEHICLE_LEVELS ]

class VehiclesFilterPopover(TankCarouselFilterPopoverMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx):
        super(VehiclesFilterPopover, self).__init__()
        self._carousel = None
        self._isFrontline = False
        self._isRanked = False
        self._isComp7 = False
        self._withRoles = False
        if ctx and 'data' in ctx:
            data = ctx['data']
            self._isFrontline = getattr(data, 'isFrontline', False)
            self._isRanked = getattr(data, 'isRanked', False)
            self._isComp7 = getattr(data, 'isComp7', False)
        self.__mapping = {}
        self.__usedFilters = ()
        return

    def setTankCarousel(self, carousel):
        customParams = carousel.getCustomParams()
        customParams['isRanked'] = self._isRanked
        customParams['isComp7'] = self._isComp7
        self.__mapping = self._generateMapping((carousel.hasRentedVehicles() or not carousel.filter.isDefault((FILTER_KEYS.RENTED,))), (carousel.hasEventVehicles() or not carousel.filter.isDefault((FILTER_KEYS.EVENT,))), carousel.hasRoles(), **customParams)
        self.__usedFilters = list(itertools.chain.from_iterable(self.__mapping.itervalues()))
        self._carousel = carousel
        self._carousel.setPopoverCallback(self.__onCarouselSwitched)
        self._update(isInitial=True)

    def changeFilter(self, sectionId, itemId):
        if self._carousel is not None and self._carousel.filter is not None:
            if sectionId == FILTER_SECTION.ROLES or sectionId == FILTER_SECTION.ROLES_WITH_EXTRA:
                filters = self._carousel.filter.getFilters(self.__usedFilters)
                target = self.__mapping[FILTER_SECTION.ROLES][self.__getSelectedVehType(filters)][itemId]
            else:
                target = self.__mapping[sectionId][itemId]
            self._carousel.filter.switch(target, save=False)
            self._update()
        return

    def changeSearchNameVehicle(self, inputText):
        self._carousel.filter.update({'searchNameVehicle': inputText}, save=False)
        self._update()

    def _getUpdateVO(self, filters):
        mapping = self.__mapping
        vehType = self.__getSelectedVehType(filters)
        return {'nations': [ filters[key] for key in mapping[FILTER_SECTION.NATIONS] ],
         'vehicleTypes': [ filters[key] for key in mapping[FILTER_SECTION.VEHICLE_TYPES] ],
         'levels': [ filters[key] for key in mapping[FILTER_SECTION.LEVELS] ],
         'specials': [ filters[key] for key in mapping[FILTER_SECTION.SPECIALS] ],
         'hidden': [ filters[key] for key in mapping[FILTER_SECTION.HIDDEN] ],
         'progressions': [ filters[key] for key in mapping[FILTER_SECTION.PROGRESSIONS] ],
         'roles': {vType:[ filters[role] for role in mapping[FILTER_SECTION.ROLES].get(vType, []) ] for vType in mapping[FILTER_SECTION.VEHICLE_TYPES]},
         'rolesLabel': self.__getRolesLabel(vehType),
         'rolesSectionVisible': self._withRoles and vehType is not None}

    def _getInitialVO(self, filters, xpRateMultiplier):
        mapping = self.__mapping
        vehType = self.__getSelectedVehType(filters)
        dataVO = {'nationsSectionId': FILTER_SECTION.NATIONS,
         'vehicleTypesSectionId': FILTER_SECTION.VEHICLE_TYPES,
         'levelsSectionId': FILTER_SECTION.LEVELS,
         'specialSectionId': FILTER_SECTION.SPECIALS,
         'hiddenSectionId': FILTER_SECTION.HIDDEN,
         'progressionsSectionId': FILTER_SECTION.PROGRESSIONS,
         'rolesSectionId': FILTER_SECTION.ROLES_WITH_EXTRA,
         'titleLabel': text_styles.highTitle('#tank_carousel_filter:popover/title'),
         'nationsLabel': text_styles.standard('#tank_carousel_filter:popover/label/nations'),
         'vehicleTypesLabel': text_styles.standard('#tank_carousel_filter:popover/label/vehicleTypes'),
         'levelsLabel': text_styles.standard('#tank_carousel_filter:popover/label/levels'),
         'specialsLabel': text_styles.standard('#tank_carousel_filter:popover/label/specials'),
         'hiddenLabel': text_styles.standard('#tank_carousel_filter:popover/label/hidden'),
         'progressionsLabel': text_styles.standard('#tank_carousel_filter:popover/label/progressions'),
         'rolesLabel': self.__getRolesLabel(vehType),
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
         'roles': {},
         'hiddenSectionVisible': True,
         'specialSectionVisible': True,
         'tankTierSectionVisible': True,
         'searchSectionVisible': True,
         'progressionsSectionVisible': False,
         'rolesSectionVisible': False,
         'changeableArrowDirection': False}

        def isSelected(entry):
            return filters.get(entry, False)

        for entry in mapping[FILTER_SECTION.NATIONS]:
            dataVO['nations'].append({'value': getNationsFilterAssetPath(entry),
             'tooltip': makeTooltip('#nations:{}'.format(entry), '#tank_carousel_filter:tooltip/nations/body'),
             'selected': isSelected(entry)})

        for entry in mapping[FILTER_SECTION.LEVELS]:
            dataVO['levels'].append({'value': getLevelsAssetPath(entry),
             'selected': isSelected(entry)})

        for entry in mapping[FILTER_SECTION.VEHICLE_TYPES]:
            dataVO['vehicleTypes'].append({'value': getVehicleTypeAssetPath(entry),
             'tooltip': makeTooltip('#menu:carousel_tank_filter/{}'.format(entry), '#tank_carousel_filter:tooltip/vehicleTypes/body'),
             'selected': isSelected(entry)})

        for entry in mapping[FILTER_SECTION.HIDDEN]:
            dataVO['hidden'].append({'label': text_styles.standard('#tank_carousel_filter:popover/checkbox/{}'.format(entry)),
             'tooltip': makeTooltip('#tank_carousel_filter:tooltip/{}/header'.format(entry), '#tank_carousel_filter:tooltip/{}/body'.format(entry)),
             'selected': isSelected(entry)})

        for entry in mapping[FILTER_SECTION.SPECIALS]:
            contexts = getFilterPopoverSetupContexts(xpRateMultiplier)
            filterCtx = contexts.get(entry, FilterSetupContext())
            tooltipRes = R.strings.tank_carousel_filter.tooltip.dyn(entry)
            enabled = not (entry == FILTER_KEYS.BONUS and self._isFrontline)
            dataVO['specials'].append(self._packSpecial(entry, filterCtx, isSelected(entry), tooltipRes, enabled))

        for entry in mapping[FILTER_SECTION.PROGRESSIONS]:
            contexts = getFilterPopoverSetupContexts(xpRateMultiplier)
            filterCtx = contexts.get(entry, FilterSetupContext())
            tooltipRes = R.strings.tank_carousel_filter.tooltip.dyn(entry)
            dataVO['progressions'].append({'value': getButtonsAssetPath(filterCtx.asset or entry),
             'tooltip': makeTooltip(backport.text(tooltipRes.header()) if tooltipRes else '', backport.text(tooltipRes.body(), **filterCtx.ctx)) if tooltipRes else '',
             'selected': isSelected(entry)})

        for vType in mapping[FILTER_SECTION.VEHICLE_TYPES]:
            dataVO['roles'][vType] = [ self.__getRoleVO(entry, filters) for entry in mapping[FILTER_SECTION.ROLES].get(vType, []) if entry is not None ]

        if not dataVO['hidden']:
            dataVO['hiddenSectionVisible'] = False
        if not dataVO['specials']:
            dataVO['specialSectionVisible'] = False
        if self._withRoles and vehType is not None:
            dataVO['rolesSectionVisible'] = True
        return dataVO

    def _packSpecial(self, entry, filterCtx, isSelected, tooltipRes, enabled):
        return {'value': getButtonsAssetPath(filterCtx.asset or entry),
         'tooltip': makeTooltip(backport.text(tooltipRes.header()) if tooltipRes else '', backport.text(tooltipRes.body(), **filterCtx.ctx)) if tooltipRes else '',
         'selected': isSelected,
         'enabled': enabled}

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
        self._withRoles = self._carousel.hasRoles()
        if isInitial:
            self.as_setInitDataS(self._getInitialVO(filters, xpRateMultiplier))
        else:
            self.as_setStateS(self._getUpdateVO(filters))
        self._carousel.applyFilter()
        self.as_showCounterS(text_styles.main(backport.text(R.strings.tank_carousel_filter.popover.counter(), count=self._carousel.formatCountVehicles())))

    @classmethod
    def _generateMapping(cls, hasRented, hasEvent, hasRoles, **kwargs):
        mapping = {FILTER_SECTION.NATIONS: GUI_NATIONS,
         FILTER_SECTION.VEHICLE_TYPES: VEHICLE_TYPES_ORDER,
         FILTER_SECTION.LEVELS: _VEHICLE_LEVEL_FILTERS,
         FILTER_SECTION.SPECIALS: [],
         FILTER_SECTION.HIDDEN: [],
         FILTER_SECTION.PROGRESSIONS: [],
         FILTER_SECTION.ROLES: VEHICLE_ROLES_LABELS_BY_CLASS if hasRoles else {},
         FILTER_SECTION.ROLES_WITH_EXTRA: VEHICLE_ROLES_LABELS + [constants.ROLES_COLLAPSE] if hasRoles else [],
         FILTER_SECTION.TEXT_SEARCH: [FILTER_KEYS.SEARCH_NAME_VEHICLE]}
        isBattleRoyaleEnabled = kwargs.get('hasBattleRoyleVehicles', False)
        if isBattleRoyaleEnabled:
            mapping[FILTER_SECTION.HIDDEN].append(FILTER_KEYS.BATTLE_ROYALE)
        elif hasEvent:
            mapping[FILTER_SECTION.HIDDEN].append(FILTER_KEYS.EVENT)
        if isBattleRoyaleEnabled and hasEvent:
            _logger.warning('It is not correct to show event and battleRoyale filters once')
        return mapping

    def __getSelectedVehType(self, filters):
        vehType = None
        if self._withRoles:
            for entry in self.__mapping[FILTER_SECTION.VEHICLE_TYPES]:
                if filters.get(entry, False):
                    if vehType is None:
                        vehType = entry
                    else:
                        vehType = None
                        break

        return vehType

    def __onCarouselSwitched(self):
        self.destroy()

    @staticmethod
    def __getRolesLabel(vehType):
        levels = toRomanRangeString(constants.ROLE_LEVELS)
        return text_styles.standard(_ms(TANK_CAROUSEL_FILTER.getRolesLabel(vehType), levels=levels)) if vehType is not None else ''

    @staticmethod
    def __getRoleVO(role, filters):
        return {'value': backport.image(R.images.gui.maps.icons.roleExp.roles.c_16x16.dyn(role)()),
         'tooltip': makeTooltip(backport.text(R.strings.menu.roleExp.roleName.dyn(role)(), groupName=backport.text(R.strings.menu.roleExp.roleGroupName.dyn(role)())), backport.text(R.strings.tank_carousel_filter.tooltip.role.body())),
         'selected': filters[role]}


class TankCarouselFilterPopover(VehiclesFilterPopover):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, ctx):
        super(TankCarouselFilterPopover, self).__init__(ctx)
        self._carouselRowCount = 0
        self._readRowCount(ctx)

    def switchCarouselType(self, selected):
        setting = self.__settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
        self._carouselRowCount = setting.CAROUSEL_TYPES.index(setting.OPTIONS.DOUBLE if selected else setting.OPTIONS.SINGLE)
        self._carousel.setRowCount(self._carouselRowCount + 1)

    def _getInitialVO(self, filters, xpRateMultiplier):
        dataVO = super(TankCarouselFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        dataVO.update({'toggleSwitchCarouselTooltip': makeTooltip('#tank_carousel_filter:tooltip/toggleSwitchCarousel/header', '#tank_carousel_filter:tooltip/toggleSwitchCarousel/body'),
         'toggleSwitchCarouselIcon': RES_ICONS.MAPS_ICONS_FILTERS_DOUBLE_CAROUSEL,
         'toggleSwitchCarouselSelected': bool(self._carouselRowCount)})
        return dataVO

    def _update(self, isInitial=False):
        super(TankCarouselFilterPopover, self)._update(isInitial)
        self._carousel.updateHotFilters()

    def _dispose(self):
        self._saveRowCount()
        super(TankCarouselFilterPopover, self)._dispose()

    def _readRowCount(self, _):
        setting = self.__settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
        self._carouselRowCount = setting.get()

    def _saveRowCount(self):
        self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, {settings_constants.GAME.CAROUSEL_TYPE: self._carouselRowCount})

    @classmethod
    def _generateMapping(cls, hasRented, hasEvent, hasRoles, **kwargs):
        mapping = super(TankCarouselFilterPopover, cls)._generateMapping(hasRented, hasEvent, hasRoles, **kwargs)
        mapping[FILTER_SECTION.SPECIALS].extend(cls._getBaseSpecialSection())
        if hasRented:
            mapping[FILTER_SECTION.SPECIALS].append(FILTER_KEYS.RENTED)
        if hasEvent:
            mapping[FILTER_SECTION.SPECIALS].append(FILTER_KEYS.EVENT)
        if constants.IS_KOREA:
            mapping[FILTER_SECTION.SPECIALS].append(FILTER_KEYS.IGR)
        clanWarsVehicles = cls.itemsCache.items.getItems(GUI_ITEM_TYPE.VEHICLE, REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.CLAN_WARS)
        if bool(clanWarsVehicles):
            mapping[FILTER_SECTION.SPECIALS].append(FILTER_KEYS.CLAN_RENTED)
        if kwargs.get('isRanked', False):
            mapping[FILTER_SECTION.SPECIALS].append(FILTER_KEYS.RANKED)
        if kwargs.get('isComp7', False):
            mapping[FILTER_SECTION.SPECIALS].append('comp7')
        if kwargs.get('debut_boxes', False):
            mapping[FILTER_SECTION.SPECIALS].append('debut_boxes')
        if kwargs.get('early_access', False):
            mapping[FILTER_SECTION.SPECIALS].append('early_access')
        return mapping

    @classmethod
    def _getBaseSpecialSection(cls):
        return [FILTER_KEYS.BONUS,
         FILTER_KEYS.FAVORITE,
         FILTER_KEYS.PREMIUM,
         FILTER_KEYS.ELITE,
         FILTER_KEYS.CRYSTALS]


class BattlePassCarouselFilterPopover(TankCarouselFilterPopover):
    __battlePassController = dependency.descriptor(IBattlePassController)

    @classmethod
    def _generateMapping(cls, hasRented, hasEvent, hasRoles, **kwargs):
        mapping = super(BattlePassCarouselFilterPopover, cls)._generateMapping(hasRented, hasEvent, hasRoles, **kwargs)
        if cls.__battlePassController.isVisible() and kwargs.get('isBattlePass', True):
            mapping[FILTER_SECTION.PROGRESSIONS].extend([BattlePassFilterConsts.FILTER_KEY_COMMON])
        return mapping

    def _getInitialVO(self, filters, xpRateMultiplier):
        isBattlePass = self._carousel.getCustomParams().get('isBattlePass', True)
        dataVO = super(BattlePassCarouselFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        dataVO['progressionsSectionVisible'] = self.__battlePassController.isVisible() and isBattlePass
        return dataVO


class BattleRoyaleCarouselFilterPopover(TankCarouselFilterPopover):

    @classmethod
    def _getBaseSpecialSection(cls):
        return [FILTER_KEYS.BONUS,
         FILTER_KEYS.FAVORITE,
         FILTER_KEYS.PREMIUM,
         FILTER_KEYS.ELITE]


class BattleTankCarouselFilterPopover(TankCarouselFilterPopover):

    def _getInitialVO(self, filters, xpRateMultiplier):
        dataVO = super(BattleTankCarouselFilterPopover, self)._getInitialVO(filters, xpRateMultiplier)
        dataVO['specialSectionVisible'] = True
        dataVO['searchSectionVisible'] = True
        dataVO['progressionsSectionVisible'] = False
        vehicleLevels = self._carousel.getCustomParams().get('vehicleLevelsFilter', list())
        if self._carousel is not None and not len(vehicleLevels) > 1:
            dataVO['tankTierSectionVisible'] = False
        return dataVO

    @classmethod
    def _getBaseSpecialSection(cls):
        return [FILTER_KEYS.FAVORITE, FILTER_KEYS.PREMIUM]

    def _generateMapping(self, hasRented, hasEvent, hasRoles, **kwargs):
        mapping = super(BattleTankCarouselFilterPopover, self)._generateMapping(hasRented, hasEvent, hasRoles, **kwargs)
        vehicleLevels = kwargs.get('vehicleLevelsFilter', list())
        if len(vehicleLevels) > 1:
            mapping[FILTER_SECTION.LEVELS] = [ 'level_{}'.format(lvl) for lvl in vehicleLevels ]
        else:
            mapping[FILTER_SECTION.LEVELS] = []
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

    def _generateMapping(self, hasRented, hasEvent, hasRoles, **kwargs):
        mapping = super(StorageBlueprintsFilterPopover, self)._generateMapping(hasRented, hasEvent, hasRoles, **kwargs)
        mapping[FILTER_SECTION.HIDDEN].append('unlock_available')
        return mapping
