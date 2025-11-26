# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_filters_presenter.py
from __future__ import absolute_import
import json
import typing
import BigWorld
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.options import CarouselTypeSetting
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from gui import GUI_NATIONS
from gui.filters.carousel_filter import FILTER_KEYS
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass import BattlePassFilterConsts
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_filter_model import VehicleFilterModel, FilterSection, RoleSection
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.settings import VEHICLE_LEVELS
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER, VEHICLE_ROLES_LABELS_BY_CLASS, VEHICLE_CLASS_NAME
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from typing import List, Dict
    from gui.filters.carousel_filter import CarouselFilter
_VEHICLE_LEVEL_FILTERS = [ 'level_{}'.format(level) for level in VEHICLE_LEVELS ]
_CAROUSEL_ROW_COUNT_TYPE = {1: CarouselTypeSetting.CAROUSEL_TYPES.index(CarouselTypeSetting.OPTIONS.SINGLE),
 2: CarouselTypeSetting.CAROUSEL_TYPES.index(CarouselTypeSetting.OPTIONS.DOUBLE)}

class VehicleFiltersDataProvider(ViewComponent[VehicleFilterModel]):
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, carouselFilter):
        self.__filter = carouselFilter
        self.__rowCount = None
        super(VehicleFiltersDataProvider, self).__init__(model=VehicleFilterModel)
        return

    @property
    def viewModel(self):
        return super(VehicleFiltersDataProvider, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(VehicleFiltersDataProvider, self)._onLoading(*args, **kwargs)
        self._generateMappings()
        self.__filter.load()
        self.__updateCarousel()
        self.viewModel.setDefaultFilters(json.dumps(self.__convertToModel(self.__filter.filterDefaults)))
        self.__updateModel()

    def _getEvents(self):
        return ((self.viewModel.onSaveFilter, self.__onSaveFilter),
         (self.viewModel.onCarouselTypeChange, self.__onCarouselTypeChanged),
         (self.__settingsCore.onSettingsChanged, self.__onCarouselSettingsChange),
         (self.viewModel.onResetFilter, self.__onResetFilter))

    @classmethod
    def _getBaseSpecialSection(cls):
        return [FILTER_KEYS.BONUS,
         FILTER_KEYS.FAVORITE,
         FILTER_KEYS.PREMIUM,
         FILTER_KEYS.ELITE,
         FILTER_KEYS.CRYSTALS,
         FILTER_KEYS.OWN_3D_STYLE,
         FILTER_KEYS.CAN_INSTALL_ATTACHMENTS,
         FILTER_KEYS.RENTED]

    def _generateMappings(self):
        self.__mapping = {FilterSection.NATIONS.value: GUI_NATIONS,
         FilterSection.VEHICLETYPES.value: VEHICLE_TYPES_ORDER,
         FilterSection.LEVELS.value: _VEHICLE_LEVEL_FILTERS,
         FilterSection.SPECIALS.value: self._getBaseSpecialSection(),
         FilterSection.TEXTSEARCH.value: [FILTER_KEYS.SEARCH_NAME_VEHICLE],
         FilterSection.BATTLEPASS.value: BattlePassFilterConsts.FILTERS_KEYS,
         RoleSection.LIGHTTANK.value: VEHICLE_ROLES_LABELS_BY_CLASS[VEHICLE_CLASS_NAME.LIGHT_TANK],
         RoleSection.MEDIUMTANK.value: VEHICLE_ROLES_LABELS_BY_CLASS[VEHICLE_CLASS_NAME.MEDIUM_TANK],
         RoleSection.HEAVYTANK.value: VEHICLE_ROLES_LABELS_BY_CLASS[VEHICLE_CLASS_NAME.HEAVY_TANK],
         RoleSection.ATSPG.value: VEHICLE_ROLES_LABELS_BY_CLASS[VEHICLE_CLASS_NAME.AT_SPG]}

    def __onResetFilter(self):
        self.__filter.reset()
        self.__updateModel()

    def __convertSection(self, sectionKey, filters):
        result = []
        for key in self.__mapping[sectionKey]:
            if sectionKey == FilterSection.TEXTSEARCH.value and filters.get('searchNameVehicle'):
                result.append(filters.get('searchNameVehicle'))
            if filters.get(key):
                result.append(key)

        return {sectionKey: result}

    def __convertToModel(self, filters):
        result = {}
        for key in self.__mapping:
            section = self.__convertSection(key, filters)
            for value in section.values():
                if value:
                    result.update(section)

        return result

    def __updateModel(self):
        filters = self.__filter.getFilters()
        with self.viewModel.transaction() as model:
            model.setFilters(json.dumps(self.__convertToModel(filters)))
            model.getNationsOrder().clear()
            for nation in GUI_NATIONS:
                model.getNationsOrder().addString(nation)

    def __onSaveFilter(self, args):
        data = json.loads(args.get('filters'))
        self.__filter.clear(save=False)
        for sectionKey, valueList in data.items():
            for value in valueList:
                if sectionKey == FilterSection.TEXTSEARCH.value:
                    self.__filter.update({FILTER_KEYS.SEARCH_NAME_VEHICLE: value}, save=False)
                index = self.__mapping[sectionKey].index(value)
                key = self.__mapping[sectionKey][index]
                self.__filter.update({key: True}, False)

        self.__filter.save()
        self.__updateModel()

    def __onCarouselSettingsChange(self, diff):
        if settings_constants.GAME.CAROUSEL_TYPE in diff and BigWorld.player() is not None:
            self.__rowCount = None
            self.__updateCarousel()
        return

    def __onCarouselTypeChanged(self, args):
        self.__rowCount = int(args.get('rowCount'))
        self.__settingsCore.serverSettings.setSectionSettings(SETTINGS_SECTIONS.GAME_EXTENDED, {settings_constants.GAME.CAROUSEL_TYPE: _CAROUSEL_ROW_COUNT_TYPE[self.__rowCount]})
        self.__updateCarousel()

    def __updateCarousel(self):
        setting = self.__settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
        self.viewModel.setCarouselRowCount(self.__rowCount or setting.getRowCount())
