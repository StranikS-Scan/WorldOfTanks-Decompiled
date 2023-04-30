# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collection/collection_item_preview.py
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags
from gui.collection.collections_helpers import getItemInfo
from gui.collection.sounds import COLLECTIONS_SOUND_SPACE
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.collection.collection_item_preview_model import CollectionItemPreviewModel
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.event_dispatcher import showHangar
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from skeletons.gui.game_control import ICollectionsSystemController

class CollectionItemPreview(ViewImpl):
    __slots__ = ('__itemId', '__collectionId')
    _COMMON_SOUND_SPACE = COLLECTIONS_SOUND_SPACE
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)

    def __init__(self, layoutID, itemId, collectionId):
        settings = ViewSettings(layoutID)
        settings.model = CollectionItemPreviewModel()
        self.__itemId = itemId
        self.__collectionId = collectionId
        super(CollectionItemPreview, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(CollectionItemPreview, self)._onLoading(*args, **kwargs)
        switchHangarOverlaySoundFilter(on=True)
        name, itemType, description, largeImage, smallImage = getItemInfo(self.__itemId, self.__collectionId)
        with self.viewModel.transaction() as tx:
            tx.setName(name)
            tx.setType(itemType)
            tx.setDescription(description)
            tx.setLargeImage(largeImage)
            tx.setSmallImage(smallImage)

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        super(CollectionItemPreview, self)._finalize()

    @property
    def viewModel(self):
        return super(CollectionItemPreview, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClosePreview, self.__onClosePreview), (self.__collectionsSystem.onServerSettingsChanged, self.__onSettingsChanged), (g_playerEvents.onDisconnected, self.__onDisconnected))

    def __onClosePreview(self):
        self.destroyWindow()

    def __onSettingsChanged(self):
        if not self.__collectionsSystem.isEnabled():
            showHangar()
            self.destroyWindow()

    def __onDisconnected(self):
        self.destroyWindow()


class CollectionItemPreviewWindow(WindowImpl):
    __slots__ = ('__blur',)

    def __init__(self, itemId, collectionId):
        super(CollectionItemPreviewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=CollectionItemPreview(R.views.lobby.collection.CollectionItemPreview(), itemId, collectionId), parent=None)
        self.__blur = CachedBlur(enabled=True, ownLayer=self.layer)
        return

    def _finalize(self):
        self.__blur.fini()
        super(CollectionItemPreviewWindow, self)._finalize()
