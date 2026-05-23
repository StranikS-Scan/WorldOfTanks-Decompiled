# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/tankmen_voiceover_view.py
from __future__ import absolute_import
import logging
from future.moves.urllib.parse import urljoin
from battle_pass_common import BattlePassTankmenSource
from frameworks.wulf import Array
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getShopURL
from gui.battle_pass.battle_pass_helpers import getReceivedTankmenCount, getDataByTankman
from gui.battle_pass.sounds import BattlePassSounds
from gui.collection.collections_helpers import getTankmanFullName
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.skill_model import SkillModel
from gui.impl.gen.view_models.views.lobby.battle_pass.tankman_model import TankmanModel, TankmanStates
from gui.impl.gen.view_models.views.lobby.battle_pass.tankmen_voiceover_view_model import TankmenVoiceoverViewModel
from gui.impl.lobby.battle_pass.tooltips.crew_member_skill_tooltip import CrewMemberSkillTooltip
from gui.impl.pub.view_component import ViewComponent
from gui.server_events.recruit_helper import getRecruitInfo
from gui.shared.event_dispatcher import showShop
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from shared_utils import findFirst
from skeletons.gui.game_control import IBattlePassController
_logger = logging.getLogger(__name__)

class TankmenVoiceoverPresenter(ViewComponent[TankmenVoiceoverViewModel]):
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, *args, **kwargs):
        super(TankmenVoiceoverPresenter, self).__init__(R.aliases.battle_pass.TankmenScreen(), TankmenVoiceoverViewModel)
        self.__screenID = kwargs.get('screenID')

    @property
    def viewModel(self):
        return super(TankmenVoiceoverPresenter, self).getViewModel()

    def updateInitialData(self, **kwargs):
        self.__screenID = kwargs.get('screenID')
        self.__fillModel()

    def activate(self):
        self._subscribe()

    def deactivate(self):
        self._unsubscribe()

    def createToolTipContent(self, event, contentID):
        return CrewMemberSkillTooltip(event.getArgument('name'), event.getArgument('isZero'), event.getArgument('hasZeroPerk')) if contentID == R.views.mono.battle_pass.tooltips.crew_member_skill() else super(TankmenVoiceoverPresenter, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(TankmenVoiceoverPresenter, self)._onLoading(*args, **kwargs)
        switchHangarOverlaySoundFilter(on=True)
        self.__battlePass.tankmenCacheUpdate()
        self.__fillModel()

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        self.soundManager.playInstantSound(self._getStopSound())
        super(TankmenVoiceoverPresenter, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.showShop, self.__showShop),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassChange),
         (self.__battlePass.onSeasonStateChanged, self.__onBattlePassChange),
         (self.__battlePass.onExtraChapterExpired, self.__onBattlePassChange),
         (self.__battlePass.onEntitlementCacheUpdated, self.__fillModel))

    def _getStopSound(self):
        return BattlePassSounds.HOLIDAY_VOICEOVER_STOP if self.__battlePass.isHoliday() else BattlePassSounds.VOICEOVER_STOP

    def __showShop(self, args):
        tankmanGroupName = args.get('tankmanGroupName')
        tankmanToken = findFirst(lambda tankman: tankmanGroupName in tankman, self.__getTankmenForView(), '')
        tankmanBundlePath = self.__getTankmenForView().get(tankmanToken, {}).get('bundlePath', '')
        showShop(urljoin(getShopURL(), tankmanBundlePath))
        self.destroyWindow()

    def __getTankmanInfo(self, tankman):
        tankmanInfo = self.__getTankmenForView().get(tankman, {})
        if not tankmanInfo:
            _logger.error('Tankman info for %s cannot be empty!', tankman)
        return tankmanInfo

    def __getTankmenByPriority(self, tankmenDict):
        return sorted(tankmenDict.keys(), key=lambda k: tankmenDict[k].get('priority', 0))

    def __getCount(self, tankman):
        return self.__getTankmanInfo(tankman).get('availableCount', 0)

    def __getTankmenForView(self):
        return self.__battlePass.getTankmenScreens().get(self.__screenID, {}).get('tankmen', {})

    def __fillModel(self):
        with self.viewModel.transaction() as model:
            self.__fillTankmen(self.__getTankmenForView(), model.getTankmen())
            model.setScreenID(self.__screenID)

    def __fillTankmen(self, tankmenDict, tankmenModels):
        tankmenModels.clear()
        for tankman in self.__getTankmenByPriority(tankmenDict):
            model = TankmanModel()
            self.__fillTankmanModel(model, tankman)
            tankmenModels.addViewModel(model)

        tankmenModels.invalidate()

    def __fillTankmanModel(self, model, tankman):
        _, _, freeSkills, earnedSkills, groupName = getDataByTankman(getRecruitInfo(tankman))
        tankmanInfo = self.__getTankmanInfo(tankman)
        count = self.__getCount(tankman)
        skillsArray = Array()
        for skill in freeSkills:
            skillModel = SkillModel()
            skillModel.setName(skill)
            skillModel.setIsZero(True)
            skillsArray.addViewModel(skillModel)

        for skill in earnedSkills:
            skillModel = SkillModel()
            skillModel.setName(skill)
            skillModel.setIsZero(False)
            skillsArray.addViewModel(skillModel)

        model.setGroupName(groupName)
        model.setFullName(getTankmanFullName(groupName))
        model.setCount(count)
        model.setSkills(skillsArray)
        model.setHasVoiceover(self.__battlePass.isVoicedTankman(groupName))
        self.__fillTankmenStateForModel(model, tankman, tankmanInfo, count)
        self.__fillTankmenProgressionInfo(model, tankmanInfo)

    def __fillTankmenStateForModel(self, model, tankman, tankmanInfo, count):
        receivedCount = getReceivedTankmenCount(tankman)
        availableCount = count - receivedCount
        state = TankmanStates.UNAVAILABLE
        source = tankmanInfo.get('source', '')
        if source == BattlePassTankmenSource.SHOP:
            state = self.__getStateForShopTankmanModel(count, availableCount)
        if source == BattlePassTankmenSource.PROGRESSION:
            state = self.__getStateForProgressionTankmanModel(source, tankmanInfo.get('chapterId'), receivedCount)
        model.setAvailableCount(availableCount)
        model.setState(state)

    def __fillTankmenProgressionInfo(self, model, tankmanInfo):
        if tankmanInfo.get('source', '') == BattlePassTankmenSource.PROGRESSION:
            chapterID = tankmanInfo.get('chapterId', 0)
            level = tankmanInfo.get('progressionLevel', 0)
            model.setChapterID(chapterID)
            model.setProgressionLevel(level)

    def __getStateForShopTankmanModel(self, count, availableCount):
        if availableCount <= 0:
            return TankmanStates.RECEIVED
        return TankmanStates.IN_SHOP if availableCount == count else TankmanStates.NOT_FULL

    def __getStateForProgressionTankmanModel(self, source, chapterID, receivedCount):
        if receivedCount:
            return TankmanStates.RECEIVED
        return TankmanStates.PROGRESSION if self.__battlePass.isActive() and chapterID in self.__battlePass.getChapterIDs() else TankmanStates.UNAVAILABLE

    def __onBattlePassChange(self, *_):
        if self.__battlePass.getTankmenScreens():
            self.__battlePass.tankmenCacheUpdate()
        else:
            self.destroy()
