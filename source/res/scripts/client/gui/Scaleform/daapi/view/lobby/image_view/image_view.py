# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/image_view/image_view.py
import WWISE
from gui.Scaleform.daapi.view.meta.ImageViewMeta import ImageViewMeta
from gui.sounds.filters import switchHangarFilteredFilter
from gui.shared import g_eventBus
from gui.shared.events import GameEvent
_IMAGE_ROOT_PATH = '../maps/icons/imageView'

class ImageView(ImageViewMeta):

    def __init__(self, ctx=None):
        super(ImageView, self).__init__(ctx)
        self.__soundConfig = ctx['soundConfig']
        self.__image = ctx['img']

    def _populate(self):
        super(ImageView, self)._populate()
        self.setBgPath()
        switchHangarFilteredFilter(on=True)
        self.__updateSounds('entrance')

    def onClose(self):
        self.destroy()
        switchHangarFilteredFilter(on=False)
        self.__updateSounds('exit')
        g_eventBus.handleEvent(GameEvent(GameEvent.IMAGE_VIEW_DONE))

    def setBgPath(self):
        image = ''.join((_IMAGE_ROOT_PATH, '/', self.__image))
        self.flashObject.as_setBgPath(image)

    def __updateSounds(self, key):
        if self.__soundConfig is None:
            return
        else:
            actionSoundConfig = self.__soundConfig.get(key)
            if actionSoundConfig is not None:
                event = actionSoundConfig.get('event')
                state = actionSoundConfig.get('state')
                if event is not None:
                    WWISE.WW_eventGlobal(event)
                if state is not None:
                    WWISE.WW_setState(state[0], state[1])
            return
