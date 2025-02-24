# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/epicBattle/carousel_filter.py
from account_helpers.AccountSettings import EPICBATTLE_CAROUSEL_FILTER_1, EPICBATTLE_CAROUSEL_FILTER_2, EPICBATTLE_CAROUSEL_FILTER_CLIENT_1, EPICBATTLE_CAROUSEL_FILTER_CLIENT_2, BATTLEPASS_CAROUSEL_FILTER_1, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1
from account_helpers.AccountSettings import AccountSettings
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.carousel_filter import BattlePassCarouselFilter, BattlePassCriteriesGroup
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController
from gui.Scaleform.daapi.view.battle.epic.battle_carousel_filters import FLRentedCriteriesGroup

class EpicBattleCarouselFilter(BattlePassCarouselFilter):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    FILTER_KEY_SEASON = 'epicBattleSeason'

    def __init__(self):
        super(EpicBattleCarouselFilter, self).__init__()
        clientFilter = EPICBATTLE_CAROUSEL_FILTER_CLIENT_1 if self.__epicController.isUnlockVehiclesInBattleEnabled() else EPICBATTLE_CAROUSEL_FILTER_CLIENT_2
        self._serverSections = (EPICBATTLE_CAROUSEL_FILTER_1, EPICBATTLE_CAROUSEL_FILTER_2, BATTLEPASS_CAROUSEL_FILTER_1)
        self._clientSections = (clientFilter, BATTLEPASS_CAROUSEL_FILTER_CLIENT_1)

    def save(self):
        self._filters[self.FILTER_KEY_SEASON] = self.__epicController.getCurrentSeasonID()
        super(EpicBattleCarouselFilter, self).save()

    def load(self):
        super(EpicBattleCarouselFilter, self).load()
        currentSeason = self.__epicController.getCurrentSeasonID()
        lastSeason = self._filters.get(self.FILTER_KEY_SEASON, currentSeason)
        if lastSeason != currentSeason:
            self.reset(save=False)

    def isDefault(self, keys=None):
        defaultFilters = AccountSettings.getFilterDefaults(self._serverSections)
        for section in self._clientSections:
            defaultFilters.update(AccountSettings.getFilterDefault(section))

        if keys is None:
            keys = defaultFilters.keys()
        for key in keys:
            if key != self.FILTER_KEY_SEASON and self._filters[key] != defaultFilters[key]:
                return False

        return True

    def _setCriteriaGroups(self):
        self._criteriesGroups = (FLRentedCriteriesGroup(), BattlePassCriteriesGroup())
