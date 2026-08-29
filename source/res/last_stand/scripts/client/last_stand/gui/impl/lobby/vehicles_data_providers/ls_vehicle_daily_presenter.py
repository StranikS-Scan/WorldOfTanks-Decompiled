# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/vehicles_data_providers/ls_vehicle_daily_presenter.py
from __future__ import absolute_import
import typing
from CurrentVehicle import g_currentVehicle
from gui.impl.gen import R
from helpers import dependency
from gui.impl import backport
import BigWorld
from gui.shared.gui_items.Vehicle import Vehicle
from gui.impl.lobby.hangar.base.hangar_interfaces import IVehicleFilter
from gui.impl.pub.view_component import ViewComponent
from gui.server_events.event_items import ServerEventAbstract
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.vehicle_daily_model import VehicleDailyModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.vehicles_daily_model import VehiclesDailyModel
from last_stand.gui.impl.lobby.ls_helpers import getQuestDescription
from last_stand.gui.impl.lobby.tooltips.simple_format_tooltip import SimpleFormatTooltipView
from last_stand_common import last_stand_constants
from last_stand_common.last_stand_constants import LS_VEHILCE_DAILY_QUEST
from last_stand.skeletons.ls_quests_ui_cache import ILSQuestsUICache
from skeletons.gui.shared import IItemsCache
from future.utils import viewvalues, viewitems

class LSVehiclesDailyPresenter(ViewComponent[VehiclesDailyModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    questsCache = dependency.descriptor(ILSQuestsUICache)

    def __init__(self, vehiclesComponent):
        super(LSVehiclesDailyPresenter, self).__init__(model=VehiclesDailyModel)
        self._vehiclesComponent = vehiclesComponent
        self.__quest = None
        self.__vehicleDailyCompleted = set()
        return

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.last_stand.mono.lobby.tooltips.simple_format_tooltip():
            if event.getArgument('id', '') == 'dailyQuest' and g_currentVehicle.item:
                return SimpleFormatTooltipView(header=backport.text(R.strings.last_stand_tooltips.vehicleDaily.header()), body=getQuestDescription(LS_VEHILCE_DAILY_QUEST))
        return super(LSVehiclesDailyPresenter, self).createToolTipContent(event, contentID)

    def _getEvents(self):
        return ((self._vehiclesComponent.onDiff, self.__onUpdateVehiclesProgress), (self.questsCache.onSyncCompleted, self.__onSyncQuestCompleted))

    def _onLoading(self, *args, **kwargs):
        super(LSVehiclesDailyPresenter, self)._onLoading(*args, **kwargs)
        self.__quest = self.__getDailyQuest()
        self.__updateCompletedVehicles()
        self.__fillVehicles()

    @property
    def viewModel(self):
        return super(LSVehiclesDailyPresenter, self).getViewModel()

    @property
    def account(self):
        return getattr(BigWorld.player(), 'LSAccountComponent', None)

    def __getDailyModel(self, vehCD):
        dailyModel = VehicleDailyModel()
        dailyModel.setId(str(vehCD))
        dailyModel.setIsActive(vehCD not in self.__vehicleDailyCompleted)
        return dailyModel

    def __fillVehicles(self):
        vehicles = self._vehiclesComponent.vehicles
        with self.viewModel.transaction() as model:
            dailyVehicles = model.getDailyVehicles()
            dailyVehicles.clear()
            for vehicle in viewvalues(vehicles):
                dailyModel = self.__getDailyModel(vehicle.intCD)
                dailyVehicles.set(dailyModel.getId(), dailyModel)

    def __onSyncQuestCompleted(self):
        if self.__quest is None:
            self.__quest = self.__getDailyQuest()
        vehiclesBeforeSync = self.__vehicleDailyCompleted
        self.__updateCompletedVehicles()
        diff = self.__vehicleDailyCompleted ^ vehiclesBeforeSync
        if diff:
            self.__onUpdateVehiclesProgress(diff)
        return

    def __updateCompletedVehicles(self):
        if self.__quest is None:
            return
        else:
            progress = self.__quest.getProgressData()
            bonusLimit = self.__quest.bonusCond.getBonusLimit()
            vehicleDailyCompleted = set()
            for vehCD, bonusCountData in viewitems(progress):
                if bonusCountData.get('bonusCount') >= bonusLimit:
                    vehicleDailyCompleted.add(vehCD)

            self.__vehicleDailyCompleted = vehicleDailyCompleted
            return

    def __getDailyQuest(self):
        q = self.questsCache.getQuests().get(last_stand_constants.LS_VEHILCE_DAILY_QUEST)
        return q if q and not q.isOutOfDate() and q.isStarted() and ServerEventAbstract.isAvailable(q).isValid else None

    def __onUpdateVehiclesProgress(self, diff):
        with self.viewModel.transaction() as model:
            vehicleDaily = model.getDailyVehicles()
            for intCD in diff:
                if intCD in self._vehiclesComponent.vehicles:
                    vehicle = self._vehiclesComponent.vehicles[intCD]
                    dailyModel = self.__getDailyModel(vehicle.intCD)
                    vehicleDaily.set(dailyModel.getId(), dailyModel)
                vehicleDaily.remove(str(intCD))
