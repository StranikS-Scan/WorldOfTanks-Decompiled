# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_challenge_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.new_year.views.base.ny_scene_rotatable_view import NySceneRotatableView
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_office_model import NewYearChallengeOfficeModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_guest_d_customization_model import NewYearGuestDCustomizationModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quests_celebrity_model import NewYearQuestsCelebrityModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_tournament_celebrity_model import NewYearTournamentCelebrityModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.ny_challenge_completed_model import NyChallengeCompletedModel

class ChallengeViewStates(Enum):
    TOURNAMENT = 'tournament'
    GUESTA = 'guestA'
    GUESTM = 'guestM'
    GUESTC = 'guestC'
    GUESTD = 'guestD'
    COMPLETED = 'completed'
    HEADQUARTERS = 'headquarters'


class Celebrity(Enum):
    GUESTA = 'guest_A'
    GUESTM = 'guest_M'
    GUESTC = 'guest_C'
    GUESTD = 'guest_D'


class NewYearChallengeModel(NySceneRotatableView):
    __slots__ = ()

    def __init__(self, properties=8, commands=2):
        super(NewYearChallengeModel, self).__init__(properties=properties, commands=commands)

    @property
    def tournamentCelebrityModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getTournamentCelebrityModelType():
        return NewYearTournamentCelebrityModel

    @property
    def questsCelebrityModel(self):
        return self._getViewModel(2)

    @staticmethod
    def getQuestsCelebrityModelType():
        return NewYearQuestsCelebrityModel

    @property
    def challengeOfficeModel(self):
        return self._getViewModel(3)

    @staticmethod
    def getChallengeOfficeModelType():
        return NewYearChallengeOfficeModel

    @property
    def completedModel(self):
        return self._getViewModel(4)

    @staticmethod
    def getCompletedModelType():
        return NyChallengeCompletedModel

    @property
    def guestDCustomizationModel(self):
        return self._getViewModel(5)

    @staticmethod
    def getGuestDCustomizationModelType():
        return NewYearGuestDCustomizationModel

    def getViewState(self):
        return ChallengeViewStates(self._getString(6))

    def setViewState(self, value):
        self._setString(6, value.value)

    def getIsDiscountPopoverOpened(self):
        return self._getBool(7)

    def setIsDiscountPopoverOpened(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(NewYearChallengeModel, self)._initialize()
        self._addViewModelProperty('tournamentCelebrityModel', NewYearTournamentCelebrityModel())
        self._addViewModelProperty('questsCelebrityModel', NewYearQuestsCelebrityModel())
        self._addViewModelProperty('challengeOfficeModel', NewYearChallengeOfficeModel())
        self._addViewModelProperty('completedModel', NyChallengeCompletedModel())
        self._addViewModelProperty('guestDCustomizationModel', NewYearGuestDCustomizationModel())
        self._addStringProperty('viewState')
        self._addBoolProperty('isDiscountPopoverOpened', False)
