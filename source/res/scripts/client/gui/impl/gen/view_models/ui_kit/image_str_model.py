# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/image_str_model.py
from frameworks.wulf import ViewModel

class ImageStrModel(ViewModel):
    __slots__ = ()

    def getImgSource(self):
        return self._getString(0)

    def setImgSource(self, value):
        self._setString(0, value)

    def _initialize(self):
        self._addStringProperty('imgSource', '')
