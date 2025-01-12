# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/image_view/image_view.py
from gui.Scaleform.daapi.view.meta.ImageViewMeta import ImageViewMeta
from gui.sounds.filters import switchHangarFilteredFilter
_IMAGE_ROOT_PATH = '../maps/icons/imageView'

class ImageView(ImageViewMeta):

    def __init__(self, ctx=None):
        super(ImageView, self).__init__(ctx)
        self.__image = ctx['img']

    def _populate(self):
        super(ImageView, self)._populate()
        self.setBgPath()
        switchHangarFilteredFilter(on=True)

    def onClose(self):
        self.destroy()
        switchHangarFilteredFilter(on=False)

    def setBgPath(self):
        image = ''.join((_IMAGE_ROOT_PATH, '/', self.__image))
        self.flashObject.as_setBgPath(image)
