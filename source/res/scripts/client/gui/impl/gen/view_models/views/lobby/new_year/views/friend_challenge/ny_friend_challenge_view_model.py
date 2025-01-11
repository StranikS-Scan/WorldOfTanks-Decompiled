# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/friend_challenge/ny_friend_challenge_view_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.new_year.views.base.ny_scene_rotatable_view import NySceneRotatableView
from gui.impl.gen.view_models.views.lobby.new_year.views.friend_challenge.friend_challenge_card_model import FriendChallengeCardModel

class NyFriendChallengeViewModel(NySceneRotatableView):
    __slots__ = ()

    def __init__(self, properties=4, commands=2):
        super(NyFriendChallengeViewModel, self).__init__(properties=properties, commands=commands)

    def getChallengeList(self):
        return self._getArray(1)

    def setChallengeList(self, value):
        self._setArray(1, value)

    @staticmethod
    def getChallengeListType():
        return FriendChallengeCardModel

    def getShowDogTooltip(self):
        return self._getBool(2)

    def setShowDogTooltip(self, value):
        self._setBool(2, value)

    def getFriendName(self):
        return self._getString(3)

    def setFriendName(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(NyFriendChallengeViewModel, self)._initialize()
        self._addArrayProperty('challengeList', Array())
        self._addBoolProperty('showDogTooltip', False)
        self._addStringProperty('friendName', '')
