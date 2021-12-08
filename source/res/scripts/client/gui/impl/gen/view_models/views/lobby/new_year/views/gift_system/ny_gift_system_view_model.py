# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/gift_system/ny_gift_system_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.gifts_progression_model import GiftsProgressionModel
from gui.impl.gen.view_models.views.lobby.new_year.views.gift_system.submission_form_model import SubmissionFormModel

class State(IntEnum):
    NORMAL = 0
    NO_FRIENDS = 1
    NO_POST_STAMPS = 2
    NO_BALANCE = 3


class NyGiftSystemViewModel(ViewModel):
    __slots__ = ('onIntroClose', 'onQuestsBtnClick', 'onCelebrityBtnClick')

    def __init__(self, properties=5, commands=3):
        super(NyGiftSystemViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def submissionForm(self):
        return self._getViewModel(0)

    @property
    def giftsProgression(self):
        return self._getViewModel(1)

    def getIsIntroOpened(self):
        return self._getBool(2)

    def setIsIntroOpened(self, value):
        self._setBool(2, value)

    def getState(self):
        return State(self._getNumber(3))

    def setState(self, value):
        self._setNumber(3, value.value)

    def getPostStampsCount(self):
        return self._getNumber(4)

    def setPostStampsCount(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(NyGiftSystemViewModel, self)._initialize()
        self._addViewModelProperty('submissionForm', SubmissionFormModel())
        self._addViewModelProperty('giftsProgression', GiftsProgressionModel())
        self._addBoolProperty('isIntroOpened', False)
        self._addNumberProperty('state')
        self._addNumberProperty('postStampsCount', 0)
        self.onIntroClose = self._addCommand('onIntroClose')
        self.onQuestsBtnClick = self._addCommand('onQuestsBtnClick')
        self.onCelebrityBtnClick = self._addCommand('onCelebrityBtnClick')
