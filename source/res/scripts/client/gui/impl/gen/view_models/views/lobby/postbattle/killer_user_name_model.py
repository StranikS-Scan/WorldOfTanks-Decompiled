# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/killer_user_name_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.user_name_model import UserNameModel

class KillerUserNameModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(KillerUserNameModel, self).__init__(properties=properties, commands=commands)

    @property
    def user(self):
        return self._getViewModel(0)

    def getIsPersonal(self):
        return self._getBool(1)

    def setIsPersonal(self, value):
        self._setBool(1, value)

    def getIsSameSquad(self):
        return self._getBool(2)

    def setIsSameSquad(self, value):
        self._setBool(2, value)

    def getIsBot(self):
        return self._getBool(3)

    def setIsBot(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(KillerUserNameModel, self)._initialize()
        self._addViewModelProperty('user', UserNameModel())
        self._addBoolProperty('isPersonal', False)
        self._addBoolProperty('isSameSquad', False)
        self._addBoolProperty('isBot', False)
