# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/sub_views/teaser_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class Type(Enum):
    NEWS = 'news'
    SHOPPROMO = 'shopPromo'
    NONE = 'none'


class TeaserModel(ViewModel):
    __slots__ = ('onClick', 'onClose')

    def __init__(self, properties=7, commands=2):
        super(TeaserModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return Type(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getPostCounter(self):
        return self._getNumber(1)

    def setPostCounter(self, value):
        self._setNumber(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getText(self):
        return self._getString(3)

    def setText(self, value):
        self._setString(3, value)

    def getIsVideo(self):
        return self._getBool(4)

    def setIsVideo(self, value):
        self._setBool(4, value)

    def getFinishTime(self):
        return self._getNumber(5)

    def setFinishTime(self, value):
        self._setNumber(5, value)

    def getImage(self):
        return self._getString(6)

    def setImage(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(TeaserModel, self)._initialize()
        self._addStringProperty('type', Type.NONE.value)
        self._addNumberProperty('postCounter', 0)
        self._addStringProperty('description', '')
        self._addStringProperty('text', '')
        self._addBoolProperty('isVideo', False)
        self._addNumberProperty('finishTime', -1)
        self._addStringProperty('image', '')
        self.onClick = self._addCommand('onClick')
        self.onClose = self._addCommand('onClose')
