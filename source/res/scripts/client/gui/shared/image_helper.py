# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/image_helper.py
import BigWorld
import ResMgr
from adisp import async
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.shared.utils import mapTextureToTheMemory, getImageSize, removeTextureFromMemory

def readLocalImage(path):
    data = ResMgr.openSection(path)
    return data.asBinary if data is not None else None


def getTextureLinkByID(imageID):
    return 'img://{}'.format(imageID)


class ImageHelper(object):

    @staticmethod
    def getMemoryTexturePath(image, temp=True):
        return mapTextureToTheMemory(image, temp=temp)

    @staticmethod
    def removeTextureFromMemory(textureID):
        removeTextureFromMemory(textureID)

    @staticmethod
    def requestImageByUrl(url, callback, size=None, defaultGetter=None):
        defaultGetter = defaultGetter or (lambda v: None)

        def _onImageReceived(_, img):
            if size:
                imgSize = getImageSize(img)
                if imgSize != size:
                    LOG_WARNING('Received image has invalid size, use default instead', imgSize, size, url, type(img))
                    img = defaultGetter(size)
            callback(img)

        if hasattr(BigWorld.player(), 'customFilesCache'):
            if url is not None:
                BigWorld.player().customFilesCache.get(url, _onImageReceived)
            else:
                BigWorld.callback(0.0, lambda : callback(defaultGetter(size)))
        else:
            LOG_WARNING('Trying to get image by url from non-account', url)
            BigWorld.callback(0.0, lambda : callback(defaultGetter(size)))
        return


class ImagesFetchCoordinator(object):

    def __init__(self):
        self.__texturesCache = {}
        self.__isDying = False

    def __del__(self):
        for url, imageID in self.__texturesCache.iteritems():
            LOG_ERROR('Image "{}" was not removed from memory (id={}). Perhaps, forgot to call "fini"'.format(url, imageID))

    @async
    def fetchImageByUrl(self, url, oneUse=True, callback=None):
        if self.__isDying:
            callback(None)
        elif url in self.__texturesCache:
            callback(getTextureLinkByID(self.__texturesCache[url]))
        else:

            def onImageData(imageData):
                if imageData and not self.__isDying:
                    imageID = mapTextureToTheMemory(imageData, temp=oneUse)
                    if not oneUse:
                        self.__texturesCache[url] = imageID
                    callback(getTextureLinkByID(imageID))
                    return
                else:
                    callback(None)
                    return

            ImageHelper.requestImageByUrl(url, onImageData)
        return

    def clearMappedImageByUrl(self, url):
        if url not in self.__texturesCache:
            LOG_WARNING('Mapped image "{}" not found!'.format(url))
        else:
            removeTextureFromMemory(self.__texturesCache[url])

    def clearAllMappedImages(self):
        for imageID in self.__texturesCache.values():
            removeTextureFromMemory(imageID)

        self.__texturesCache.clear()

    def fini(self):
        self.clearAllMappedImages()
        self.__isDying = True
