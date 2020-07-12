# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/event_info_view_model.py
from frameworks.wulf import ViewModel

class EventInfoViewModel(ViewModel):
    __slots__ = ('onInfoVideoClicked',)

    def __init__(self, properties=1, commands=1):
        super(EventInfoViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(EventInfoViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self.onInfoVideoClicked = self._addCommand('onInfoVideoClicked')
