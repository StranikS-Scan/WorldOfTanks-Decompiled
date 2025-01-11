# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/challenge/ny_challenge_headquarters.py
import typing
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_action_model import NewYearChallengeActionModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_story_model import NewYearChallengeStoryModel
from gui.impl.lobby.new_year.ny_history_presenter import NyHistoryPresenter
from helpers import dependency
from items.components.ny_constants import NYFriendServiceDataTokens
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from new_year.ny_constants import GuestsQuestsTokens, GuestQuestTokenActionType
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import ICelebrityController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_office_model import NewYearChallengeOfficeModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_model import NewYearChallengeModel
    from ny_common.GuestsQuestsConfig import GuestQuest
_QUEST_ACTION_TYPE_BY_TOKEN = {NYFriendServiceDataTokens.GUEST_A_QUEST_ANIM_1: 'guest_a_1',
 NYFriendServiceDataTokens.GUEST_A_QUEST_ANIM_2: 'guest_a_2',
 NYFriendServiceDataTokens.GUEST_A_QUEST_ANIM_3: 'guest_a_3',
 NYFriendServiceDataTokens.GUEST_C_QUEST_ANIM_1: 'guest_cat_1',
 NYFriendServiceDataTokens.GUEST_C_QUEST_ANIM_2: 'guest_cat_2',
 NYFriendServiceDataTokens.GUEST_C_QUEST_ANIM_3: 'guest_cat_3'}
_QUEST_TOKEN_BY_ACTION_TYPE = {v:k for k, v in _QUEST_ACTION_TYPE_BY_TOKEN.iteritems()}
_FIRST_STORY_LEVEL = 1

class NewYearChallengeHeadquarters(NyHistoryPresenter):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __celebrityController = dependency.descriptor(ICelebrityController)

    @property
    def viewModel(self):
        model = self.getViewModel()
        return model.challengeOfficeModel

    def initialize(self, *args, **kwargs):
        super(NewYearChallengeHeadquarters, self).initialize(self, *args, **kwargs)
        self.__fillModel()

    def _getEvents(self):
        evnts = super(NewYearChallengeHeadquarters, self)._getEvents()
        return evnts + ((self.viewModel.onStartAction, self.__onActionClick), (self.viewModel.onShowStory, self.__onStoryClick), (self.__celebrityController.onCelebActionTokenUpdated, self.__onCelebActionTokenUpdated))

    def __fillModel(self):
        with self.viewModel.transaction() as tx:
            actions = tx.getActions()
            actions.clear()
            stories = tx.getStories()
            stories.clear()
            for guestName in GuestsQuestsTokens.GUESTS_ALL:
                if GuestsQuestsConfigHelper.hasAnyAvailableGuestQuest(guestName):
                    animatedQuests = GuestsQuestsConfigHelper.getAnimatedGuestQuests(guestName)
                    for quest in animatedQuests:
                        slotType = self.__getQuestSlotType(quest)
                        if slotType is None:
                            continue
                        newAction = NewYearChallengeActionModel()
                        newAction.setType(slotType)
                        actions.addViewModel(newAction)

                    newAction = NewYearChallengeActionModel()
                    newAction.setIsSeparator(True)
                    actions.addViewModel(newAction)
                storiesTokens = GuestsQuestsConfigHelper.getGuestsActionTokens(guestName, GuestQuestTokenActionType.STORY)
                if storiesTokens:
                    completedStoriesTokens = self.__celebrityController.getAllReceivedTokens([guestName], [GuestQuestTokenActionType.STORY])
                    newStory = NewYearChallengeStoryModel()
                    newStory.setStoryBy(guestName)
                    newStory.setAvailableStories(len(completedStoriesTokens))
                    newStory.setTotalStories(len(storiesTokens))
                    stories.addViewModel(newStory)

            actions.invalidate()
            stories.invalidate()
        return

    def __getQuestSlotType(self, quest):
        if self.__celebrityController.isGuestQuestCompleted(quest):
            tokenID = GuestsQuestsConfigHelper.getQuestActionToken(quest, GuestQuestTokenActionType.ANIM)
            return _QUEST_ACTION_TYPE_BY_TOKEN.get(tokenID)
        else:
            guestName = GuestsQuestsConfigHelper.getGuestNameByQuest(quest)
            return 'empty' if guestName else None

    def __onActionClick(self, args):
        actionType = args.get('actionType', None)
        if actionType is None:
            return
        else:
            tokenID = _QUEST_TOKEN_BY_ACTION_TYPE.get(actionType)
            self.__celebrityController.doActionByCelebActionToken(tokenID)
            return

    def __onStoryClick(self, args):
        guestName = args.get('storyBy', None)
        if guestName is None:
            return
        else:
            tokenID = GuestsQuestsTokens.generateDefaultActionToken(guestName, GuestQuestTokenActionType.STORY, _FIRST_STORY_LEVEL)
            self.__celebrityController.doActionByCelebActionToken(tokenID)
            return

    def __onCelebActionTokenUpdated(self, token):
        self.__fillModel()
