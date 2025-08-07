# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/regular_reward_view.py
import logging
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wot_anniversary.regular_reward_view_model import RegularRewardViewModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.wot_anniversary.bonus_packers import getWotAnniversaryRewardBonusPacker, composeBonuses
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from helpers import dependency
from skeletons.gui.wot_anniversary import IWotAnniversaryController
_logger = logging.getLogger(__name__)

class RegularRewardView(ViewImpl):
    __wotAnniversaryController = dependency.descriptor(IWotAnniversaryController)

    def __init__(self, closeCallback=None, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.wot_anniversary.RegularRewardView(), model=RegularRewardViewModel(), args=args, kwargs=kwargs)
        self.__closeCallback = closeCallback
        super(RegularRewardView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _getEvents(self):
        return super(RegularRewardView, self)._getEvents() + ((self.viewModel.onClose, self.__onClose),)

    def _onLoading(self, bonuses, *args, **kwargs):
        super(RegularRewardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            packBonusModelAndTooltipData(composeBonuses(bonuses), tx.getBonuses(), packer=getWotAnniversaryRewardBonusPacker())

    def _finalize(self):
        if self.__closeCallback is not None:
            self.__closeCallback()
            self.__closeCallback = None
        super(RegularRewardView, self)._finalize()
        return

    def __onClose(self):
        self.destroyWindow()


class RegularRewardWindow(LobbyWindow):

    def __init__(self, parent=None, *args, **kwargs):
        super(RegularRewardWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.TOP_WINDOW, content=RegularRewardView(*args, **kwargs), parent=parent)
