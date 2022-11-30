# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/dialogs/challenge/challenge_confirm_dialog_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.sub_views.challenge_discount_model import ChallengeDiscountModel
from gui.impl.gen.view_models.views.lobby.new_year.dialogs.challenge.sub_views.challenge_task_switch_model import ChallengeTaskSwitchModel

class DialogViews(Enum):
    TASKSWITCH = 'TaskSwitch'
    DISCOUNT = 'Discount'


class ChallengeConfirmDialogModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(ChallengeConfirmDialogModel, self).__init__(properties=properties, commands=commands)

    @property
    def challengeTaskSwitchModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getChallengeTaskSwitchModelType():
        return ChallengeTaskSwitchModel

    @property
    def challengeDiscountModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getChallengeDiscountModelType():
        return ChallengeDiscountModel

    def getCurrentViewID(self):
        return self._getNumber(2)

    def setCurrentViewID(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ChallengeConfirmDialogModel, self)._initialize()
        self._addViewModelProperty('challengeTaskSwitchModel', ChallengeTaskSwitchModel())
        self._addViewModelProperty('challengeDiscountModel', ChallengeDiscountModel())
        self._addNumberProperty('currentViewID', 0)
        self.onClose = self._addCommand('onClose')
