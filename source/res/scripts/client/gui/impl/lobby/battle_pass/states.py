# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/states.py
from typing import TYPE_CHECKING
from ClientSelectableCameraObject import ClientSelectableCameraObject
from battle_pass_common import BattlePassConsts, FinalReward
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.battle_pass.battle_pass_helpers import getAllFinalRewards, getExtraVideoURL, getIntroVideoURL, getStyleForChapter, getVehicleInfoForChapter
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.lobby.battle_pass.common import isExtraChapterSeen, isExtraVideoShown, isIntroShown, isIntroVideoShown, setExtraChapterSeen, setExtraVideoShown, setIntroVideoShown, showOverlayVideo
from gui.lobby_state_machine.states import LobbyState, LobbyStateDescription, SubScopeSubLayerState, ViewLobbyState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.shared.event_dispatcher import showBattlePass, showBattlePassStyleProgressionPreview, showStylePreview, showVehiclePreviewWithoutBottomPanel
from helpers import dependency
from shared_utils import nextTick
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.shared import IItemsCache
from web.web_client_api.common import ItemPackEntry, ItemPackType
if TYPE_CHECKING:
    from typing import Dict, Union
    from frameworks.state_machine import State
_BP = R.aliases.battle_pass

def registerStates(machine):
    machine.addState(BattlePassState())


def registerTransitions(machine):
    battlePassState = machine.getStateByCls(BattlePassState)
    machine.addNavigationTransitionFromParent(battlePassState)


@SubScopeSubLayerState.parentOf
class BattlePassState(ViewLobbyState):
    STATE_ID = 'battlePass'
    VIEW_KEY = ViewKey(VIEW_ALIAS.BATTLE_PASS)

    def registerStates(self):
        lsm = self.getMachine()
        childStates = STATES.copy()
        lsm.addState(childStates.pop(_INITIAL_STATE_ID)(flags=StateFlags.INITIAL))
        for state in childStates.itervalues():
            lsm.addState(state())

    def registerTransitions(self):
        lsm = self.getMachine()
        for state in self.getChildrenStates():
            if state.VIEW_KEY.alias not in (_BP.IntroVideo(), _BP.ExtraVideo()):
                lsm.addNavigationTransitionFromParent(state)

        introVideoState = lsm.getStateByCls(IntroVideoBattlePassState)
        self.addTransition(HijackTransition(IntroBattlePassState, _shallNavigateToIntroVideo), introVideoState)
        extraVideoState = lsm.getStateByCls(ExtraVideoBattlePassState)
        self.addTransition(HijackTransition(IntroBattlePassState, _shallNavigateToExtraVideo), extraVideoState)

    def _onEntered(self, event):
        super(BattlePassState, self)._onEntered(event)
        childStateID = event.params.get('childStateID', R.invalid())
        if childStateID in STATES:
            STATES[childStateID].goTo(**event.params)


class _BattlePassPresenterState(LobbyState):

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_BattlePassPresenterState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def serializeParams(self):
        return self.__cachedParams

    def addNavigationTransition(self, targetViewState, transitionType=TransitionType.INTERNAL, record=True):
        super(_BattlePassPresenterState, self).addNavigationTransition(targetViewState, transitionType, record)

    def getNavigationDescription(self):
        shortStateID = self.STATE_ID.split('/')[-1]
        return LobbyStateDescription(title=backport.text(R.strings.battle_pass.navigation.dyn(shortStateID)(), **self._getNavigationDescriptionArgs()))

    def _getNavigationDescriptionArgs(self):
        return {}

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(_BattlePassPresenterState, self)._onEntered(event)

    def _onExited(self):
        super(_BattlePassPresenterState, self)._onExited()
        self.__cachedParams = {}


@BattlePassState.parentOf
class IntroVideoBattlePassState(LobbyState):
    STATE_ID = 'introVideo'
    VIEW_KEY = ViewKey(_BP.IntroVideo())

    def _onEntered(self, event):
        super(IntroVideoBattlePassState, self)._onEntered(event)
        self.__showOverlayVideo()

    @nextTick
    def __showOverlayVideo(self):
        showOverlayVideo(getIntroVideoURL(), self.__onVideoShown)

    @staticmethod
    def __onVideoShown():
        setIntroVideoShown()
        IntroBattlePassState.goTo()


