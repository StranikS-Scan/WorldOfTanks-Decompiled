# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_welcome_model.py
from frameworks.wulf import ViewModel

class WtEventWelcomeModel(ViewModel):
    __slots__ = ('onClose', 'onVideo')

    def __init__(self, properties=1, commands=2):
        super(WtEventWelcomeModel, self).__init__(properties=properties, commands=commands)

    def getIsVideoOpened(self):
        return self._getBool(0)

    def setIsVideoOpened(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(WtEventWelcomeModel, self)._initialize()
        self._addBoolProperty('isVideoOpened', False)
        self.onClose = self._addCommand('onClose')
        self.onVideo = self._addCommand('onVideo')
