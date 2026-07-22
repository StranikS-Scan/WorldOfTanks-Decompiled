# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/post_battle_mail_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from mt_birthday.gui.impl.gen.view_models.views.lobby.birthday.post_battle_player_model import PostBattlePlayerModel

class PostBattleMailViewModel(ViewModel):
    __slots__ = ('onSent',)

    def __init__(self, properties=6, commands=1):
        super(PostBattleMailViewModel, self).__init__(properties=properties, commands=commands)

    def getStampCount(self):
        return self._getNumber(0)

    def setStampCount(self, value):
        self._setNumber(0, value)

    def getIsBlogger(self):
        return self._getBool(1)

    def setIsBlogger(self, value):
        self._setBool(1, value)

    def getIfCanSendBloggerGift(self):
        return self._getBool(2)

    def setIfCanSendBloggerGift(self, value):
        self._setBool(2, value)

    def getSendBackChance(self):
        return self._getNumber(3)

    def setSendBackChance(self, value):
        self._setNumber(3, value)

    def getAllyPlayerList(self):
        return self._getArray(4)

    def setAllyPlayerList(self, value):
        self._setArray(4, value)

    @staticmethod
    def getAllyPlayerListType():
        return PostBattlePlayerModel

    def getEnemyPlayerList(self):
        return self._getArray(5)

    def setEnemyPlayerList(self, value):
        self._setArray(5, value)

    @staticmethod
    def getEnemyPlayerListType():
        return PostBattlePlayerModel

    def _initialize(self):
        super(PostBattleMailViewModel, self)._initialize()
        self._addNumberProperty('stampCount', 0)
        self._addBoolProperty('isBlogger', False)
        self._addBoolProperty('ifCanSendBloggerGift', False)
        self._addNumberProperty('sendBackChance', 0)
        self._addArrayProperty('allyPlayerList', Array())
        self._addArrayProperty('enemyPlayerList', Array())
        self.onSent = self._addCommand('onSent')
