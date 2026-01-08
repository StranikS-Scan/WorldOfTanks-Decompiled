# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collector20_reward/collector20_reward_view.py
from constants import DOSSIER_TYPE
from frameworks.wulf import ViewSettings, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.awards_view_model import AwardsViewModel
from gui.impl.lobby.collector20_reward.packers import getCollector20RewardsBonusPacker
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import DossierBonus
import SoundGroups
EXIT_EVENT = 'gui_hangar_award_screen_stop'

class Collector20RewardView(ViewImpl):

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.mono.lobby.collector20_reward())
        settings.model = AwardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(Collector20RewardView, self).__init__(settings)
        self.__tooltipItems = {}

    @property
    def viewModel(self):
        return super(Collector20RewardView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(Collector20RewardView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltipItems.get(tooltipId)

    def _onLoading(self, dossierRewards, *args, **kwargs):
        super(Collector20RewardView, self)._onLoading(*args, **kwargs)
        if not dossierRewards:
            return
        dossierBonus = DossierBonus('dossier', {DOSSIER_TYPE.ACCOUNT: dossierRewards})
        with self.viewModel.transaction() as vm:
            packBonusModelAndTooltipData([dossierBonus], vm.mainRewards, self.__tooltipItems, packer=getCollector20RewardsBonusPacker())

    def _finalize(self):
        SoundGroups.g_instance.playSound2D(EXIT_EVENT)
        self.__tooltipItems.clear()
        super(Collector20RewardView, self)._finalize()

    def _getEvents(self):
        return super(Collector20RewardView, self)._getEvents() + ((self.viewModel.onClose, self.__onClose),)

    def __onClose(self, *_):
        self.destroyWindow()


class Collector20RewardWindow(LobbyNotificationWindow):

    def __init__(self, dossierRewards, parent=None):
        super(Collector20RewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=Collector20RewardView(dossierRewards), parent=parent)
