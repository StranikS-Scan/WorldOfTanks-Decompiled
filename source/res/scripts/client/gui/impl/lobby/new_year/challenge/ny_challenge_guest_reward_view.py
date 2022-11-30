# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_guest_reward_view.py
from frameworks.wulf import ViewSettings, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.challenge_reward_view_model import ChallengeRewardViewModel, Type
from gui.impl.lobby.new_year.challenge.ny_challenge_reward_base_view import ChallengeRewardBaseView
from gui.impl.lobby.new_year.tooltips.ny_economic_bonus_tooltip import NyEconomicBonusTooltip
from gui.impl.new_year.navigation import NewYearNavigation, ViewAliases
from gui.impl.new_year.new_year_bonus_packer import getNYCelebrityGuestRewardBonuses, guestQuestBonusSortOrder
from gui.impl.new_year.new_year_helper import nyCreateToolTipContentDecorator
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared.event_dispatcher import hideVehiclePreview, showCelebrityGuestReward
from gui.shared import events, g_eventBus
from helpers import dependency, uniprof
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from new_year.ny_constants import GuestsQuestsTokens, NyTabBarChallengeView, AdditionalCameraObject, CHALLENGE_TAB_TO_CAMERA_OBJ
from skeletons.new_year import ICelebrityController
_SERVER_GUEST_ID_TO_TAB_NAME = {GuestsQuestsTokens.GUEST_A: NyTabBarChallengeView.GUEST_A,
 GuestsQuestsTokens.GUEST_M: NyTabBarChallengeView.GUEST_M,
 GuestsQuestsTokens.GUEST_C: NyTabBarChallengeView.GUEST_CAT}
_CHANGE_LAYERS_VISIBILITY = (WindowLayer.VIEW, WindowLayer.WINDOW)

class ChallengeGuestRewardView(ChallengeRewardBaseView):
    __celebrityController = dependency.descriptor(ICelebrityController)

    def __init__(self, layoutID, guestName, questIndex):
        settings = ViewSettings(layoutID)
        settings.model = ChallengeRewardViewModel()
        self.__guestName = guestName
        self.__questIndex = questIndex
        self._tooltips = {}
        super(ChallengeGuestRewardView, self).__init__(settings)

    @nyCreateToolTipContentDecorator
    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.new_year.tooltips.NyEconomicBonusTooltip():
            isMaxBonus = event.getArgument('isMaxBonus', False)
            if isMaxBonus or self.__questIndex > -1:
                return NyEconomicBonusTooltip(isMaxBonus, self.__questIndex, self.__guestName)
        return super(ChallengeGuestRewardView, self).createToolTipContent(event, contentID)

    @uniprof.regionDecorator(label='ny_challenge_guest_reward', scope='enter')
    def _initialize(self):
        super(ChallengeGuestRewardView, self)._initialize()
        self._changeLayersVisibility(True, _CHANGE_LAYERS_VISIBILITY)
        self.__onGuestRewardShow(self.__guestName)

    @uniprof.regionDecorator(label='ny_challenge_guest_reward', scope='exit')
    def _finalize(self):
        super(ChallengeGuestRewardView, self)._finalize()
        self._changeLayersVisibility(False, _CHANGE_LAYERS_VISIBILITY)
        if not self.isInPreview:
            self.__onGuestRewardHide(self.__guestName, self.__questIndex)

    def _backCallback(self):
        hideVehiclePreview(back=False, close=True)
        if self._nyController.isEnabled():
            guestID = _SERVER_GUEST_ID_TO_TAB_NAME.get(self.__guestName)
            objectName = CHALLENGE_TAB_TO_CAMERA_OBJ.get(guestID, AdditionalCameraObject.CELEBRITY)
            NewYearNavigation.switchTo(objectName, instantly=True, viewAlias=ViewAliases.CELEBRITY_VIEW, withFade=False, tabName=guestID, hidden=True)
            showCelebrityGuestReward(self.__guestName, self.__questIndex, instantly=True)
        super(ChallengeGuestRewardView, self)._backCallback()

    def _fillModel(self, model):
        super(ChallengeGuestRewardView, self)._fillModel(model)
        questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(self.__guestName)
        quest = questsHolder.getQuestByQuestIndex(self.__questIndex)
        model.setType(Type.QUEST)
        model.setCelebrity(self.__guestName)
        rewardsList = model.getRewards()
        rewardsList.clear()
        bonuses = quest.getQuestRewards()
        rewards = getNYCelebrityGuestRewardBonuses(bonuses, sortKey=lambda b: guestQuestBonusSortOrder(*b), excludeTokensChecker=GuestsQuestsTokens.isActionToken)
        for index, (bonus, tooltip) in enumerate(rewards):
            tooltipId = str(index)
            bonus.setTooltipId(tooltipId)
            bonus.setIndex(index)
            rewardsList.addViewModel(bonus)
            self._tooltips[tooltipId] = tooltip

        rewardsList.invalidate()

    def __onGuestRewardShow(self, guestName):
        ctx = {'guestName': guestName}
        g_eventBus.handleEvent(events.NyCelebrityRewardEvent(events.NyCelebrityRewardEvent.REWARD_GUEST_VIEW_OPENED, ctx=ctx))

    def __onGuestRewardHide(self, guestName, questIndex):
        ctx = {'guestName': guestName,
         'questIndex': questIndex}
        g_eventBus.handleEvent(events.NyCelebrityRewardEvent(events.NyCelebrityRewardEvent.REWARD_GUEST_VIEW_CLOSED, ctx=ctx))


class ChallengeGuestRewardViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, guestName, questIndex, parent=None):
        super(ChallengeGuestRewardViewWindow, self).__init__(content=ChallengeGuestRewardView(R.views.lobby.new_year.ChallengeRewardView(), guestName, questIndex), parent=parent, layer=WindowLayer.TOP_WINDOW)
