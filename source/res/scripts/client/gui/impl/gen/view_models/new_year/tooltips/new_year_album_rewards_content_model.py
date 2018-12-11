# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/new_year/tooltips/new_year_album_rewards_content_model.py
import typing
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class NewYearAlbumRewardsContentModel(ViewModel):
    __slots__ = ()

    def getStyleName(self):
        return self._getString(0)

    def setStyleName(self, value):
        self._setString(0, value)

    def getEmblemName(self):
        return self._getString(1)

    def setEmblemName(self, value):
        self._setString(1, value)

    def getInscriptionName(self):
        return self._getString(2)

    def setInscriptionName(self, value):
        self._setString(2, value)

    def getNations(self):
        return self._getArray(3)

    def setNations(self, value):
        self._setArray(3, value)

    def getCollectionName(self):
        return self._getString(4)

    def setCollectionName(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(NewYearAlbumRewardsContentModel, self)._initialize()
        self._addStringProperty('styleName', '')
        self._addStringProperty('emblemName', '')
        self._addStringProperty('inscriptionName', '')
        self._addArrayProperty('nations', Array())
        self._addStringProperty('collectionName', '')
