# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/year_leaderboard_view.py
from constants import CURRENT_REALM
from dossiers2.ui.achievements import BADGES_BLOCK
from frameworks.wulf import WindowFlags, ViewSettings
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.ranked.year_leaderboard_view_model import YearLeaderboardViewModel
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.utils import getPlayerName
from gui.Scaleform.genConsts.RANKEDBATTLES_CONSTS import RANKEDBATTLES_CONSTS
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext

def _extractReward(rewardsData):
    for block in rewardsData.get('dossier', {}).itervalues():
        for record in block.iterkeys():
            block, name = record
            if block == BADGES_BLOCK:
                return name

    return None


class YearLeaderboardView(ViewImpl):
    __slots__ = ()
    __rankedController = dependency.descriptor(IRankedBattlesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, contentResID, *args):
        settings = ViewSettings(contentResID)
        settings.model = YearLeaderboardViewModel()
        settings.args = args
        super(YearLeaderboardView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(YearLeaderboardView, self).getViewModel()

    def _initialize(self, _, __, *args, **kwargs):
        super(YearLeaderboardView, self)._initialize(*args, **kwargs)
        self.viewModel.onLeaderboardBtnClick += self.__onLeaderboardBtnClick
        self.__rankedController.getSoundManager().setOverlayStateOn()

    def _finalize(self):
        self.__rankedController.getSoundManager().setOverlayStateOff()
        self.viewModel.onLeaderboardBtnClick -= self.__onLeaderboardBtnClick
        super(YearLeaderboardView, self)._finalize()

    def _onLoading(self, playerPosition, rewardsData, *args, **kwargs):
        super(YearLeaderboardView, self)._onLoading(*args, **kwargs)
        defaultBG = R.images.gui.maps.icons.rankedBattles.yearLeaderboardReward.bg_default
        overrideBG = R.images.gui.maps.icons.rankedBattles.yearLeaderboardReward.dyn('bg_' + CURRENT_REALM, defaultBG)
        with self.viewModel.transaction() as model:
            model.setPlayerName(getPlayerName())
            model.setPlayerClan(self.__getClanAbbrev())
            model.setPositionsTotal(self.__rankedController.getYearLBSize())
            model.setPosition(playerPosition)
            model.setRewardId(_extractReward(rewardsData))
            model.setBgImage(overrideBG())

    def __getClanAbbrev(self):
        clanAbbrev = self.__lobbyContext.getClanAbbrev(self.__itemsCache.items.stats.clanInfo)
        return backport.text(R.strings.ranked_battles.yearLeaderboard.rewardView.clanDescr(), clan=clanAbbrev) if clanAbbrev is not None else ''

    def __onLeaderboardBtnClick(self):
        self.__rankedController.showRankedBattlePage(ctx={'selectedItemID': RANKEDBATTLES_CONSTS.RANKED_BATTLES_YEAR_RATING_ID})
        self.destroyWindow()


class YearLeaderboardAwardWindow(LobbyNotificationWindow):
    __slots__ = ('__args',)

    def __init__(self, *args):
        super(YearLeaderboardAwardWindow, self).__init__(content=YearLeaderboardView(R.views.lobby.ranked.YearLeaderboardView(), *args), wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN)
        self.__args = args

    def isParamsEqual(self, *args):
        return self.__args == args
