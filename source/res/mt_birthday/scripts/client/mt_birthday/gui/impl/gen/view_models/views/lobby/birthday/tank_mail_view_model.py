# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/tank_mail_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.progression import Progression
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.user_item import UserItem

class TankMailViewModel(ViewModel):
    __slots__ = ('onPhraseChange', 'onPlayerSelect', 'onSent', 'onTasks', 'onAnimationEnded', 'onComponentDestroyed')

    def __init__(self, properties=7, commands=6):
        super(TankMailViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def progression(self):
        return self._getViewModel(0)

    @staticmethod
    def getProgressionType():
        return Progression

    def getCurrencyCount(self):
        return self._getNumber(1)

    def setCurrencyCount(self, value):
        self._setNumber(1, value)

    def getIsSentError(self):
        return self._getBool(2)

    def setIsSentError(self, value):
        self._setBool(2, value)

    def getIsPostError(self):
        return self._getBool(3)

    def setIsPostError(self, value):
        self._setBool(3, value)

    def getIsSending(self):
        return self._getBool(4)

    def setIsSending(self, value):
        self._setBool(4, value)

    def getPhraseID(self):
        return self._getNumber(5)

    def setPhraseID(self, value):
        self._setNumber(5, value)

    def getSelectedUsers(self):
        return self._getArray(6)

    def setSelectedUsers(self, value):
        self._setArray(6, value)

    @staticmethod
    def getSelectedUsersType():
        return UserItem

    def _initialize(self):
        super(TankMailViewModel, self)._initialize()
        self._addViewModelProperty('progression', Progression())
        self._addNumberProperty('currencyCount', 0)
        self._addBoolProperty('isSentError', False)
        self._addBoolProperty('isPostError', False)
        self._addBoolProperty('isSending', False)
        self._addNumberProperty('phraseID', 1)
        self._addArrayProperty('selectedUsers', Array())
        self.onPhraseChange = self._addCommand('onPhraseChange')
        self.onPlayerSelect = self._addCommand('onPlayerSelect')
        self.onSent = self._addCommand('onSent')
        self.onTasks = self._addCommand('onTasks')
        self.onAnimationEnded = self._addCommand('onAnimationEnded')
        self.onComponentDestroyed = self._addCommand('onComponentDestroyed')
