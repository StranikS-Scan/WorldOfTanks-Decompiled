# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/collection/collection_entry_point.py
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus
from gui.Scaleform.daapi.view.meta.CollectionEntryPointMeta import CollectionEntryPointMeta
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.views.lobby.collection.collection_entry_point_model import CollectionEntryPointModel, CollectionState
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showCollectionWindow
from helpers import dependency
from helpers.time_utils import getTimestampByStrDate
from skeletons.gui.game_control import ICollectionsSystemController

@dependency.replace_none_kwargs(collectionsController=ICollectionsSystemController)
def isCollectionEntryPointAvailable(data, collectionsController=None):
    return collectionsController.getCollection(data.get('collectionId', None)) is not None


@dependency.replace_none_kwargs(collectionsController=ICollectionsSystemController)
def getCurrentCollectionState(collectionId, collectionsController=None):
    if not collectionsController.isEnabled():
        return CollectionState.DISABLED
    return CollectionState.COMPLETED if collectionsController.isCollectionCompleted(collectionId) else CollectionState.ACTIVE


class CollectionEntryPoint(CollectionEntryPointMeta):
    __slots__ = ('__collectionData', '__view')

    def __init__(self):
        super(CollectionEntryPoint, self).__init__()
        self.__view = None
        self.__collectionData = None
        return

    def setData(self, data):
        self.__collectionData = {'collectionId': data.get('collectionId', None),
         'eventEndDate': getTimestampByStrDate(data['collectionEventEndDate']) if 'collectionEventEndDate' in data else 0}
        if self.__view is not None:
            self.__view.setCollectionData(self.__collectionData)
        return

    def _makeInjectView(self):
        self.__view = CollectionEntryPointView(flags=ViewFlags.VIEW)
        if self.__collectionData is not None:
            self.__view.setCollectionData(self.__collectionData)
        return self.__view


class CollectionEntryPointView(ViewImpl):
    __slots__ = ('__collectionId', '__eventEndDate')
    __collectionsController = dependency.descriptor(ICollectionsSystemController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.collection.CollectionEntryPointView())
        settings.flags = flags
        settings.model = CollectionEntryPointModel()
        super(CollectionEntryPointView, self).__init__(settings)
        self.__collectionId = None
        self.__eventEndDate = 0
        return

    @property
    def viewModel(self):
        return super(CollectionEntryPointView, self).getViewModel()

    def setCollectionData(self, collectionData):
        self.__collectionId = collectionData['collectionId']
        self.__eventEndDate = collectionData['eventEndDate']
        if self.viewStatus in (ViewStatus.LOADING, ViewStatus.LOADED):
            self.__update()

    def _onLoading(self, *args, **kwargs):
        super(CollectionEntryPointView, self)._onLoading(*args, **kwargs)
        self.__update()

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onClick),
         (self.__collectionsController.onAvailabilityChanged, self.__update),
         (self.__collectionsController.onServerSettingsChanged, self.__onSettingsChanged),
         (self.__collectionsController.onBalanceUpdated, self.__update))

    def _getListeners(self):
        return ((events.CollectionsEvent.NEW_ITEM_SHOWN, self.__update, EVENT_BUS_SCOPE.LOBBY),)

    def __setViewModel(self, collection):
        with self.viewModel.transaction() as tx:
            tx.setFinishDateStamp(self.__eventEndDate)
            tx.setCollectionName(collection.name)
            tx.setState(getCurrentCollectionState(self.__collectionId))
            tx.setNewReceivedItems(self.__collectionsController.getNewLinkedCollectionsItemCount(self.__collectionId))

    def __setDefaultViewModel(self):
        with self.viewModel.transaction() as tx:
            tx.setFinishDateStamp(0)
            tx.setCollectionName('')
            tx.setState(CollectionState.DISABLED)
            tx.setNewReceivedItems(0)

    def __update(self, *_):
        if self.__collectionId is None:
            self.__setDefaultViewModel()
            return
        else:
            collection = self.__collectionsController.getCollection(self.__collectionId)
            if collection is not None:
                self.__setViewModel(collection)
            else:
                self.__setDefaultViewModel()
            return

    def __onClick(self):
        if self.__collectionsController.isEnabled():
            backText = backport.text(R.strings.menu.viewHeader.backBtn.descrLabel.hangar())
            showCollectionWindow(collectionId=self.__collectionId, backBtnText=backText)

    def __onSettingsChanged(self):
        if self.__collectionId is not None:
            collection = self.__collectionsController.getCollection(self.__collectionId)
            if collection is None and self.viewStatus == ViewStatus.LOADED:
                self.destroyWindow()
            else:
                self.__update()
        return
