# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/ui_kit/image_res_str_model.py
from frameworks.wulf import Resource
from frameworks.wulf import ViewModel

class ImageResStrModel(ViewModel):
    __slots__ = ()

    def getImgSource(self):
        return self._getResource(0)

    def setImgSource(self, value):
        self._setResource(0, value)

    def _initialize(self):
        super(ImageResStrModel, self)._initialize()
        self._addResourceProperty('imgSource', Resource.INVALID)
