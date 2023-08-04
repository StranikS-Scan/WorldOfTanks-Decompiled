# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/lobby/gui_lootboxes/unique_rewards_view.py
import logging
import typing
from frameworks.wulf import WindowFlags, WindowLayer, ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window, View, ViewModel
_logger = logging.getLogger(__name__)
_HANDLERS_TYPES_LIST = []

def getUniqueRewardHandler(rewards):
    for handlerType in _HANDLERS_TYPES_LIST:
        possibleHandler = handlerType.createHandlerFromRewards(rewards)
        if possibleHandler is not None:
            return possibleHandler

    return


class IUniqueRewardHandler(object):

    def __init__(self, _):
        super(IUniqueRewardHandler, self).__init__()

    @classmethod
    def createHandlerFromRewards(cls, rewards):
        raise NotImplementedError

    def getRewardsData(self):
        raise NotImplementedError

    def getRewardsViewID(self):
        raise NotImplementedError

    def showRewardsWindow(self, parent):
        raise NotImplementedError

    def _getRewardsViewClass(self):
        raise NotImplementedError


class BaseUniqueRewardHandler(IUniqueRewardHandler):
    __slots__ = ('_rewardsData', '_window')

    def __init__(self, rewardsData):
        super(BaseUniqueRewardHandler, self).__init__(rewardsData)
        self._rewardsData = rewardsData
        self._window = None
        return

    @classmethod
    def createHandlerFromRewards(cls, rewards):
        return None

    def getRewardsData(self):
        return self._rewardsData

    def getRewardsViewID(self):
        return R.invalid()

    def showRewardsWindow(self, parent):
        self._window = UniqueLootBoxesRewardsWindow(self._getRewardsViewClass()(self.getRewardsViewID(), self._rewardsData), parent=parent)
        self._window.load()

    def _getRewardsViewClass(self):
        return BaseUniqueRewardsView


class UniqueLootBoxesRewardsWindow(LobbyWindow):

    def __init__(self, content, parent=None):
        super(UniqueLootBoxesRewardsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, None, content, parent, WindowLayer.OVERLAY)
        return


class BaseUniqueRewardsView(ViewImpl):
    __slots__ = ('_rewards',)

    def __init__(self, layoutID, rewards, model=None):
        settings = ViewSettings(layoutID)
        settings.model = model
        super(BaseUniqueRewardsView, self).__init__(settings)
        self._rewards = rewards


def registerHandler(handlerType):
    _HANDLERS_TYPES_LIST.append(handlerType)
