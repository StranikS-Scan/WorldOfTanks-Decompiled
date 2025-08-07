# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/gen/view_models/views/lobby/birthday/collage_view_model.py
from frameworks.wulf import ViewModel

class CollageViewModel(ViewModel):
    __slots__ = ('onClose', 'onStartMoving', 'onMoveSpace', 'onStartFadeInAnim')

    def __init__(self, properties=0, commands=4):
        super(CollageViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(CollageViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onStartMoving = self._addCommand('onStartMoving')
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onStartFadeInAnim = self._addCommand('onStartFadeInAnim')
