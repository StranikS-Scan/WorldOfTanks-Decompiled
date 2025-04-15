# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/hb_meta_view/mark_detail_model.py
from frameworks.wulf import ViewModel

class MarkDetailModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MarkDetailModel, self).__init__(properties=properties, commands=commands)

    def getLocked(self):
        return self._getBool(0)

    def setLocked(self, value):
        self._setBool(0, value)

    def getVideoUrl(self):
        return self._getString(1)

    def setVideoUrl(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(MarkDetailModel, self)._initialize()
        self._addBoolProperty('locked', False)
        self._addStringProperty('videoUrl', '')
