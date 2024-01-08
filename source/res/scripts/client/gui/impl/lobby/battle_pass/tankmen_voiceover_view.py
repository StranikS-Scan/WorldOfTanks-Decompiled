# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tankmen_voiceover_view.py
import logging
from urlparse import urljoin
from battle_pass_common import BattlePassTankmenSource, TANKMAN_QUEST_CHAIN_ENTITLEMENT_POSTFIX
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL
from gui.battle_pass.battle_pass_helpers import getReceivedTankmenCount
from gui.battle_pass.sounds import BattlePassSounds
from gui.collection.collections_helpers import getTankmanFullName
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.tankman_model import TankmanModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tankmen_voiceover_view_model import TankmenVoiceoverViewModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared.event_dispatcher import showShop
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import IBattlePassController
_logger = logging.getLogger(__name__)

class TankmenVoiceoverView(ViewImpl):
    __slots__ = ()
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.battle_pass.TankmenVoiceoverView())
        settings.model = TankmenVoiceoverViewModel()
        super(TankmenVoiceoverView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(TankmenVoiceoverView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TankmenVoiceoverView, self)._onLoading(*args, **kwargs)
        switchHangarOverlaySoundFilter(on=True)
        self.__battlePass.tankmenCacheUpdate()
        self.__fillModel()

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        self.soundManager.playInstantSound(BattlePassSounds.HOLIDAY_VOICEOVER_STOP if self.__battlePass.isHoliday() else BattlePassSounds.VOICEOVER_STOP)
        super(TankmenVoiceoverView, self)._finalize()

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            self.__fillTankmen(self.__battlePass.getSpecialTankmen(), model.getTankmen())

    def _getEvents(self):
        return ((self.viewModel.close, self.__close),
         (self.viewModel.showShop, self.__showShop),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassChange),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassChange),
         (self.__battlePass.onExtraChapterExpired, self.__onBattlePassChange),
         (self.__battlePass.onEntitlementCacheUpdated, self.__fillModel))

    def __close(self):
        self.destroyWindow()

    def __showShop(self, args):
        tankmanGroupName = args.get('tankmanGroupName')
        tankmanBundlePath = self.__battlePass.getSpecialTankmen().get(tankmanGroupName, {}).get('bundlePath', '')
        showShop(urljoin(getShopURL(), tankmanBundlePath))
        self.destroyWindow()

    def __tankmanInfo(self, tankman):
        return self.__battlePass.getSpecialTankmen().get(tankman, {})

    def __getTankmenByPriority(self, tankmenDict):
        return sorted(tankmenDict.keys(), key=lambda k: tankmenDict[k].get('priority', 0))

    def __getCount(self, tankman):
        return self.__tankmanInfo(tankman).get('availableCount', 0)

    def __fillTankmen(self, tankmenDict, tankmenModels):
        tankmenModels.clear()
        for tankman in self.__getTankmenByPriority(tankmenDict):
            model = TankmanModel()
            self.__fillTankmanModel(model, tankman)
            tankmenModels.addViewModel(model)

        tankmenModels.invalidate()

    def __fillTankmanModel(self, model, groupName):
        tankmanInfo = self.__tankmanInfo(groupName)
        source = tankmanInfo.get('source', '')
        count = self.__getCount(groupName)
        model.setGroupName(groupName)
        model.setFullName(getTankmanFullName(groupName))
        model.setCount(count)
        model.setHasVoiceover(self.__battlePass.isVoicedTankman(groupName))
        self.__fillTankmenStateForModel(model, groupName, source, count)
        self.__fillTankmenProgressionInfo(model, tankmanInfo, source)

    def __fillTankmenStateForModel(self, model, groupName, source, count):
        receivedCount = getReceivedTankmenCount(groupName)
        availableCount = count - receivedCount
        if source == BattlePassTankmenSource.SHOP:
            state = self.__getStateForShopTankmanModel(count, availableCount)
        if source == BattlePassTankmenSource.QUEST_CHAIN:
            state, availableCount = self.__getStateForQuestChainTankmanModel(groupName, count)
            if state == TankmanModel.AVAILABLE_IN_QUEST_CHAIN and receivedCount:
                state = TankmanModel.RECEIVED
        if source in BattlePassTankmenSource.PROGRESSION:
            state = self.__getStateForProgressionTankmanModel(source, receivedCount)
        model.setAvailableCount(availableCount)
        model.setState(state)

    def __fillTankmenProgressionInfo(self, model, tankmanInfo, source):
        if source in BattlePassTankmenSource.PROGRESSION:
            chapterID = tankmanInfo.get('chapterID', 0)
            level = tankmanInfo.get('progressionLevel', 0)
            model.setChapterID(chapterID)
            model.setProgressionLevel(level)

    def __getStateForShopTankmanModel(self, count, availableCount):
        if availableCount <= 0:
            return TankmanModel.RECEIVED
        return TankmanModel.IN_SHOP if availableCount == count else TankmanModel.NOT_FULL

    def __getStateForQuestChainTankmanModel(self, groupName, count):
        receivedQuestCount = getReceivedTankmenCount(groupName + TANKMAN_QUEST_CHAIN_ENTITLEMENT_POSTFIX)
        questChainsLeftToBuy = count - receivedQuestCount
        if questChainsLeftToBuy <= 0:
            state = TankmanModel.AVAILABLE_IN_QUEST_CHAIN
        elif questChainsLeftToBuy == count:
            state = TankmanModel.QUEST_CHAIN
        else:
            state = TankmanModel.NOT_FULL
        return (state, questChainsLeftToBuy)

    def __getStateForProgressionTankmanModel(self, source, receivedCount=0):
        if receivedCount:
            return TankmanModel.RECEIVED
        if self.__battlePass.isActive() and (self.__battlePass.hasExtra() or self.__battlePass.isHoliday()):
            if source == BattlePassTankmenSource.PAID:
                return TankmanModel.PAID
            return TankmanModel.FREE
        return TankmanModel.UNAVAILABLE

    def __onBattlePassChange(self, *_):
        if self.__battlePass.getSpecialVoiceChapters():
            self.__battlePass.tankmenCacheUpdate()
        else:
            self.__close()


class TankmenVoiceoverWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, parent=None):
        super(TankmenVoiceoverWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=TankmenVoiceoverView(), parent=parent)
