# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/view_helpers/image_helper.py
import BigWorld
import ResMgr
from debug_utils import LOG_WARNING
from gui.shared.utils import mapTextureToTheMemory, getImageSize

def readLocalImage(path):
    data = ResMgr.openSection(path)
    return data.asBinary if data is not None else None


class ImageHelper(object):

    @staticmethod
    def getMemoryTexturePath(image):
        return mapTextureToTheMemory(image)

    @staticmethod
    def requestImageByUrl(url, size, callback, defaultGetter=None):
        defaultGetter = defaultGetter or (lambda v: None)

        def _onImageReceived(_, img):
            imgSize = getImageSize(img)
            if imgSize != size:
                LOG_WARNING('Received image has invalid size, use default instead', imgSize, size, url, type(img))
                img = defaultGetter(size)
                print img
            callback(img)

        if hasattr(BigWorld.player(), 'customFilesCache'):
            if url is not None:
                BigWorld.player().customFilesCache.get(url, _onImageReceived)
            else:
                BigWorld.callback(0.0, lambda : callback(defaultGetter(size)))
        else:
            LOG_WARNING('Trying to get image by url from non-account', url)
        return
