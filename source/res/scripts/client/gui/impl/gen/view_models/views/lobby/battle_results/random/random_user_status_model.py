# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/random/random_user_status_model.py
from gui.impl.gen.view_models.common.account_model import AccountModel
from gui.impl.gen.view_models.views.lobby.battle_results.user_status_model import UserStatusModel

class RandomUserStatusModel(UserStatusModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RandomUserStatusModel, self).__init__(properties=properties, commands=commands)

    @property
    def killer(self):
        return self._getViewModel(3)

    @staticmethod
    def getKillerType():
        return AccountModel

    def _initialize(self):
        super(RandomUserStatusModel, self)._initialize()
        self._addViewModelProperty('killer', AccountModel())
