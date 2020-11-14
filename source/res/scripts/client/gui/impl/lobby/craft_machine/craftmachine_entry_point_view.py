# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/craft_machine/craftmachine_entry_point_view.py
import json
import logging
import time
from datetime import datetime
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl import backport
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
        self.__startDateUI = ''
        self.__endDateUI = ''
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
                additionalUrl = entryData.get('craftMachineAdditionalUrl')
                if additionalUrl is not None:
                    self.__additionalUrl = str(additionalUrl)
                self.__startDateUI = entryData.get('startDateUI')
                self.__endDateUI = entryData.get('endDateUI')

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
            tx.setTitle(backport.text(R.strings.event.craftMachine.title()))
            tx.setSubTitle(backport.text(R.strings.event.craftMachine.subTitle()))
            tx.setStartDate(0)
            tx.setEndDate(0)
            if self.__startDateUI:
                startDateUI = time.mktime(datetime.strptime(self.__startDateUI, _TIME_FORMAT).timetuple())
                tx.setStartDate(startDateUI)
            if self.__endDateUI:
                endDateUI = time.mktime(datetime.strptime(self.__endDateUI, _TIME_FORMAT).timetuple())
                tx.setEndDate(endDateUI)
            tx.setIconSmall(R.images.gui.maps.icons.event.craftMachine.entryPoint.logo_small())
            tx.setIconBig(R.images.gui.maps.icons.event.craftMachine.entryPoint.logo_big())
            tx.setBgSmallThin(R.images.gui.maps.icons.event.craftMachine.entryPoint.bg_small_thin())
            tx.setBgBigThin(R.images.gui.maps.icons.event.craftMachine.entryPoint.bg_big_thin())
            tx.setBgSmallWide(R.images.gui.maps.icons.event.craftMachine.entryPoint.bg_small_wide())
            tx.setBgBigWide(R.images.gui.maps.icons.event.craftMachine.entryPoint.bg_big_wide())

    def __onClick(self):
        self.__openCraftMachine()
