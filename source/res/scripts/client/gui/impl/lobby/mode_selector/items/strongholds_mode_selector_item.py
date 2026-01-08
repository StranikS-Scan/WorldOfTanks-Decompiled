# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/strongholds_mode_selector_item.py
import typing
from gui.clans.clan_cache import g_clanCache
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_stronghold_model import ModeSelectorStrongholdModel
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.stronghold.stronghold_helpers import CLAN_SEASON_PROGRESS_PREFIX, getClanSeasonProgressLevel
from PlayerEvents import g_playerEvents
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_stronghold_widget_model import ModeSelectorStrongholdWidgetModel

class StrongholdsModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorStrongholdModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.STRONGHOLD

    @property
    def viewModel(self):
        return super(StrongholdsModeSelectorItem, self).viewModel

    def _onInitializing(self):
        super(StrongholdsModeSelectorItem, self)._onInitializing()
        g_clientUpdateManager.addCallbacks({'stats.clanInfo': self.__clanInfoUpdateHandler})
        setBattlePassState(self.viewModel)
        g_playerEvents.onClientUpdated += self.__onTokensUpdate
        self.__resolveClanText()

    def _onDisposing(self):
        super(StrongholdsModeSelectorItem, self)._onDisposing()
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_playerEvents.onClientUpdated -= self.__onTokensUpdate

    def __clanInfoUpdateHandler(self, *args):
        self.__resolveClanText()

    def __resolveClanText(self):
        if g_clanCache.isInClan:
            dynAcc = R.strings.mode_selector.mode.strongholdsBattlesList.call.c_2()
        else:
            dynAcc = R.strings.mode_selector.mode.strongholdsBattlesList.call.c_1()
        self.viewModel.setStatusActive(backport.text(dynAcc))
        with self.viewModel.widget.transaction() as vm:
            vm.setCurrentStage(getClanSeasonProgressLevel())
            vm.setIsInClan(g_clanCache.isInClan)
            vm.setIsActive(g_clanCache.strongholdEventProvider.isRunning())

    def __onTokensUpdate(self, diff, _):
        tokens = diff.get('tokens', {})
        if not tokens:
            return
        if any((tokenID.startswith(CLAN_SEASON_PROGRESS_PREFIX) for tokenID, token in tokens.iteritems())):
            self.viewModel.widget.setCurrentStage(getClanSeasonProgressLevel())
