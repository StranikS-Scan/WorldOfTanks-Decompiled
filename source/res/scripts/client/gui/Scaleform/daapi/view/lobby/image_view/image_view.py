# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/image_view/image_view.py
from gui.impl.lobby.common.sound_constants import HANGAR_FILTERED_SOUND_SPACE
from gui.Scaleform.daapi.view.meta.ImageViewMeta import ImageViewMeta
_IMAGE_ROOT_PATH = '../maps/icons/imageView'

class ImageView(ImageViewMeta):
    _COMMON_SOUND_SPACE = HANGAR_FILTERED_SOUND_SPACE

    def __init__(self, ctx=None):
        super(ImageView, self).__init__(ctx)
        self.__image = ctx['img']

    def _populate(self):
        super(ImageView, self)._populate()
        self.setBgPath()

    def onClose(self):
        self.destroy()

    def setBgPath(self):
        image = ''.join((_IMAGE_ROOT_PATH, '/', self.__image))
        self.flashObject.as_setBgPath(image)
