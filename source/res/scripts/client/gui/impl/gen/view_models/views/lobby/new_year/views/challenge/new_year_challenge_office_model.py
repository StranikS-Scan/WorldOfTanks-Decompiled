# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_challenge_office_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_action_model import NewYearChallengeActionModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_story_model import NewYearChallengeStoryModel

class NewYearChallengeOfficeModel(ViewModel):
    __slots__ = ('onStartAction', 'onShowStory')

    def __init__(self, properties=3, commands=2):
        super(NewYearChallengeOfficeModel, self).__init__(properties=properties, commands=commands)

    def getShowDogTooltip(self):
        return self._getBool(0)

    def setShowDogTooltip(self, value):
        self._setBool(0, value)

    def getActions(self):
        return self._getArray(1)

    def setActions(self, value):
        self._setArray(1, value)

    @staticmethod
    def getActionsType():
        return NewYearChallengeActionModel

    def getStories(self):
        return self._getArray(2)

    def setStories(self, value):
        self._setArray(2, value)

    @staticmethod
    def getStoriesType():
        return NewYearChallengeStoryModel

    def _initialize(self):
        super(NewYearChallengeOfficeModel, self)._initialize()
        self._addBoolProperty('showDogTooltip', False)
        self._addArrayProperty('actions', Array())
        self._addArrayProperty('stories', Array())
        self.onStartAction = self._addCommand('onStartAction')
        self.onShowStory = self._addCommand('onShowStory')
