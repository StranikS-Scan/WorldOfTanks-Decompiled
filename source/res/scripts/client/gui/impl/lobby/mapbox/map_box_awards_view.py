# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mapbox/map_box_awards_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_awards_view_model import MapBoxAwardsViewModel
from gui.impl.lobby.mapbox.sound import getMapboxViewSoundSpace
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.mapbox.mapbox_bonus_packers import getMapboxBonusPacker
from gui.mapbox.mapbox_helpers import packMapboxRewardModelAndTooltip, getMapboxRewardTooltip
from gui.shared.event_dispatcher import showMapboxRewardChoice
from shared_utils import first

class MapBoxAwardsView(ViewImpl):
    __slots__ = ('__numBattles', '__tooltips', '__reward')
    _COMMON_SOUND_SPACE = getMapboxViewSoundSpace(enterEvent='bp_reward_screen')

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

    def _initialize(self, *args, **kwargs):
        super(MapBoxAwardsView, self)._initialize(*args, **kwargs)
        self.viewModel.onPick += self.__onPick

    def _finalize(self):
        self.viewModel.onPick -= self.__onPick
        super(MapBoxAwardsView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(MapBoxAwardsView, self)._onLoading(*args, **kwargs)
        packer = getMapboxBonusPacker()
        with self.viewModel.transaction() as model:
            model.setBattlesNumber(self.__numBattles)
            rewardsList = model.rewards
            packMapboxRewardModelAndTooltip(rewardsList, self.__reward, packer, self.__numBattles, self.__tooltips)
            rewardsList.invalidate()

    def __onPick(self, args):
        rewardModel = self.viewModel.rewards.getItem(int(args['index']))
        selectableCrewbook = first([ item for item in self.__reward if item.getName() == 'selectableCrewbook' ])
        reward = first([ item for item in selectableCrewbook.getItems() if item.name == rewardModel.getName() ])
        showMapboxRewardChoice(reward)


class MapBoxAwardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, numBattles, rewards, parent=None):
        super(MapBoxAwardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=MapBoxAwardsView(numBattles, rewards), parent=parent)
