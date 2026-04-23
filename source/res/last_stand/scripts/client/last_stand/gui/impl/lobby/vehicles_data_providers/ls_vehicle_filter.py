# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/vehicles_data_providers/ls_vehicle_filter.py
from __future__ import absolute_import
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CAROUSEL_FILTER_1, CAROUSEL_FILTER_2, CAROUSEL_FILTER_CLIENT_1
from gui.filters.carousel_filter import CarouselFilter
from helpers import dependency
from last_stand.gui.ls_account_settings import AccountSettingsKeys
from last_stand.skeletons.ls_controller import ILSController

class LSBattleCarouselFilter(CarouselFilter):
    __lsController = dependency.descriptor(ILSController)

    def __init__(self):
        super(LSBattleCarouselFilter, self).__init__()
        self._serverSections = ()
        self._clientSections = (CAROUSEL_FILTER_1, CAROUSEL_FILTER_2, CAROUSEL_FILTER_CLIENT_1)

    def save(self):
        settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
        settings[AccountSettingsKeys.CAROUSEL_FILTER_DEF] = self._filters
        AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)

    def load(self):
        settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
        defaultFilters = settings.get(AccountSettingsKeys.CAROUSEL_FILTER_DEF, {})
        if defaultFilters == {}:
            for section in self._clientSections:
                defaultFilters.update(AccountSettings.getFilterDefault(section))

        self._filters = defaultFilters
