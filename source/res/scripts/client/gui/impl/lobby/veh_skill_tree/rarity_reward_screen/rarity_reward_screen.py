# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/veh_skill_tree/rarity_reward_screen/rarity_reward_screen.py
import SoundGroups
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.veh_skill_tree.rarity_reward_screen_model import RarityRewardScreenModel
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.sounds.filters import switchHangarOverlaySoundFilter

class RarityRewardScreen(ViewImpl):
    __slots__ = ('__element', '__sound')
    _REWARD_SOUND_ID = 'elements_cust_reward'

    def __init__(self, element):
        settings = ViewSettings(R.views.mono.lobby.veh_skill_tree.rarity_reward_screen())
        settings.flags = ViewFlags.VIEW
        settings.model = RarityRewardScreenModel()
        super(RarityRewardScreen, self).__init__(settings)
        self.__element = element
        self.__sound = None
        return

    @property
    def viewModel(self):
        return super(RarityRewardScreen, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, *args, **kwargs):
        super(RarityRewardScreen, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            model.setName(self.__element.name)
            model.setTitle(self.__element.userName)
            model.setRarity(self.__element.rarity)
        switchHangarOverlaySoundFilter(on=True)
        self.__sound = SoundGroups.g_instance.getSound2D(self._REWARD_SOUND_ID)
        self.__sound.play()

    def _finalize(self):
        super(RarityRewardScreen, self)._finalize()
        g_eventBus.handleEvent(events.CustomizationEvent(events.CustomizationEvent.ON_RARITY_REWARD_SCREEN_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        switchHangarOverlaySoundFilter(on=False)
        self.__sound = None
        return

    def __onClose(self):
        self.destroyWindow()


class RarityRewardWindow(LobbyWindow):
    __slots__ = ('_blur',)

    def __init__(self, element):
        self._blur = None
        super(RarityRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=RarityRewardScreen(element), layer=WindowLayer.OVERLAY)
        return

    def _initialize(self):
        super(RarityRewardWindow, self)._initialize()
        self._blur = CachedBlur(enabled=True, ownLayer=self.layer)

    def _finalize(self):
        self._blur.fini()
        self._blur = None
        super(RarityRewardWindow, self)._finalize()
        return
