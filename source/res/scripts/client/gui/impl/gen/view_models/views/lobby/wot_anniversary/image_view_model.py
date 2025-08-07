# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/image_view_model.py
from frameworks.wulf import ViewModel

class ImageViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=1, commands=1):
        super(ImageViewModel, self).__init__(properties=properties, commands=commands)

    def getImageSrc(self):
        return self._getString(0)

    def setImageSrc(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(ImageViewModel, self)._initialize()
        self._addStringProperty('imageSrc', '')
        self.onClose = self._addCommand('onClose')
