# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/dog_tags/dt_dog_tag.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.dog_tags.dt_component import DtComponent

class DtDogTag(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DtDogTag, self).__init__(properties=properties, commands=commands)

    @property
    def engraving(self):
        return self._getViewModel(0)

    @staticmethod
    def getEngravingType():
        return DtComponent

    @property
    def background(self):
        return self._getViewModel(1)

    @staticmethod
    def getBackgroundType():
        return DtComponent

    def getPlayerName(self):
        return self._getString(2)

    def setPlayerName(self, value):
        self._setString(2, value)

    def getClanTag(self):
        return self._getString(3)

    def setClanTag(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(DtDogTag, self)._initialize()
        self._addViewModelProperty('engraving', DtComponent())
        self._addViewModelProperty('background', DtComponent())
        self._addStringProperty('playerName', '')
        self._addStringProperty('clanTag', '')
