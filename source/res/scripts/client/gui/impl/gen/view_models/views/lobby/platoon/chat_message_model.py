# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/chat_message_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.chat_message_part_model import ChatMessagePartModel

class ChatMessageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ChatMessageModel, self).__init__(properties=properties, commands=commands)

    @property
    def playerName(self):
        return self._getViewModel(0)

    @staticmethod
    def getPlayerNameType():
        return ChatMessagePartModel

    @property
    def timeStamp(self):
        return self._getViewModel(1)

    @staticmethod
    def getTimeStampType():
        return ChatMessagePartModel

    @property
    def text(self):
        return self._getViewModel(2)

    @staticmethod
    def getTextType():
        return ChatMessagePartModel

    def getKey(self):
        return self._getNumber(3)

    def setKey(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ChatMessageModel, self)._initialize()
        self._addViewModelProperty('playerName', ChatMessagePartModel())
        self._addViewModelProperty('timeStamp', ChatMessagePartModel())
        self._addViewModelProperty('text', ChatMessagePartModel())
        self._addNumberProperty('key', 0)
