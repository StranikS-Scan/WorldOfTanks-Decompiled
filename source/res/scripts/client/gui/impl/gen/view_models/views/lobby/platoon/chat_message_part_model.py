# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/chat_message_part_model.py
from frameworks.wulf import ViewModel

class ChatMessagePartModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ChatMessagePartModel, self).__init__(properties=properties, commands=commands)

    def getText(self):
        return self._getString(0)

    def setText(self, value):
        self._setString(0, value)

    def getColor(self):
        return self._getString(1)

    def setColor(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(ChatMessagePartModel, self)._initialize()
        self._addStringProperty('text', '')
        self._addStringProperty('color', '')
