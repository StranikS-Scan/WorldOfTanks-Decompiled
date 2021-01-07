# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/chat_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.chat_message_model import ChatMessageModel
from gui.impl.gen.view_models.views.lobby.platoon.chat_message_part_model import ChatMessagePartModel

class ChatModel(ViewModel):
    __slots__ = ('onSend', 'onInputCleared')

    def __init__(self, properties=3, commands=2):
        super(ChatModel, self).__init__(properties=properties, commands=commands)

    @property
    def headerExtraInfo(self):
        return self._getViewModel(0)

    def getMessages(self):
        return self._getArray(1)

    def setMessages(self, value):
        self._setArray(1, value)

    def getCanClearInput(self):
        return self._getBool(2)

    def setCanClearInput(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ChatModel, self)._initialize()
        self._addViewModelProperty('headerExtraInfo', ChatMessagePartModel())
        self._addArrayProperty('messages', Array())
        self._addBoolProperty('canClearInput', False)
        self.onSend = self._addCommand('onSend')
        self.onInputCleared = self._addCommand('onInputCleared')
