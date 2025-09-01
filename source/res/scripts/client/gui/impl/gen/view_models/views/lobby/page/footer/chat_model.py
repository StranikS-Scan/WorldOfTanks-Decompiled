# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/footer/chat_model.py
from frameworks.wulf import Map, ViewModel
from gui.impl.gen.view_models.views.lobby.page.footer.message_model import MessageModel

class ChatModel(ViewModel):
    __slots__ = ('onViewMessageAction', 'onDeleteMessageAction', 'onWindowAnchorPositionUpdated', 'onChatsAction')

    def __init__(self, properties=1, commands=4):
        super(ChatModel, self).__init__(properties=properties, commands=commands)

    def getMessages(self):
        return self._getMap(0)

    def setMessages(self, value):
        self._setMap(0, value)

    @staticmethod
    def getMessagesType():
        return (unicode, MessageModel)

    def _initialize(self):
        super(ChatModel, self)._initialize()
        self._addMapProperty('messages', Map(unicode, MessageModel))
        self.onViewMessageAction = self._addCommand('onViewMessageAction')
        self.onDeleteMessageAction = self._addCommand('onDeleteMessageAction')
        self.onWindowAnchorPositionUpdated = self._addCommand('onWindowAnchorPositionUpdated')
        self.onChatsAction = self._addCommand('onChatsAction')
