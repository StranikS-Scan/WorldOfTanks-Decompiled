# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/widgets/carousel_view.py
import copy
import json
import BigWorld
from CurrentVehicle import g_currentVehicle
from account_helpers import AccountSettings
from gui import GUI_NATIONS
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.backport import createTooltipData, BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.shared.gui_items.Vehicle import getIconResourceName
from last_stand.gui import vehicleComparisonKey
from last_stand.gui.impl.lobby.ls_helpers import getQuestDescription, getVehicleState
from last_stand.gui.impl.lobby.tooltips.simple_format_tooltip import SimpleFormatTooltipView
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.gui.ls_gui_constants import LS_CAROUSEL_VEHICLE_TOOLTIP
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_view_model import HangarCarouselViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_filter_view_model import FilterKeys
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency
from last_stand_common import last_stand_constants
from last_stand_common.last_stand_constants import LS_VEHILCE_DAILY_QUEST
from skeletons.gui.shared import IItemsCache
DEFAULT_FILTER = {FilterKeys.ISFAVORITE.value: False,
 FilterKeys.ISPREMIUM.value: False,
 FilterKeys.ISRENT.value: False,
 FilterKeys.ISELITE.value: False,
 FilterKeys.VEHICLETYPE.value: [],
 FilterKeys.NATION.value: [],
 FilterKeys.SEARCHNAME.value: ''}

