# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/abstract/ImageManagerMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIModule import BaseDAAPIModule

class ImageManagerMeta(BaseDAAPIModule):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIModule
    """

    def as_setImageCacheSettingsS(self, maxSize, minSize):
        return self.flashObject.as_setImageCacheSettings(maxSize, minSize) if self._isDAAPIInited() else None

    def as_loadImagesS(self, sourceData):
        return self.flashObject.as_loadImages(sourceData) if self._isDAAPIInited() else None

    def as_unloadImagesS(self, sourceData):
        return self.flashObject.as_unloadImages(sourceData) if self._isDAAPIInited() else None
