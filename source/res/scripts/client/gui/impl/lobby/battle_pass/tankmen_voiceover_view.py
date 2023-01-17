# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tankmen_voiceover_view.py
import logging
from battle_pass_common import BattlePassConsts
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBuyBattlePassUrl
from gui.battle_pass.battle_pass_constants import MIN_LEVEL
from gui.battle_pass.battle_pass_helpers import getSpecialVoiceTankmen, getTankmanInfo
from gui.battle_pass.sounds import BATTLE_PASS_SOUND_SPACE, BattlePassSounds
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tankman_model import TankmanModel, TankmanStates
from gui.impl.gen.view_models.views.lobby.battle_pass.tankmen_voiceover_view_model import TankmenVoiceoverViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.event_dispatcher import showShop
from helpers import dependency
from shared_utils import findFirst, first
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class TankmenVoiceoverView(ViewImpl):
    __slots__ = ()
    __battlePass = dependency.descriptor(IBattlePassController)
    __itemsCache = dependency.descriptor(IItemsCache)
    _COMMON_SOUND_SPACE = BATTLE_PASS_SOUND_SPACE

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.TankmenVoiceoverView())
        settings.model = TankmenVoiceoverViewModel()
        super(TankmenVoiceoverView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankmenVoiceoverView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TankmenVoiceoverView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__fillTankmen(getSpecialVoiceTankmen(), model.getTankmen())

    def _finalize(self):
        self.soundManager.playInstantSound(BattlePassSounds.HOLIDAY_VOICEOVERS_STOP)
        super(TankmenVoiceoverView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.close, self.__close),
         (self.viewModel.showShop, self.__showShop),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassChange),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassChange))

    def __close(self):
        self.destroyWindow()

    def __showShop(self):
        showShop(getBuyBattlePassUrl())
        self.destroyWindow()

    def __fillTankmen(self, tankmen, tankmenModels):
        tankmenModels.clear()
        for tankman in tankmen.get('progression', []):
            model = TankmanModel()
            self.__fillProgressionTankmanModel(model, tankman)
            tankmenModels.addViewModel(model)

        for tankman in tankmen.get('shop', []):
            model = TankmanModel()
            self.__fillShopTankmanModel(model, tankman)
            tankmenModels.addViewModel(model)

        tankmenModels.invalidate()

    def __fillProgressionTankmanModel(self, model, tankman):
        recruitInfo = getRecruitInfo(tankman)
        groupName = recruitInfo.getGroupName()
        model.setGroupName(groupName)
        model.setFullName(recruitInfo.getFullUserName())
        if self.__isTankmanRecieved(groupName):
            state = TankmanStates.RECEIVED
        else:
            state = TankmanStates.AVAILABLEINPROGRESSION if self.__battlePass.isActive() else TankmanStates.UNAVAILABLE
        level = self.__getTankmanProgressionLevel(groupName) if state == TankmanStates.AVAILABLEINPROGRESSION else 0
        model.setProgressionLevel(level)
        model.setState(state)

    def __fillShopTankmanModel(self, model, tankman):
        recruitInfo = getRecruitInfo(tankman)
        groupName = recruitInfo.getGroupName()
        model.setGroupName(groupName)
        model.setFullName(recruitInfo.getFullUserName())
        state = TankmanStates.RECEIVED if self.__isTankmanRecieved(groupName) else TankmanStates.AVAILABLEINSHOP
        model.setState(state)

    def __getTankmanProgressionLevel(self, groupName):
        progressionLevel = 0
        chapterID = first(self.__battlePass.getChapterIDs())
        maxLevel = self.__battlePass.getMaxLevelInChapter(chapterID)
        awards = self.__battlePass.getAwardsInterval(chapterID, MIN_LEVEL, maxLevel, BattlePassConsts.REWARD_BOTH)
        for level, bonuses in awards.iteritems():
            tankmanBonus = findFirst(lambda b: b.getName() == 'tmanToken', bonuses)
            if tankmanBonus is not None:
                tankmanInfo = getTankmanInfo(tankmanBonus)
                if tankmanInfo is not None and tankmanInfo.getGroupName() == groupName:
                    progressionLevel = level
                    break

        if not progressionLevel:
            _logger.error('Tankman with group %s is not found!', groupName)
        return progressionLevel

    def __isTankmanRecieved(self, groupName):
        return self.__itemsCache.items.stats.entitlements.get(groupName, 0) > 0

    def __onBattlePassChange(self, *_):
        with self.viewModel.transaction() as model:
            self.__fillTankmen(getSpecialVoiceTankmen(), model.getTankmen())


class TankmenVoiceoverWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(TankmenVoiceoverWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TankmenVoiceoverView(), parent=parent)
