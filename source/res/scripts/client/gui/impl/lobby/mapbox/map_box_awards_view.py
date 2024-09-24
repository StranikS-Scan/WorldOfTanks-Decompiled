# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mapbox/map_box_awards_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_awards_view_model import MapBoxAwardsViewModel
from gui.impl.lobby.mapbox.sound import getMapboxViewSoundSpace, MapBoxSounds, playSound
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.mapbox.mapbox_bonus_packers import getMapboxBonusPacker, packMapboxRewardModelAndTooltip
from gui.mapbox.mapbox_helpers import getMapboxRewardTooltip

class MapBoxAwardsView(ViewImpl):
    __slots__ = ('__numBattles', '__tooltips', '__reward')
    _COMMON_SOUND_SPACE = getMapboxViewSoundSpace()

    def __init__(self, numBattles, reward, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.mapbox.MapBoxAwardsView(), model=MapBoxAwardsViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(MapBoxAwardsView, self).__init__(settings)
        self.__numBattles = numBattles
        self.__reward = reward
        self.__tooltips = []

    @property
    def viewModel(self):
        return super(MapBoxAwardsView, self).getViewModel()

    def createToolTip(self, event):
        tooltip = getMapboxRewardTooltip(event, self.__tooltips, self.getParentWindow())
        return tooltip or super(MapBoxAwardsView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(MapBoxAwardsView, self)._onLoading(*args, **kwargs)
        packer = getMapboxBonusPacker()
        with self.viewModel.transaction() as model:
            model.setBattlesNumber(self.__numBattles)
            rewardsList = model.rewards
            packMapboxRewardModelAndTooltip(rewardsList, self.__reward, packer, self.__numBattles, self.__tooltips)
            rewardsList.invalidate()
        playSound(MapBoxSounds.REWARD_SCREEN.value)


class MapBoxAwardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, numBattles, rewards, parent=None):
        super(MapBoxAwardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=MapBoxAwardsView(numBattles, rewards), parent=parent)
