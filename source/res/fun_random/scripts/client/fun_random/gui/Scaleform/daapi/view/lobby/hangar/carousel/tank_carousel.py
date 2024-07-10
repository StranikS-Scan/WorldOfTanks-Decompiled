# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/hangar/carousel/tank_carousel.py
from constants import ARENA_BONUS_TYPE
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.Scaleform.daapi.view.common.filter_popover import fillFunRandomFilterVO
from fun_random.gui.Scaleform.daapi.view.lobby.hangar.carousel.carousel_data_provider import FunRandomCarouselDataProvider
from fun_random.gui.Scaleform.daapi.view.lobby.hangar.carousel.carousel_filter import FunRandomCarouselFilter
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.Scaleform.daapi.view.lobby.hangar.carousels import BattlePassTankCarousel

class FunRandomTankCarousel(BattlePassTankCarousel, FunSubModesWatcher):

    def __init__(self):
        super(FunRandomTankCarousel, self).__init__()
        self._carouselDPCls = FunRandomCarouselDataProvider
        self._carouselFilterCls = FunRandomCarouselFilter

    def getCustomParams(self):
        return {'isBattlePass': self._battlePassController.isGameModeEnabled(ARENA_BONUS_TYPE.FUN_RANDOM)}

    @classmethod
    def _makeFilterVO(cls, filterID, contexts, filters):
        return super(FunRandomTankCarousel, cls)._makeFilterVO(filterID, contexts, filters) if filterID != 'funRandom' else fillFunRandomFilterVO({'id': filterID}, filters[filterID], True)

    def _populate(self):
        super(FunRandomTankCarousel, self)._populate()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded
        self.startSubSelectionListening(self.__onSubModeSelected)
        self.startSubSettingsListening(self.__onSubModeUpdated, desiredOnly=True)

    def _dispose(self):
        self.stopSubSettingsListening(self.__onSubModeUpdated, desiredOnly=True)
        self.stopSubSelectionListening(self.__onSubModeSelected)
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        super(FunRandomTankCarousel, self)._dispose()

    def _getFilters(self):
        return super(FunRandomTankCarousel, self)._getFilters() + ('funRandom',)

    def _getFiltersPopoverAlias(self):
        return FUNRANDOM_ALIASES.FUN_RANDOM_CAROUSEL_FILTER_POPOVER

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.alias == FUNRANDOM_ALIASES.FUN_RANDOM_CAROUSEL_FILTER_POPOVER:
            view.setTankCarousel(self)

    def __onSubModeSelected(self, *_):
        self._carouselDP.onSubModeSelected()
        self._updateDynamicFilters()

    def __onSubModeUpdated(self, *_):
        self._updateDynamicFilters()
