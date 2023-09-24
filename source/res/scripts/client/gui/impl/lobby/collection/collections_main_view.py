# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collection/collections_main_view.py
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus
from gui.Scaleform.daapi.view.lobby.profile.sound_constants import ACHIEVEMENTS_SOUND_SPACE
from gui.collection.account_settings import isCompletedCollectionShown, isIntroShown, isNewCollection, getLastShownCollectionBalance, resetCollectionsTabCounter, setCollectionsUpdatedEntrySeen, setLastShownCollectionBalance, setLastShownNewCollection, setShownCompletedCollection
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.collection.collection_model import CollectionModel
from gui.impl.gen.view_models.views.lobby.collection.collections_main_view_model import CollectionsMainViewModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showCollectionWindow, showCollectionsMainPage, showHangar
from helpers import dependency
from skeletons.gui.game_control import ICollectionsSystemController
from skeletons.gui.impl import IGuiLoader

class CollectionsMainView(ViewImpl):
    __slots__ = ('__wasFirstActivation',)
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)
    __guiLoader = dependency.descriptor(IGuiLoader)
    _COMMON_SOUND_SPACE = ACHIEVEMENTS_SOUND_SPACE

    def __init__(self):
        settings = ViewSettings(R.views.lobby.collection.CollectionsMainView())
        settings.flags = ViewFlags.VIEW
        settings.model = CollectionsMainViewModel()
        self.__wasFirstActivation = False
        super(CollectionsMainView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CollectionsMainView, self).getViewModel()

    def activate(self):
        if not self.__wasFirstActivation:
            self.__wasFirstActivation = True
        else:
            with self.viewModel.transaction() as model:
                self.__updateData(model=model)
                self.__setIsViewActive(True, model=model)
            self._subscribe()
        resetCollectionsTabCounter(collectionsSystem=self.__collectionsSystem)

    def deactivate(self):
        self._unsubscribe()
        if self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            self.__setIsViewActive(False)

    def _finalize(self):
        g_eventBus.removeListener(events.CollectionsEvent.COLLECTION_VIEW_CLOSED, self.__onCollectionViewClosed, EVENT_BUS_SCOPE.LOBBY)
        super(CollectionsMainView, self)._finalize()

    def _getEvents(self):
        return ((self.__collectionsSystem.onServerSettingsChanged, self.__onSettingsChanged),
         (self.__collectionsSystem.onBalanceUpdated, self.__onBalanceUpdated),
         (self.viewModel.onOpenCollection, self.__openCollection),
         (self.viewModel.onClose, self.__close),
         (self.viewModel.setCompletionWasShown, self.__setCompletionShown),
         (self.viewModel.onSetNewCollectionShown, self.__setShownNewCollection))

    def _getListeners(self):
        return ((events.CollectionsEvent.COLLECTION_INTRO_CLOSED, self.__onIntroViewClosed, EVENT_BUS_SCOPE.LOBBY),)

    def _onLoading(self, *args, **kwargs):
        super(CollectionsMainView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateData(model=model)
            self.__setIsViewActive(True, model=model)

    def _onLoaded(self, *args, **kwargs):
        setCollectionsUpdatedEntrySeen()

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        self.__fillCollections(model=model)

    @replaceNoneKwargsModel
    def __setIsViewActive(self, isActive, model=None):
        model.setIsViewActive(isActive)

    @replaceNoneKwargsModel
    def __fillCollections(self, model=None):
        collections = model.getCollections()
        collections.clear()
        for collectionID, collection in self.__collectionsSystem.getCollections(reverseSort=True).iteritems():
            if isNewCollection(collectionID, collectionsSystem=self.__collectionsSystem) and self.__isIntroViewOpen():
                continue
            collectionModel = CollectionModel()
            self.__fillCollection(collectionModel, collectionID, collection)
            collections.addViewModel(collectionModel)

        collections.invalidate()

    def __fillCollection(self, collectionModel, collectionID, collection):
        isIntroOpen = self.__isIntroViewOpen()
        collectionModel.setCollectionId(collectionID)
        collectionModel.setName(collection.name)
        collectionModel.setYear(collection.year)
        collectionModel.setIsActive(collection.isActive)
        collectionModel.setIsNew(isNewCollection(collectionID, collectionsSystem=self.__collectionsSystem) and not isIntroOpen)
        itemCount = self.__collectionsSystem.getReceivedProgressItemCount(collectionID)
        collectionModel.setItemCount(itemCount if not isIntroOpen else getLastShownCollectionBalance(collectionID))
        collectionModel.setMaxCount(self.__collectionsSystem.getMaxProgressItemCount(collectionID))
        collectionModel.setCompletionWasShown(isCompletedCollectionShown(collectionID))
        setLastShownCollectionBalance(collectionID, itemCount)

    def __onSettingsChanged(self):
        if not self.__collectionsSystem.isEnabled():
            showHangar()
            self.destroyWindow()
        else:
            self.__updateData()

    def __onBalanceUpdated(self):
        self.__updateData()

    def __openCollection(self, args):
        self._unsubscribe()
        g_eventBus.addListener(events.CollectionsEvent.COLLECTION_VIEW_CLOSED, self.__onCollectionViewClosed, EVENT_BUS_SCOPE.LOBBY)
        collection = self.__collectionsSystem.getCollection(int(args.get('collectionId')))
        showCollectionWindow(collection.collectionId, backBtnText=backport.text(R.strings.collections.main.backText()), backCallback=showCollectionsMainPage)

    def __setCompletionShown(self, args):
        setShownCompletedCollection(int(args.get('collectionId')))
        self.__updateData()

    def __setShownNewCollection(self, args):
        setLastShownNewCollection(int(args.get('collectionId')))
        self.__updateData()

    def __close(self):
        showHangar()
        self.destroyWindow()

    def __onCollectionViewClosed(self, *_):
        if self.viewStatus not in (ViewStatus.DESTROYING, ViewStatus.DESTROYED):
            self._subscribe()
            self.__updateData()
        g_eventBus.removeListener(events.CollectionsEvent.COLLECTION_VIEW_CLOSED, self.__onCollectionViewClosed, EVENT_BUS_SCOPE.LOBBY)

    def __onIntroViewClosed(self, *_):
        self.__updateData()

    def __isIntroViewOpen(self):

        def introViewPredicate(view):
            return view.layoutID == R.views.lobby.collection.IntroView() and view.viewStatus in (ViewStatus.CREATED, ViewStatus.LOADING, ViewStatus.LOADED)

        return bool(self.__guiLoader.windowsManager.findViews(introViewPredicate)) or not isIntroShown()
