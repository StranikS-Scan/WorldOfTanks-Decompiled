# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/album_card_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ContentType(Enum):
    IMAGE = 'image'
    VIDEO = 'video'


class AlbumCardViewModel(ViewModel):
    __slots__ = ('onClose', 'onPreview', 'onLearn')

    def __init__(self, properties=6, commands=3):
        super(AlbumCardViewModel, self).__init__(properties=properties, commands=commands)

    def getImageSrc(self):
        return self._getString(0)

    def setImageSrc(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getContentType(self):
        return ContentType(self._getString(3))

    def setContentType(self, value):
        self._setString(3, value.value)

    def getLearning(self):
        return self._getBool(4)

    def setLearning(self, value):
        self._setBool(4, value)

    def getIsBlurred(self):
        return self._getBool(5)

    def setIsBlurred(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(AlbumCardViewModel, self)._initialize()
        self._addStringProperty('imageSrc', '')
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addStringProperty('contentType', ContentType.IMAGE.value)
        self._addBoolProperty('learning', False)
        self._addBoolProperty('isBlurred', False)
        self.onClose = self._addCommand('onClose')
        self.onPreview = self._addCommand('onPreview')
        self.onLearn = self._addCommand('onLearn')
