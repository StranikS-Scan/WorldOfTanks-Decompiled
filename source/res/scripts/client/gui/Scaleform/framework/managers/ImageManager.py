# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/ImageManager.py
from gui import GUI_SETTINGS
from gui.Scaleform.framework.entities.abstract.ImageManagerMeta import ImageManagerMeta

class ImageManager(ImageManagerMeta):

    def __init__(self):
        super(ImageManager, self).__init__()
        self.__cache = set()

    def loadImages(self, sourceData):
        data = []
        for source in sourceData:
            if source not in self.__cache:
                data.append(source)
                self.__cache.add(source)

        self.as_loadImagesS(data)

    def unloadImages(self, sourceData):
        data = []
        for source in sourceData:
            if source in self.__cache:
                data.append(source)
                self.__cache.remove(source)

        self.as_unloadImagesS(data)

    def _populate(self):
        super(ImageManager, self)._populate()
        self.__cache.clear()
        self.as_setImageCacheSettingsS(GUI_SETTINGS.imageCache['maxSize'] * 1024, GUI_SETTINGS.imageCache['minSize'] * 1024)

    def _dispose(self):
        self.__cache.clear()
        super(ImageManager, self)._dispose()