@BattlePassState.parentOf
class ExtraVideoBattlePassState(LobbyState):
    STATE_ID = 'extraVideo'
    VIEW_KEY = ViewKey(_BP.ExtraVideo())

    def _onEntered(self, event):
        super(ExtraVideoBattlePassState, self)._onEntered(event)
        self.__showOverlayVideo()

    @nextTick
    def __showOverlayVideo(self):
        showOverlayVideo(getExtraVideoURL(), self.__onVideoShown)

    @staticmethod
    def __onVideoShown():
        setExtraVideoShown()
        IntroBattlePassState.goTo()


@BattlePassState.parentOf
class IntroBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'intro'
    VIEW_KEY = ViewKey(_BP.Intro())
    __battlePass = dependency.descriptor(IBattlePassController)

    def _getNavigationDescriptionArgs(self):
        return {'seasonNum': self.__battlePass.getSeasonNum()}

    def _onEntered(self, event):
        if self.__needShowIntroView():
            super(IntroBattlePassState, self)._onEntered(event)
        elif self.__battlePass.hasExtra() and not isExtraChapterSeen():
            setExtraChapterSeen()
            showBattlePass(_BP.ChapterChoice())
        else:
            showBattlePass(**event.params)

    def __needShowIntroView(self):
        return not isIntroVideoShown() or not isExtraVideoShown() or not isIntroShown()


@BattlePassState.parentOf
class ChapterChoiceBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'chapterChoice'
    VIEW_KEY = ViewKey(_BP.ChapterChoice())
    __battlePass = dependency.descriptor(IBattlePassController)

    def registerTransitions(self):
        lsm = self.getMachine()
        progressionState = lsm.getStateByCls(ProgressionBattlePassState)
        postProgressionState = lsm.getStateByCls(PostProgressionBattlePassState)
        self.addNavigationTransition(progressionState)
        self.addNavigationTransition(postProgressionState)

    def _getNavigationDescriptionArgs(self):
        return {'seasonNum': self.__battlePass.getSeasonNum()}


@BattlePassState.parentOf
class ProgressionBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'progression'
    VIEW_KEY = ViewKey(_BP.Progression())

    def registerTransitions(self):
        lsm = self.getMachine()
        buyPassState = lsm.getStateByCls(BuyPassBattlePassState)
        buyLevelsState = lsm.getStateByCls(BuyLevelsBattlePassState)
        finalRewardPreviewState = lsm.getStateByCls(FinalRewardPreviewBattlePassState)
        self.addNavigationTransition(buyPassState)
        self.addNavigationTransition(buyLevelsState)
        self.addNavigationTransition(finalRewardPreviewState)


@BattlePassState.parentOf
class PostProgressionBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'postProgression'
    VIEW_KEY = ViewKey(_BP.PostProgression())

    def registerTransitions(self):
        lsm = self.getMachine()
        progressionState = lsm.getStateByCls(ProgressionBattlePassState)
        buyPassState = lsm.getStateByCls(BuyPassBattlePassState)
        buyPassConfirmState = lsm.getStateByCls(BuyPassConfirmBattlePassState)
        self.addNavigationTransition(progressionState)
        self.addNavigationTransition(buyPassState)
        self.addNavigationTransition(buyPassConfirmState)


@BattlePassState.parentOf
class BuyPassBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyPass'
    VIEW_KEY = ViewKey(_BP.BuyPass())

    def registerTransitions(self):
        lsm = self.getMachine()
        confirmState = lsm.getStateByCls(BuyPassConfirmBattlePassState)
        self.addNavigationTransition(confirmState)


@BattlePassState.parentOf
class BuyPassConfirmBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyPassConfirm'
    VIEW_KEY = ViewKey(_BP.BuyPassConfirm())

    def registerTransitions(self):
        lsm = self.getMachine()
        rewardsState = lsm.getStateByCls(BuyPassRewardsBattlePassState)
        self.addNavigationTransition(rewardsState)


@BattlePassState.parentOf
class BuyPassRewardsBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyPassRewards'
    VIEW_KEY = ViewKey(_BP.BuyPassRewards())


@BattlePassState.parentOf
class BuyLevelsBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyLevels'
    VIEW_KEY = ViewKey(_BP.BuyLevels())

    def registerTransitions(self):
        lsm = self.getMachine()
        rewardsState = lsm.getStateByCls(BuyLevelsRewardsBattlePassState)
        self.addNavigationTransition(rewardsState)


