# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_playlists_presenter.py
from __future__ import absolute_import
import logging
from BWUtil import AsyncReturn
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicle_playlists_model import VehiclePlaylistsModel
from gui.impl.lobby.hangar.dialogs.vehicle_playlists import showTypeParamPlaylistDialog
from gui.impl.lobby.hangar.playlists_states import EditVehiclePlaylistsState
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.game_control import IVehiclePlaylistsController
from wg_async import wg_async, BrokenPromiseError
from gui.shared.event_dispatcher import showVehicleHubOverview
from gui.Scaleform.lobby_entry import getLobbyStateMachine
_logger = logging.getLogger(__name__)

class VehiclePlaylistsPresenter(ViewComponent[VehiclePlaylistsModel]):
    __vehiclePlaylistsCtrl = dependency.descriptor(IVehiclePlaylistsController)

    def __init__(self):
        super(VehiclePlaylistsPresenter, self).__init__(model=VehiclePlaylistsModel)
        self.__dialogFuture = None
        return

    def _onLoading(self, *args, **kwargs):
        super(VehiclePlaylistsPresenter, self)._onLoading(*args, **kwargs)
        self.__refillModel()

    def _finalize(self):
        self.__closeDialog()
        super(VehiclePlaylistsPresenter, self)._finalize()

    def _getEvents(self):
        vm = self.getViewModel()
        return ((vm.onSelect, self.__onSelectPlaylist),
         (vm.onCreate, self.__onCreatePlaylist),
         (vm.onModify, self.__onModifyPlaylist),
         (vm.onDelete, self.__onDeletePlaylist),
         (vm.onSave, self.__onSavePlaylist),
         (vm.onDiscard, self.__onDiscardAndExit),
         (vm.onSetDirtyEdit, self.__onDirtyEditFlagChanged),
         (vm.openImportConfirm, self.__onOpenImportConfirm),
         (vm.openDeleteConfirm, self.__onOpenDeleteConfirm),
         (vm.onGoToAboutVehicle, self.__onGoToAboutVehicle),
         (self.__vehiclePlaylistsCtrl.onEnabledStatusChanged, self.__onEnabledStatusChanged),
         (self.__vehiclePlaylistsCtrl.onModifiedPlaylistDiscarded, self.__onModifiedPlaylistDiscarded),
         (self.__vehiclePlaylistsCtrl.onDirtyClean, self.__onDirtyClean),
         (self.__vehiclePlaylistsCtrl.onPlaylistSaved, self.__onPlaylistSaved))

    def __onEnabledStatusChanged(self, _):
        self.__refillModel()
        if not self.__vehiclePlaylistsCtrl.isEnabled:
            self.__closeDialog()

    def __refillModel(self):
        with self.getViewModel().transaction() as vm:
            vm.setSelectedID(self.__vehiclePlaylistsCtrl.getSelectedID())
            vm.setEnabled(self.__vehiclePlaylistsCtrl.isEnabled)
            vm.setDirtyEdit(self.__vehiclePlaylistsCtrl.isModifiedPlaylistChanged)
            storage = vm.getStorage()
            storage.clear()
            for pId, pStrData in self.__vehiclePlaylistsCtrl.iterPlaylists():
                storage.set(pId, pStrData)

    def __onCreatePlaylist(self, ctx):
        self.__performPlaylistCreation(playlistID=ctx.get('id'), playlistData=ctx.get('data'))

    def __onModifyPlaylist(self, ctx):
        plStrID = ctx.get('id', '')
        plData = ctx.get('data', '')
        if self.__vehiclePlaylistsCtrl.updateModifiedPlaylist(plStrID, playlistData=plData):
            with self.getViewModel().transaction() as vm:
                storage = vm.getStorage()
                storage.set(plStrID, plData)

    def __onDirtyEditFlagChanged(self, ctx):
        dirtyEdit = ctx.get('value')
        if dirtyEdit is None:
            _logger.warning('Dirty Edit Flag has not been passed!')
            return
        else:
            self.__vehiclePlaylistsCtrl.setModifiedPlaylistChanged(dirtyEdit)
            self.getViewModel().setDirtyEdit(self.__vehiclePlaylistsCtrl.isModifiedPlaylistChanged)
            return

    def __onSelectPlaylist(self, ctx):
        plID = ctx.get('id', '')
        if self.__vehiclePlaylistsCtrl.setSelectedID(plID):
            vm = self.getViewModel()
            vm.setSelectedID(plID)

    def __onPlaylistSaved(self, playlistID, playlist):
        with self.getViewModel().transaction() as vm:
            vm.setSelectedID(playlistID)
            vm.setDirtyEdit(self.__vehiclePlaylistsCtrl.isModifiedPlaylistChanged)
            storage = vm.getStorage()
            storage.set(playlistID, playlist)

    def __onSavePlaylist(self, *_, **__):
        savedPlaylist = self.__vehiclePlaylistsCtrl.saveModifiedPlaylist()
        if not savedPlaylist:
            return
        playlistStrID, playlistData = savedPlaylist
        self.__vehiclePlaylistsCtrl.clearModifiedPlaylist()
        self.__vehiclePlaylistsCtrl.setInitialModifiedPlaylist(playlistStrID, playlistData)

    def __onDiscardAndExit(self, *_, **__):
        self.__goBack()

    def __onDeletePlaylist(self, ctx):
        self.__performPlaylistDeletion(playlistID=ctx.get('id', ''))

    def __onOpenImportConfirm(self, ctx):
        self.__showImportConfirmDialog(dialogType=ctx.get('type', ''), dialogParams=ctx.get('params', ''))

    def __onOpenDeleteConfirm(self, ctx):
        self.__showDeleteConfirmDialog(playlistID=ctx.get('id', ''), dialogType=ctx.get('type', ''), dialogParams=ctx.get('params', ''))

    def __closeDialog(self):
        if self.__dialogFuture is not None:
            self.__dialogFuture.cancel()
        return

    @wg_async
    def __showParamDialog(self, dialogType, dialogParams):
        _logger.debug('Shows dialog %r.', dialogType)
        try:
            if self.__dialogFuture is not None:
                _logger.warning('Recreate dialog to %r. Abort previous.', dialogType)
                self.__dialogFuture.cancel()
            self.__dialogFuture = showTypeParamPlaylistDialog(dialogType, dialogParams)
            _, result = yield self.__dialogFuture
            raise AsyncReturn(result)
        finally:
            self.__dialogFuture = None

        return

    @wg_async
    def __showImportConfirmDialog(self, dialogType, dialogParams):
        try:
            result = yield self.__showParamDialog(dialogType, dialogParams)
            if result is None:
                return
            if 'action' in result and result['action'] == 'import':
                self.__performPlaylistCreation(playlistID=result.get('id'), playlistData=result.get('data'))
        except BrokenPromiseError:
            _logger.debug('Import dialog %r cancelled.', dialogType)

        return

    @wg_async
    def __showDeleteConfirmDialog(self, playlistID, dialogType, dialogParams):
        result = yield self.__showParamDialog(dialogType, dialogParams)
        if result is not None:
            action = result.get('action')
            if action == 'delete':
                self.__performPlaylistDeletion(playlistID)
                self.__goBack()
        return

    def __goBack(self):
        state = getLobbyStateMachine().getStateFromView(self.getParentView())
        if state is not None:
            state.goBack()
        return

    def __performPlaylistDeletion(self, playlistID):
        if self.__vehiclePlaylistsCtrl.deletePlaylist(playlistID):
            with self.getViewModel().transaction() as vm:
                if playlistID == vm.getSelectedID():
                    vm.setSelectedID(self.__vehiclePlaylistsCtrl.getSelectedID())
                    isModifyingListChanged = False
                    vm.setDirtyEdit(isModifyingListChanged)
                    self.__vehiclePlaylistsCtrl.setModifiedPlaylistChanged(isModifyingListChanged)
                storage = vm.getStorage()
                del storage[playlistID]

    def __performPlaylistCreation(self, playlistID, playlistData):
        if self.__vehiclePlaylistsCtrl.createPlaylist(plStrID=playlistID, playlistData=playlistData):
            if self.__vehiclePlaylistsCtrl.updateModifiedPlaylist(plStrID=playlistID, playlistData=playlistData):
                with self.getViewModel().transaction() as vm:
                    vm.setSelectedID(playlistID)
                    isModifyingListChanged = False
                    self.__vehiclePlaylistsCtrl.setModifiedPlaylistChanged(isModifyingListChanged)
                    vm.setDirtyEdit(isModifyingListChanged)
                    storage = vm.getStorage()
                    storage.set(playlistID, playlistData)
                EditVehiclePlaylistsState.goTo(id=playlistID, new=True)

    def __onModifiedPlaylistDiscarded(self, playlistStrID, playlistData):
        with self.getViewModel().transaction() as vm:
            vm.setDirtyEdit(False)
            storage = vm.getStorage()
            storage.set(playlistStrID, playlistData)

    def __onGoToAboutVehicle(self, args):
        showVehicleHubOverview(int(args.get('intCD')))

    def __onDirtyClean(self):
        with self.getViewModel().transaction() as vm:
            vm.setDirtyEdit(False)