class CarouselView(ViewComponent[HangarCarouselViewModel]):
    _itemsCache = dependency.descriptor(IItemsCache)
    lsCtrl = dependency.descriptor(ILSController)
    _difficultyController = dependency.descriptor(IDifficultyLevelController)

    def __init__(self):
        super(CarouselView, self).__init__(R.aliases.last_stand.shared.Carousel(), HangarCarouselViewModel)
        self.__filter = {}
        self.__filteredTypes = []
        self.__filteredNations = []

    @property
    def viewModel(self):
        return super(CarouselView, self).getViewModel()

    @property
    def account(self):
        return getattr(BigWorld.player(), 'LSAccountComponent', None)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            specialArgs = []
            if tooltipId == LS_CAROUSEL_VEHICLE_TOOLTIP:
                intCD = event.getArgument('intCD', None)
                if intCD is not None:
                    specialArgs = [int(intCD)]
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
            window.load()
            return window
        else:
            return super(CarouselView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.last_stand.mono.lobby.tooltips.simple_format_tooltip():
            if event.getArgument('id', '') == 'dailyQuest' and g_currentVehicle.item:
                return SimpleFormatTooltipView(header=backport.text(R.strings.last_stand_lobby.carousel.daily.header()), body=getQuestDescription(LS_VEHILCE_DAILY_QUEST))
        return super(CarouselView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(CarouselView, self)._onLoading(*args, **kwargs)
        self.__fillModel()
        self.__loadFilters()
        self.__fillFilter()

    def _subscribe(self):
        super(CarouselView, self)._subscribe()
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.__onVehicleLockUpdated,
         'inventory.1': self.__fillVehicles,
         '{}.daily'.format(last_stand_constants.LS_INFO_PDATA_KEY): self.__updateDaily,
         '{}.curDay'.format(last_stand_constants.LS_INFO_PDATA_KEY): self.__curDayChanged})

    def _unsubscribe(self):
        super(CarouselView, self)._unsubscribe()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def _getEvents(self):
        return [(self.viewModel.onChangeVehicle, self.__onChangeVehicle),
         (self.viewModel.filter.onFiltered, self.__onFiltered),
         (self.viewModel.filter.onReset, self.__onReset),
         (self._difficultyController.onChangeDifficultyLevel, self.__onDifficultyChange),
         (g_currentVehicle.onChanged, self.__onCurrentVehicleChanged),
         (self.lsCtrl.onSettingsUpdate, self.__fillVehicles)]

    def _getVehicles(self):
        suitableVehicles = self.lsCtrl.getSuitableVehicles()
        vehicles = []
        vehicleDailyCompleted = self.account.vehicleDailyCompleted if self.account else None
        for value in sorted(suitableVehicles, key=vehicleComparisonKey):
            hasDaily = value.intCD not in vehicleDailyCompleted if vehicleDailyCompleted is not None else False
            vehicles.append({'name': value.descriptor.type.shortUserString,
             'intCD': value.intCD,
             'invID': value.invID,
             'nation': value.nationName,
             'icon': getIconResourceName(value.name),
             'type': value.type.replace('-', '_'),
             'isFavorite': value.isFavorite,
             'isPremium': value.isPremium,
             'isPremiumIGR': value.isPremiumIGR,
             'isElite': value.isElite,
             'isRent': value.isRented,
             'vehicleState': getVehicleState(value),
             'hasDaily': hasDaily})

        return json.dumps(vehicles)

    def __fillVehicles(self, *args, **kwargs):
        vehicles = self._getVehicles()
        self.viewModel.setVehicles(str(vehicles))

    def __fillModel(self):
        if g_currentVehicle.item:
            self.viewModel.setSelectedVehicle(g_currentVehicle.invID)
        self.__fillVehicles()
        self.viewModel.getOrderedNations().clear()
        for nation in GUI_NATIONS:
            self.viewModel.getOrderedNations().addString(nation)

    def __onReset(self):
        self.__filteredTypes = []
        self.__filteredNations = []
        self.__filter = copy.deepcopy(DEFAULT_FILTER)
        self.__fillFilter()
        self.__saveFilter()

    def __onDifficultyChange(self, _):
        self.__fillModel()

    def __onChangeVehicle(self, args):
        if args is not None:
            self.lsCtrl.selectVehicle(int(args.get('invID')))
        return

    def __onFiltered(self, args):
        key = args.get('key', None)
        value = args.get('value', None)
        if key is None or value is None:
            return
        else:
            if key == FilterKeys.ISFAVORITE.value:
                self.viewModel.filter.setIsFavorite(value)
                self.__filter[FilterKeys.ISFAVORITE.value] = value
            if key == FilterKeys.ISPREMIUM.value:
                self.viewModel.filter.setIsPremium(value)
                self.__filter[FilterKeys.ISPREMIUM.value] = value
            if key == FilterKeys.ISRENT.value:
                self.viewModel.filter.setIsRent(value)
                self.__filter[FilterKeys.ISRENT.value] = value
            if key == FilterKeys.ISELITE.value:
                self.viewModel.filter.setIsElite(value)
                self.__filter[FilterKeys.ISELITE.value] = value
            if key == FilterKeys.VEHICLETYPE.value:
                self.__addOrRemove(self.__filteredTypes, value)
                self.viewModel.filter.setTypes(json.dumps(self.__filteredTypes))
                self.__filter[FilterKeys.VEHICLETYPE.value] = self.__filteredTypes
            if key == FilterKeys.NATION.value:
                self.__addOrRemove(self.__filteredNations, value)
                self.viewModel.filter.setNations(json.dumps(self.__filteredNations))
                self.__filter[FilterKeys.NATION.value] = self.__filteredNations
            if key == FilterKeys.SEARCHNAME.value:
                self.viewModel.filter.setName(value)
                self.__filter[FilterKeys.SEARCHNAME.value] = value
            self.__saveFilter()
            return

    def __loadFilters(self):
        settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
        self.__filter = settings.get(AccountSettingsKeys.CAROUSEL_FILTER_DEF, None)
        if self.__filter is None or self.__filter == {}:
            self.__filter = copy.deepcopy(DEFAULT_FILTER)
        self.__filteredTypes = self.__filter.get(FilterKeys.VEHICLETYPE.value)
        self.__filteredNations = self.__filter.get(FilterKeys.NATION.value)
        return

    def __fillFilter(self):
        if self.__filter is None or self.__filter == {}:
            self.__filter = copy.deepcopy(DEFAULT_FILTER)
        with self.viewModel.transaction() as tx:
            tx.filter.setIsPremium(self.__filter.get(FilterKeys.ISPREMIUM.value))
            tx.filter.setIsFavorite(self.__filter.get(FilterKeys.ISFAVORITE.value))
            tx.filter.setName(self.__filter.get(FilterKeys.SEARCHNAME.value, ''))
            tx.filter.setNations(json.dumps(self.__filter.get(FilterKeys.NATION.value)))
            tx.filter.setTypes(json.dumps(self.__filter.get(FilterKeys.VEHICLETYPE.value)))
            tx.filter.setIsRent(self.__filter.get(FilterKeys.ISRENT.value))
            tx.filter.setIsElite(self.__filter.get(FilterKeys.ISELITE.value))
        return

    def __saveFilter(self):
        settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
        settings[AccountSettingsKeys.CAROUSEL_FILTER_DEF] = self.__filter
        AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)

    def __addOrRemove(self, arr, value):
        if value in arr:
            arr.remove(value)
        else:
            arr.append(value)

    def __onCurrentVehicleChanged(self):
        if g_currentVehicle.item is None:
            return
        else:
            self.viewModel.setSelectedVehicle(g_currentVehicle.invID)
            return

    def __onVehicleLockUpdated(self, *args):
        self.__fillVehicles()

    def __updateDaily(self, diff):
        if diff is None:
            return
        elif not self.account:
            return
        else:
            vehicleDailyCompleted = diff.get(self.account.curDay)
            if not vehicleDailyCompleted:
                return
            with self.viewModel.transaction() as tx:
                data = {'intCDs': list(vehicleDailyCompleted),
                 'extend': True}
                tx.setVehicleDailyCompleted(json.dumps(data))
            return

    def __curDayChanged(self, diff):
        if diff is None:
            return
        elif not self.account:
            return
        else:
            with self.viewModel.transaction() as tx:
                data = {'intCDs': list(self.account.vehicleDailyCompleted),
                 'extend': False}
                tx.setVehicleDailyCompleted(json.dumps(data))
            return
