# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mapbox/map_box_intro.py
from constants import Configs
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_intro_model import MapBoxIntroModel
from gui.impl.lobby.mapbox.sound import getMapboxViewSoundSpace
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
from gui.server_events.events_dispatcher import showMissionsMapboxProgression
from gui.shared.event_dispatcher import showModeSelectorWindow
from gui.shared.utils import SelectorBattleTypesUtils
from helpers import dependency, server_settings, time_utils
from skeletons.gui.game_control import IMapboxController
from skeletons.gui.lobby_context import ILobbyContext

class MapBoxIntro(ViewImpl, IGlobalListener):
    __slots__ = ('__closeCallback',)
    _COMMON_SOUND_SPACE = getMapboxViewSoundSpace()
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.mapbox.MapBoxIntro())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = MapBoxIntroModel()
        self.__closeCallback = kwargs.get('closeCallback')
        super(MapBoxIntro, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MapBoxIntro, self).getViewModel()

    def onPrbEntitySwitched(self):
        self.destroyWindow()

    def _initialize(self):
        super(MapBoxIntro, self)._initialize()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.__onPrimeTimeChanged
        self.viewModel.onClose += self.__onClose
        self.startGlobalListening()

    def _finalize(self):
        self.stopGlobalListening()
        self.viewModel.onClose -= self.__onClose
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.__onPrimeTimeChanged
        super(MapBoxIntro, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        self.__updateViewModel()

    def __onPrimeTimeChanged(self, *_):
        self.__updateViewModel()

    @server_settings.serverSettingsChangeListener(Configs.MAPBOX_CONFIG.value)
    def __onServerSettingsChanged(self, _):
        if not self.__mapboxCtrl.getModeSettings().isEnabled:
            self.destroyWindow()
            return
        self.__updateViewModel()

    def __updateViewModel(self):
        nextSeason = self.__mapboxCtrl.getNextSeason()
        actualSeason = self.__mapboxCtrl.getCurrentSeason() or nextSeason
        if actualSeason is None:
            return
        else:
            with self.getViewModel().transaction() as model:
                model.setIsActive(self.__mapboxCtrl.isActive())
                if not self.__mapboxCtrl.isActive() and nextSeason is not None:
                    model.setDate(time_utils.makeLocalServerTime(nextSeason.getStartDate()))
                model.setSeasonNumber(actualSeason.getNumber())
            return

    def __onClose(self):
        self.destroyWindow()
        if not SelectorBattleTypesUtils.isKnownBattleType(SELECTOR_BATTLE_TYPES.MAPBOX):
            SelectorBattleTypesUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.MAPBOX)
        if self.__closeCallback is not None:
            self.__closeCallback()
        elif not self.__mapboxCtrl.isActive():
            showModeSelectorWindow(False)
        else:
            showMissionsMapboxProgression()
        return