@BattlePassState.parentOf
class BuyLevelsRewardsBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'buyLevelsRewards'
    VIEW_KEY = ViewKey(_BP.BuyLevelsRewards())


@BattlePassState.parentOf
class HolidayFinalBattlePassState(_BattlePassPresenterState):
    STATE_ID = 'holidayFinal'
    VIEW_KEY = ViewKey(_BP.HolidayFinal())


@BattlePassState.parentOf
class FinalRewardPreviewBattlePassState(LobbyState):
    STATE_ID = 'finalRewardPreview'
    VIEW_KEY = ViewKey(_BP.FinalRewardPreview())
    __itemsCache = dependency.descriptor(IItemsCache)
    __battlePass = dependency.descriptor(IBattlePassController)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FinalRewardPreviewBattlePassState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        self.__cachedParams = event.params
        super(FinalRewardPreviewBattlePassState, self)._onEntered(event)
        ClientSelectableCameraObject.switchCamera()
        params = event.params
        chapterID = params['chapterID']
        origin = params['origin']
        bonusID = params.get('bonusID')
        level = params.get('level')
        styleInfo = getStyleForChapter(chapterID) if bonusID is None else self.__itemsCache.items.getItemByCD(bonusID)
        vehicleCD = getVehicleCDForStyle(styleInfo)
        if level is not None:
            showBattlePassStyleProgressionPreview(vehicleCD, styleInfo, styleInfo.getDescription(), chapterId=chapterID, styleLevel=int(level), backCallback=self.__getPreviewCallback(chapterID, origin))
            return
        else:
            allRewardTypes = getAllFinalRewards(chapterID)
            if FinalReward.VEHICLE in allRewardTypes:
                vehicle, style = getVehicleInfoForChapter(chapterID, awardSource=BattlePassConsts.REWARD_BOTH)
                if styleInfo is not None:
                    showStylePreview(vehicle.intCD, style=styleInfo, topPanelData={'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
                     'tabIDs': (TabID.VEHICLE, TabID.STYLE),
                     'currentTabID': TabID.STYLE,
                     'style': styleInfo}, itemsPack=self.__getPreviewItemPack(), backCallback=self.__getPreviewCallback(chapterID, origin))
                else:
                    showVehiclePreviewWithoutBottomPanel(vehicle.intCD, itemsPack=self.__getPreviewItemPack(), style=style, backCallback=self.__getPreviewCallback(chapterID, origin))
            elif FinalReward.STYLE in allRewardTypes or bonusID:
                showStylePreview(vehicleCD, style=styleInfo, itemsPack=self.__getPreviewItemPack(), backCallback=self.__getPreviewCallback(chapterID, origin))
            return

    def _onExited(self):
        super(FinalRewardPreviewBattlePassState, self)._onExited()
        self.__cachedParams = {}

    def __getPreviewItemPack(self):
        return (ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),)

    def __getPreviewCallback(self, chapterID, origin):

        def callback():
            if origin == R.aliases.battle_pass.Progression() and not self.__battlePass.isChapterExists(chapterID):
                showBattlePass(R.aliases.battle_pass.ChapterChoice())
            else:
                showBattlePass(origin, chapterID)

        return callback


STATES = {_BP.IntroVideo(): IntroVideoBattlePassState,
 _BP.ExtraVideo(): ExtraVideoBattlePassState,
 _BP.Intro(): IntroBattlePassState,
 _BP.ChapterChoice(): ChapterChoiceBattlePassState,
 _BP.Progression(): ProgressionBattlePassState,
 _BP.PostProgression(): PostProgressionBattlePassState,
 _BP.BuyPass(): BuyPassBattlePassState,
 _BP.BuyPassConfirm(): BuyPassConfirmBattlePassState,
 _BP.BuyPassRewards(): BuyPassRewardsBattlePassState,
 _BP.BuyLevels(): BuyLevelsBattlePassState,
 _BP.BuyLevelsRewards(): BuyLevelsRewardsBattlePassState,
 _BP.HolidayFinal(): HolidayFinalBattlePassState,
 _BP.FinalRewardPreview(): FinalRewardPreviewBattlePassState}
_INITIAL_STATE_ID = _BP.Intro()

def _shallNavigateToIntroVideo(event):
    return not isIntroVideoShown()


@dependency.replace_none_kwargs(battlePass=IBattlePassController)
def _shallNavigateToExtraVideo(event, battlePass=None):
    return isIntroVideoShown() and not isExtraVideoShown()
