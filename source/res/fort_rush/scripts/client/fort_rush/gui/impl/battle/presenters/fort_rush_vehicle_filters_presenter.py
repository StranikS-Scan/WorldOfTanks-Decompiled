# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/battle/presenters/fort_rush_vehicle_filters_presenter.py
from __future__ import absolute_import
import copy
import logging
import typing
from account_helpers.AccountSettings import FORT_RUSH_CAROUSEL_FILTER_1, AccountSettings
from fort_rush.gui.fort_rush_gui_constants import BATTLE_CTRL_ID
from gui.filters.carousel_filter import FILTER_KEYS, SessionCarouselFilter
from gui.impl.lobby.hangar.presenters.vehicle_filters_presenter import VehicleFiltersDataProvider
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Any, Dict, List, Optional
_logger = logging.getLogger(__name__)

class FortRushBattleCarouselFilter(SessionCarouselFilter):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FortRushBattleCarouselFilter, self).__init__()
        self._clientSections = (FORT_RUSH_CAROUSEL_FILTER_1,)

    def load(self):
        defaults = AccountSettings.getSessionSettingsDefault(FORT_RUSH_CAROUSEL_FILTER_1)
        self._filters = copy.deepcopy(defaults)
        retained = self.__getRetainedFilters()
        if retained is None:
            self.update(copy.deepcopy(defaults), save=False)
            return
        else:
            savedFilters = copy.deepcopy(defaults)
            savedFilters.update({key:value for key, value in retained.items() if key in defaults})
            self.update(savedFilters, save=False)
            return

    def save(self):
        respawnCtrl = self.__respawnCtrl
        if respawnCtrl is None:
            _logger.warning('[FORT_RUSH] battle filter save: respawn controller unavailable, state not retained')
            return
        else:
            respawnCtrl.setRespawnVehicleFilters(self._filters)
            return

    @property
    def __respawnCtrl(self):
        dynamic = self._sessionProvider.dynamic
        return None if dynamic is None else dynamic.getControllerByID(BATTLE_CTRL_ID.FORT_RUSH_GUI_CTRL)

    def __getRetainedFilters(self):
        respawnCtrl = self.__respawnCtrl
        return None if respawnCtrl is None else respawnCtrl.getRespawnVehicleFilters()


class FortRushVehicleFiltersPresenter(VehicleFiltersDataProvider):

    def __init__(self):
        super(FortRushVehicleFiltersPresenter, self).__init__(FortRushBattleCarouselFilter())

    @classmethod
    def _getBaseSpecialSection(cls):
        return [FILTER_KEYS.FAVORITE, FILTER_KEYS.RENTED, FILTER_KEYS.EVENT]
