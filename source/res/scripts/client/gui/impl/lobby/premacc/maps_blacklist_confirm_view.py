# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/maps_blacklist_confirm_view.py
import logging
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.constants.dialog_presets import DialogPresets
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_confirm_dialog_model import MapsBlacklistConfirmDialogModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_dialog_slot_model import MapsBlacklistDialogSlotModel
from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_slot_model import MapStateEnum
from gui.impl.lobby.premacc.premacc_helpers import SoundViewMixin
from gui.impl.pub.dialog_window import DialogButtons, DialogContent, DialogWindow
from gui.impl.wrappers.user_format_string_arg_model import UserFormatStringArgModel as FmtArg
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
_logger = logging.getLogger(__name__)
_UNKNOWN_MAP_ID = -1

class MapsBlacklistConfirmView(DialogWindow, SoundViewMixin):
    __appLoader = dependency.descriptor(IAppLoader)
    __slots__ = ('__mapId', '__showSelectedMaps', '__selectedMap', '__isClosing')

    def __init__(self, mapId, disabledMaps, cooldownTime, parent):
        super(MapsBlacklistConfirmView, self).__init__(content=MapsBlacklistConfirmDialogContent(mapId, disabledMaps, cooldownTime), parent=parent, enableBlur=True)
        self.__mapId = mapId
        self.__isClosing = False
        selectedMapsCount = len(disabledMaps)
        self.__showSelectedMaps = selectedMapsCount > 1
        if selectedMapsCount == 1:
            self.__selectedMap = disabledMaps[0]
        else:
            self.__selectedMap = None
        return

    def _getResultData(self):
        return self.__selectedMap

    def _initialize(self):
        self._addSoundEvent()
        super(MapsBlacklistConfirmView, self)._initialize()
        gameInputManager = self.__getGameInputManager()
        if gameInputManager is not None:
            gameInputManager.addEscapeListener(self._onClosed)
        self.contentViewModel.selectedMaps.onItemClicked += self.__onMapSelected
        with self.viewModel.transaction() as model:
            self._addButton(DialogButtons.SUBMIT, R.strings.premacc.mapsBlacklistConfim.submit(), isFocused=True, isEnabled=not self.__showSelectedMaps)
            self._addButton(DialogButtons.CANCEL, R.strings.premacc.mapsBlacklistConfim.cancel(), invalidateAll=True)
            self._setPreset(DialogPresets.MAPS_BLACKLIST)
            mapNameDyn = R.strings.arenas.num(self.__mapId)
            if self.__showSelectedMaps:
                model.setTitle(R.strings.premacc.mapsBlacklistReplace.title())
            else:
                model.setTitle(R.strings.premacc.mapsBlacklistConfim.title())
                if mapNameDyn.isValid():
                    titleArgs = model.getTitleFmtArgs()
                    titleArgs.addViewModel(FmtArg(backport.text(mapNameDyn.name()), 'mapName'))
                    titleArgs.invalidate()
        return

    def _finalize(self):
        gameInputManager = self.__getGameInputManager()
        if gameInputManager is not None:
            gameInputManager.removeEscapeListener(self._onClosed)
        self.contentViewModel.selectedMaps.onItemClicked -= self.__onMapSelected
        super(MapsBlacklistConfirmView, self)._finalize()
        self._removeSoundEvent()
        return

    def _onClosed(self, _=None):
        if self.__isClosing:
            return
        else:
            self.__isClosing = True
            cancelButton = self._getButton(DialogButtons.CANCEL)
            if cancelButton is not None:
                self._onButtonClick(cancelButton)
            else:
                super(MapsBlacklistConfirmView, self)._onClosed()
            return

    def __getGameInputManager(self):
        app = self.__appLoader.getApp()
        return app.gameInputManager if app is not None else None

    def __onMapSelected(self, event):
        selectedIdx = event.get('index', _UNKNOWN_MAP_ID)
        if selectedIdx < 0:
            return
        for i, mapModel in enumerate(self.contentViewModel.selectedMaps.getItems()):
            if i == selectedIdx:
                self.__selectedMap = mapModel.getMapId()
                break

        self._setButtonEnabled(DialogButtons.SUBMIT, True)


class MapsBlacklistConfirmDialogContent(DialogContent):
    __slots__ = ('__mapId', '__disabledMaps', '__cooldownTime')

    def __init__(self, mapId, disabledMaps, cooldownTime):
        settings = ViewSettings(R.views.lobby.premacc.maps_blacklist.maps_blacklist_confirm_dialog.MapsBlacklistConfirmDialogContent())
        settings.model = MapsBlacklistConfirmDialogModel()
        super(MapsBlacklistConfirmDialogContent, self).__init__(settings)
        self.__mapId = mapId
        self.__disabledMaps = disabledMaps
        self.__cooldownTime = cooldownTime

    def _initialize(self):
        super(MapsBlacklistConfirmDialogContent, self)._initialize()
        self.getViewModel().selectedMaps.onItemClicked += self.__onMapSelected
        with self.getViewModel().transaction() as model:
            model.setMapId(self.__mapId)
            model.setCooldownTime(self.__cooldownTime)
            showSelectedMaps = len(self.__disabledMaps) > 1
            model.setShowSelectedMaps(showSelectedMaps)
            if not showSelectedMaps:
                return
            selectedMapsModel = model.selectedMaps.getItems()
            for mapName in self.__disabledMaps:
                slotModel = MapsBlacklistDialogSlotModel()
                slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_ACTIVE_NO_HOVER)
                slotModel.setMapId(mapName)
                slotModel.setIsResizable(True)
                selectedMapsModel.addViewModel(slotModel)

    def _finalize(self):
        self.getViewModel().selectedMaps.onItemClicked -= self.__onMapSelected
        super(MapsBlacklistConfirmDialogContent, self)._finalize()

    def __onMapSelected(self, event):
        selectedIdx = event.get('index', _UNKNOWN_MAP_ID)
        if selectedIdx < 0:
            return
        with self.getViewModel().transaction() as model:
            for i, mapModel in enumerate(model.selectedMaps.getItems()):
                if i == selectedIdx:
                    mapModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_SELECTED)
                mapModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_ACTIVE_NO_HOVER)
