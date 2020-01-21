# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/image_view/image_view.py
import WWISE
from gui.Scaleform.daapi.view.meta.ImageViewMeta import ImageViewMeta
from gui.sounds.filters import STATE_HANGAR_FILTERED
_IMAGE_ROOT_PATH = '../maps/icons/imageView'

class ImageView(ImageViewMeta):

    def __init__(self, ctx=None):
        super(ImageView, self).__init__(ctx)
        self.__image = ctx['img']

    def _populate(self):
        super(ImageView, self)._populate()
        self.setBgPath()
        WWISE.WW_setState(STATE_HANGAR_FILTERED, '{}_on'.format(STATE_HANGAR_FILTERED))

    def onClose(self):
        self.destroy()
        WWISE.WW_setState(STATE_HANGAR_FILTERED, '{}_off'.format(STATE_HANGAR_FILTERED))

    def setBgPath(self):
        image = ''.join((_IMAGE_ROOT_PATH, '/', self.__image))
        self.flashObject.as_setBgPath(image)
