# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/friend_challenge/ny_friend_challenge_view.py
import typing
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.new_year.views.friend_challenge.friend_challenge_card_model import FriendChallengeType, FriendChallengeCardModel
from gui.impl.lobby.new_year.ny_selectable_logic_presenter import SelectableLogicPresenter
from gui.impl.lobby.new_year.scene_rotatable_view import SceneRotatableView
from gui.impl.new_year.navigation import ViewAliases
from helpers import dependency
from items.components.ny_constants import NYFriendServiceDataTokens
from new_year.celebrity.celebrity_quests_helpers import GuestsQuestsConfigHelper
from skeletons.new_year import ICelebritySceneController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.friend_challenge.ny_friend_challenge_view_model import NyFriendChallengeViewModel
TYPE_TO_TOKEN_MAP = {FriendChallengeType.TOURNAMENT: NYFriendServiceDataTokens.CELEBRITY_QUEST_COMPLETED,
 FriendChallengeType.GUESTA: NYFriendServiceDataTokens.GUEST_A_QUEST_COMPLETED,
 FriendChallengeType.GUESTC: NYFriendServiceDataTokens.GUEST_CAT_QUEST_COMPLETED}

class NyFriendChallengeView(SceneRotatableView, SelectableLogicPresenter):
    __slots__ = ()
    _navigationAlias = ViewAliases.FRIEND_CELEBRITY_VIEW
    __celebrityController = dependency.descriptor(ICelebritySceneController)

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NyFriendChallengeView, self).initialize(*args, **kwargs)
        self.isMoveSpaceEnable(False)
        challengeTypes = [FriendChallengeType.TOURNAMENT, FriendChallengeType.GUESTA]
        friendTokens = self._friendsService.getFriendTokens()
        if friendTokens and friendTokens.get(NYFriendServiceDataTokens.CAT_UNLOCK, 0) > 0:
            challengeTypes.append(FriendChallengeType.GUESTC)
        with self.viewModel.transaction() as tx:
            tx.setFriendName(self._friendsService.getFriendName(self._friendsService.friendHangarSpaId))
            challengeList = Array()
            challengeList.reserve(len(challengeTypes))
            for challengeType in challengeTypes:
                challengeItem = FriendChallengeCardModel()
                challengeItem.setChallengeType(challengeType)
                challengeItem.setCurrentQuantity(friendTokens.get(TYPE_TO_TOKEN_MAP.get(challengeType), 0))
                if challengeType is FriendChallengeType.TOURNAMENT:
                    challengeItem.setTotalQuantity(self.__celebrityController.questsCount)
                else:
                    questsHolder = GuestsQuestsConfigHelper.getNYQuestsByGuest(challengeType.value)
                    challengeItem.setTotalQuantity(len(questsHolder.getQuests()))
                challengeList.addViewModel(challengeItem)

            tx.setChallengeList(challengeList)
