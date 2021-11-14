# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/mixins.py
import typing
from frameworks.wulf import WindowLayer
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.managers import ContainerManager
_LAYERS = [WindowLayer.FULLSCREEN_WINDOW,
 WindowLayer.CURSOR,
 WindowLayer.WAITING,
 WindowLayer.SERVICE_LAYOUT]

class LayerVisibilityMixin(object):

    def __init__(self, *args, **kwargs):
        super(LayerVisibilityMixin, self).__init__(*args, **kwargs)
        self.__previouslyVisibleLayers = None
        return

    def _populate(self):
        super(LayerVisibilityMixin, self)._populate()
        containerManager = self.app.containerManager
        self.__previouslyVisibleLayers = containerManager.getVisibleLayers()
        containerManager.setVisibleLayers(_LAYERS)

    def _dispose(self):
        super(LayerVisibilityMixin, self)._dispose()
        containerManager = self.app.containerManager
        containerManager.setVisibleLayers(self.__previouslyVisibleLayers)
        self.__previouslyVisibleLayers = None
        return
