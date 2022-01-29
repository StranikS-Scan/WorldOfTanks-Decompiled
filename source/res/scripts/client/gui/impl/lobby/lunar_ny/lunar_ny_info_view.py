# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_ny_info_view.py
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.info.info_model import InfoModel, Link
from gui.impl.lobby.lunar_ny.lunar_ny_base_main_view_component import BaseLunarNYViewComponent
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.events import OpenLinkEvent
from helpers import dependency
from items import lunar_ny
from items.components.lunar_ny_constants import CharmType
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_sounds import LUNAR_NY_INFO_SOUND_SPACE

class LunarNYInfoView(BaseLunarNYViewComponent[InfoModel]):
    __lunarNYController = dependency.descriptor(ILunarNYController)
    _SOUND_SPACE_SETTINGS = LUNAR_NY_INFO_SOUND_SPACE

    def onLoading(self, initCtx, isActive):
        super(LunarNYInfoView, self).onLoading(initCtx, isActive)
        startUTCTime, endUTCTime = self.__lunarNYController.getEventActiveTime()
        with self._viewModel.transaction() as model:
            model.setEventStartTime(startUTCTime)
            model.setEventEndTime(endUTCTime)
            model.setSecretSantaSentLimitTime(self.__lunarNYController.giftSystem.getSecretSantaSentPeriodLimit())
            model.setRareCharmsProbability(int(self.__lunarNYController.getMinRareCharmProbability()))
            self.__setCharmBonuses(model)

    def _addListeners(self):
        self._viewModel.onLinkClick += self.__onLinkClick

    def _removeListeners(self):
        self._viewModel.onLinkClick -= self.__onLinkClick

    def __onLinkClick(self, args):
        link = args.get('link', None)
        if link == Link.LUNARRULES:
            g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, self.__lunarNYController.getEventRulesURL()))
        elif link == Link.ENVELOPESSHOP:
            g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.SPECIFIED, self.__lunarNYController.getEnvelopesExternalShopURL()))
        elif link == Link.INFOVIDEO:
            showBrowserOverlayView(self.__lunarNYController.getInfoVideoURL())
        return

    def __setCharmBonuses(self, model):
        commonBonus = 0
        rareBonus = 0
        doubleRareBonus = 0
        for charm in lunar_ny.g_cache.charms.values():
            if charm.type == CharmType.COMMON:
                commonBonus = charm.bonuses.values()[0] if charm.bonuses else 0
            if charm.type == CharmType.RARE:
                if len(charm.bonuses) == 1:
                    doubleRareBonus = charm.bonuses.values()[0]
                elif len(charm.bonuses) == 2:
                    rareBonus = charm.bonuses.values()[0]

        model.setSimpleCharmBonus(commonBonus * 100)
        model.setSpecialCharmSingleBonus(rareBonus * 100)
        model.setSpecialCharmDoubleBonus(doubleRareBonus * 100)
