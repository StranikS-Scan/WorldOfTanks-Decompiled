# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/craft_machine/craftmachine_entry_point_view.py
import json
import logging
import time
from datetime import datetime
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl.gen.view_models.views.lobby.craft_machine.craftmachine_entry_point_view_model import CraftmachineEntryPointViewModel
from gui.Scaleform.daapi.view.lobby.clans.clan_helpers import getCraftMachineURL
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showStrongholds
from helpers import dependency
from skeletons.gui.game_control import IEventsNotificationsController
from gui.impl.gen import R
_logger = logging.getLogger(__name__)
_HANGAR_ENTRY_POINTS = 'hangarEntryPoints'
_TIME_FORMAT = '%d.%m.%Y'

class CraftmachineEntryPointView(ViewImpl):
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __slots__ = ('__additionalUrl', '__startDateUI', '__endDateUI')

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.craft_machine.CraftmachineEntryPointView())
        settings.flags = flags
        settings.model = CraftmachineEntryPointViewModel()
        self.__additionalUrl = ''
        self.__endDateUI = ''
        self.__startDateUI = ''
        super(CraftmachineEntryPointView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CraftmachineEntryPointView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        self.__notificationsCtrl.onEventNotificationsChanged += self.__onEventNotification
        self.__handleNotifications(self.__notificationsCtrl.getEventsNotifications())
        self.viewModel.onActionClick += self.__onClick

    def _onLoading(self, *args, **kwargs):
        super(CraftmachineEntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def _finalize(self):
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__onEventNotification
        self.viewModel.onActionClick -= self.__onClick

    def __parseAdditionalData(self, item):
        if item is None:
            return
        else:
            notificationEntries = json.loads(item.data)
            for entryData in notificationEntries:
                if str(entryData.get('id')) == HANGAR_ALIASES.CRAFT_MACHINE_ENTRY_POINT:
                    additionalUrl = entryData.get('craftMachineAdditionalUrl')
                    if additionalUrl is not None:
                        self.__additionalUrl = str(additionalUrl)
                    self.__startDateUI = entryData.get('startDateUI', '')
                    self.__endDateUI = entryData.get('endDateUI', '')

            return

    def __handleNotifications(self, notifications):
        for item in notifications:
            if item.eventType == _HANGAR_ENTRY_POINTS:
                self.__parseAdditionalData(item)

        self.__updateViewModel()

    def __onEventNotification(self, added, _):
        for item in added:
            if item.eventType == _HANGAR_ENTRY_POINTS:
                self.__parseAdditionalData(item)

        self.__updateViewModel()

    def __openCraftMachine(self):
        url = getCraftMachineURL()
        if url is None:
            _logger.error('Could not find craft machine URL, check clan_config')
            return
        else:
            showStrongholds(url + self.__additionalUrl)
            return

    def __updateViewModel(self):
        with self.viewModel.transaction() as tx:
            tx.setStartDate(0)
            if self.__startDateUI:
                startDateUI = time.mktime(datetime.strptime(self.__startDateUI, _TIME_FORMAT).timetuple())
                tx.setStartDate(startDateUI)
            tx.setEndDate(0)
            if self.__endDateUI:
                endDateUI = time.mktime(datetime.strptime(self.__endDateUI, _TIME_FORMAT).timetuple())
                tx.setEndDate(endDateUI)

    def __onClick(self):
        self.__openCraftMachine()
