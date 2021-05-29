# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mapbox/mapbox_reward_choice_view.py
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mapbox.map_box_reward_choice_view_model import MapBoxRewardChoiceViewModel
from gui.impl.lobby.mapbox.sound import getMapboxViewSoundSpace
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.mapbox.mapbox_bonus_packers import getMapboxBonusPacker
from gui.mapbox.mapbox_helpers import packMapboxRewardModelAndTooltip, getMapboxRewardTooltip
from helpers import dependency
from skeletons.gui.game_control import IMapboxController

class MapboxRewardChoiceView(ViewImpl):
    __slots__ = ('__tooltips', '__selectableCrewbook')
    _COMMON_SOUND_SPACE = getMapboxViewSoundSpace()
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def __init__(self, layoutID, selectableCrewbook, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.model = MapBoxRewardChoiceViewModel()
        settings.args = args
        settings.kwargs = kwargs
        self.__tooltips = []
        self.__selectableCrewbook = selectableCrewbook
        super(MapboxRewardChoiceView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MapboxRewardChoiceView, self).getViewModel()

    def createToolTip(self, event):
        tooltip = getMapboxRewardTooltip(event, self.__tooltips, self.getParentWindow())
        return tooltip or super(MapboxRewardChoiceView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        super(MapboxRewardChoiceView, self)._onLoading(*args, **kwargs)
        crewbookOptions = self.__selectableCrewbook.options
        packer = getMapboxBonusPacker()
        with self.viewModel.transaction() as model:
            rewardsList = model.rewards
            rewardsList.clearItems()
            packMapboxRewardModelAndTooltip(rewardsList, [crewbookOptions], packer, 0, self.__tooltips)
            rewardsList.invalidate()
            model.setRewardType(backport.text(R.strings.mapbox.selectableCrewbook.dyn(self.__selectableCrewbook.name)()))

    def _finalize(self):
        self.viewModel.onCloseClick -= self.__onCloseClick
        self.viewModel.onTakeClick -= self.__onTakeClick
        super(MapboxRewardChoiceView, self)._finalize()

    def _initialize(self, *args, **kwargs):
        super(MapboxRewardChoiceView, self)._initialize(*args, **kwargs)
        self.viewModel.onTakeClick += self.__onTakeClick
        self.viewModel.onCloseClick += self.__onCloseClick

    def __onCloseClick(self):
        self.destroyWindow()

    def __onTakeClick(self, args):
        itemID = args.get('itemID')
        self.__mapboxCtrl.selectCrewbookNation(itemID)


class MapboxRewardChoiceWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, selectableCrewbook):
        super(MapboxRewardChoiceWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=MapboxRewardChoiceView(R.views.lobby.mapbox.MapBoxRewardChoiceView(), selectableCrewbook))
