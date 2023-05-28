# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collection/collection_item_preview.py
from functools import partial
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from shared_utils import first
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewSettings, WindowFlags
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.collection.collections_helpers import getItemInfo, showCollectionStylePreview, getVehicleForStyleItem
from gui.collection.sounds import COLLECTIONS_SOUND_SPACE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.collection.collection_item_preview_model import CollectionItemPreviewModel, ItemType
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared.event_dispatcher import showHangar, showCollectionWindow
from gui.sounds.filters import switchHangarOverlaySoundFilter
from helpers import dependency
from items.components.c11n_components import splitIntDescr
from items.components.c11n_constants import CustomizationType
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import ICollectionsSystemController
from skeletons.gui.impl import IGuiLoader

class CollectionItemPreview(ViewImpl):
    __slots__ = ('__itemId', '__collectionId', '__page', '__collection', '__backCallback', '__backBtnText')
    _COMMON_SOUND_SPACE = COLLECTIONS_SOUND_SPACE
    __appLoader = dependency.descriptor(IAppLoader)
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID, itemId, collectionId, page, backCallback, backBtnText):
        settings = ViewSettings(layoutID)
        settings.model = CollectionItemPreviewModel()
        self.__itemId = itemId
        self.__collectionId = collectionId
        self.__page = page
        self.__collection = self.__collectionsSystem.getCollection(collectionId)
        self.__backCallback = backCallback
        self.__backBtnText = backBtnText
        super(CollectionItemPreview, self).__init__(settings)

    def _onLoading(self, *args, **kwargs):
        super(CollectionItemPreview, self)._onLoading(*args, **kwargs)
        switchHangarOverlaySoundFilter(on=True)
        name, itemType, description, largeImage, mediumImage, smallImage = getItemInfo(self.__itemId, self.__collectionId)
        with self.viewModel.transaction() as tx:
            tx.setName(name)
            tx.setType(itemType)
            tx.setDescription(description)
            tx.setLargeImage(largeImage)
            tx.setMediumImage(mediumImage)
            tx.setSmallImage(smallImage)
            tx.setCurrentCollection(self.__collection.name)
            tx.setPage(self.__page)
            if itemType == ItemType.STYLE3D:
                self.__fillVehicleInfo(model=tx)

    def _finalize(self):
        switchHangarOverlaySoundFilter(on=False)
        super(CollectionItemPreview, self)._finalize()

    @property
    def viewModel(self):
        return super(CollectionItemPreview, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClosePreview, self.__onClosePreview),
         (self.viewModel.onOpenPreview, self.__onOpenPreview),
         (self.__collectionsSystem.onServerSettingsChanged, self.__onSettingsChanged),
         (g_playerEvents.onDisconnected, self.__onDisconnected))

    @replaceNoneKwargsModel
    def __fillVehicleInfo(self, model=None):
        item = self.__collectionsSystem.getCollectionItem(self.__collectionId, self.__itemId)
        vehicle = getVehicleForStyleItem(item)
        if vehicle is not None:
            fillVehicleInfo(model.vehicleInfo, vehicle)
        return

    def __onClosePreview(self):
        self.destroyWindow()

    def __onOpenPreview(self, args):
        page = int(args.get('currentPage'))
        item = self.__collectionsSystem.getCollectionItem(self.__collectionId, self.__itemId)
        if item.type == 'customizationItem':
            itemType, _ = splitIntDescr(item.relatedId)
            if itemType == CustomizationType.STYLE:
                self.__openStylePreview(item.relatedId, page)

    def __openStylePreview(self, itemCD, page):
        showCollectionStylePreview(itemCD, _getPreviewCallback(self.__appLoader, self.__collection.collectionId, page, self.__backCallback, self.__backBtnText), backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.collections()))
        self.__backCallback = None
        self.destroyWindow()
        collectionLayoutID = R.views.lobby.collection.CollectionView()
        collectionView = first(self.__guiLoader.windowsManager.findViews(lambda v: v.layoutID == collectionLayoutID))
        if collectionView is not None:
            collectionView.destroyWindow()
        return

    def __onSettingsChanged(self):
        if not self.__collectionsSystem.isEnabled():
            showHangar()
            self.destroyWindow()

    def __onDisconnected(self):
        self.destroyWindow()


class CollectionItemPreviewWindow(WindowImpl):

    def __init__(self, itemId, collectionId, page, backCallback, backBtnText):
        super(CollectionItemPreviewWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=CollectionItemPreview(R.views.lobby.collection.CollectionItemPreview(), itemId, collectionId, page, backCallback, backBtnText), parent=None)
        return


def _getPreviewCallback(appLoader, collectionId, page, backCallback, backBtnText):

    def backToCollections(appLoader, collectionId, page, backCallback, backBtnText):
        containerManager = appLoader.getApp().containerManager
        stylePreview = first((containerManager.getViewByKey(ViewKey(viewAlias)) for viewAlias in (VIEW_ALIAS.STYLE_PREVIEW, VIEW_ALIAS.STYLE_PROGRESSION_PREVIEW)))
        if stylePreview is not None:
            stylePreview.destroy()
        showCollectionWindow(collectionId, page, backCallback or showHangar, backBtnText)
        return

    return partial(backToCollections, appLoader, collectionId, page, backCallback, backBtnText)
