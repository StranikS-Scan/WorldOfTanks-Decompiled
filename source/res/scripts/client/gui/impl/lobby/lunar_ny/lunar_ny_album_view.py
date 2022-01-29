# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/lunar_ny/lunar_ny_album_view.py
from adisp import process
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.views.lobby.lunar_ny.charm_model import CharmModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.main_view.album.album_model import AlbumModel
from gui.impl.lobby.lunar_ny.lunar_ny_base_main_view_component import BaseLunarNYViewComponent
from gui.impl.lobby.lunar_ny.tooltips.charm_tooltip import CharmTooltip
from gui.impl.gen import R
from helpers import dependency
from lunar_ny.lunar_ny_sounds import LUNAR_NY_ALBUM_SOUND_SPACE
from skeletons.gui.shared import IItemsCache
from items.components.lunar_ny_constants import INVALID_CHARM_ID
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_processor import FillAlbumSlotProcessor
from lunar_ny_common.settings_constants import LUNAR_NY_PDATA_KEY
from lunar_ny.lunar_ny_processor import SeenAllCharmsProcessor
from gui.impl.lobby.lunar_ny.lunar_ny_helpers import showSelectCharmView
from gui.impl.lobby.lunar_ny.lunar_ny_model_helpers import updateCharmModel

class LunarNYAlbumView(BaseLunarNYViewComponent[AlbumModel]):
    __slots__ = ('__selectCharmViewIsVisited',)
    __lunarController = dependency.descriptor(ILunarNYController)
    __itemsCache = dependency.descriptor(IItemsCache)
    _SOUND_SPACE_SETTINGS = LUNAR_NY_ALBUM_SOUND_SPACE

    def __init__(self, viewModel, view):
        super(LunarNYAlbumView, self).__init__(viewModel, view)
        self.__selectCharmViewIsVisited = False

    def setActive(self, isActive):
        super(LunarNYAlbumView, self).setActive(isActive)
        self.__updateNewCharms()
        if isActive:
            self.__updateCharms()
        elif self.__selectCharmViewIsVisited:
            self.__markAllCharmsAsSeen()

    def _addListeners(self):
        super(LunarNYAlbumView, self)._addListeners()
        self._viewModel.onSlotClick += self.__onSlotClick
        self._viewModel.onRemoveCharm += self.__onRemoveCharm
        g_clientUpdateManager.addCallback(LUNAR_NY_PDATA_KEY, self.__onClientUpdated)

    def _removeListeners(self):
        self._viewModel.onSlotClick -= self.__onSlotClick
        self._viewModel.onRemoveCharm -= self.__onRemoveCharm
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(LunarNYAlbumView, self)._removeListeners()

    def finalize(self):
        if self.__selectCharmViewIsVisited:
            self.__markAllCharmsAsSeen()
        super(LunarNYAlbumView, self).finalize()

    def createToolTipContent(self, event, contentID):
        return CharmTooltip(charmID=event.getArgument('charmID')) if contentID == R.views.lobby.lunar_ny.CharmTooltip() else super(LunarNYAlbumView, self).createToolTipContent(event, contentID)

    @process
    def __markAllCharmsAsSeen(self):
        self.__selectCharmViewIsVisited = False
        charms = self.__itemsCache.items.lunarNY.getCharms().values()
        newCharms = []
        for charm in charms:
            if charm is not None and charm.getUnseenCount() > 0:
                newCharms.append(charm.getID())

        if newCharms:
            yield SeenAllCharmsProcessor(newCharms).request()
        return

    def __updateCharms(self):
        charmsInSlots = self.__lunarController.charms.getCharmsInSlots()
        charms = self._viewModel.getCharmsInSlots()
        charms.clear()
        emptyCharmModel = CharmModel()
        emptyCharmModel.setCharmID(INVALID_CHARM_ID)
        for charm in charmsInSlots:
            if charm is not None:
                charmModel = CharmModel()
                updateCharmModel(charm, charmModel)
                charms.addViewModel(charmModel)
            charms.addViewModel(emptyCharmModel)

        charms.invalidate()
        self._viewModel.setCountCharmsInStorage(self.__lunarController.charms.getCountCharms())
        return

    def __updateNewCharms(self):
        countNewCharms = 0
        charms = self.__itemsCache.items.lunarNY.getCharms()
        for charm in charms.values():
            countNewCharms += charm.getUnseenCount()

        self._viewModel.setCountNewCharms(countNewCharms)

    def __onClientUpdated(self, _):
        self.__updateNewCharms()
        if self._isActive:
            self.__updateCharms()

    def __onSlotClick(self, args):
        slotIdx = args.get('slotIdx')
        showSelectCharmView(slotIdx, self._mainViewRef.getParentWindow())
        self.__selectCharmViewIsVisited = True

    @process
    def __onRemoveCharm(self, args):
        slotID = args.get('slotIdx')
        yield FillAlbumSlotProcessor(INVALID_CHARM_ID, slotID).request()
