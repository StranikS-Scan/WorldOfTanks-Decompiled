# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_special_reward_view.py
import logging
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_special_reward_view_model import NewYearSpecialRewardViewModel
from frameworks.wulf import ViewSettings
from gui.impl.backport import BackportTooltipWindow, TooltipData
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.pub import ViewImpl
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.pub.lobby_window import LobbyOverlay, OverlayBehavior, OverlayBehaviorFlags
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.server_events.recruit_helper import getRecruitInfo
from helpers import dependency
from items.components.ny_constants import NY_MAN_QUEST_ID
from shared_utils import first
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)

class NewYearSpecialRewardView(ViewImpl):
    _eventsCache = dependency.descriptor(IEventsCache)
    __slots__ = ('__recruitToken',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_special_reward_view.NewYearSpecialRewardView())
        settings.model = NewYearSpecialRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearSpecialRewardView, self).__init__(settings)
        self.__recruitToken = ''

    @property
    def viewModel(self):
        return super(NewYearSpecialRewardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = TooltipData(isSpecial=True, tooltip=None, specialAlias=TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, specialArgs=[self.__recruitToken])
            window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            window.load()
            return window
        else:
            return super(NewYearSpecialRewardView, self).createToolTip(event)

    def _initialize(self):
        super(NewYearSpecialRewardView, self)._initialize()
        NewYearSoundsManager.playEvent(NewYearSoundEvents.SANTA_CLAUS_SCREEN)
        quest = self._eventsCache.getQuestByID(NY_MAN_QUEST_ID)
        if quest is not None:
            for bonus in quest.getBonuses():
                if bonus.getName() == 'tmanToken':
                    self.__recruitToken = first(bonus.getValue().iterkeys(), '')

            if getRecruitInfo(self.__recruitToken) is None:
                _logger.error('Quest has not recruit token')
        self.viewModel.onClose += self.__onClose
        self.viewModel.onRecruit += self.__onRecruit
        setOverlayHangarGeneral(True)
        return

    def _finalize(self):
        NewYearSoundsManager.playEvent(NewYearSoundEvents.SANTA_CLAUS_SCREEN_EXIT)
        setOverlayHangarGeneral(False)
        super(NewYearSpecialRewardView, self)._finalize()
        self.getViewModel().onClose -= self.__onClose
        self.getViewModel().onRecruit -= self.__onRecruit

    def __onCloseAction(self):
        self.destroyWindow()

    def __onRecruit(self):
        showRecruitWindow(self.__recruitToken)
        self.destroyWindow()

    def __onClose(self):
        self.__onCloseAction()


class NewYearSpecialRewardWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(NewYearSpecialRewardWindow, self).__init__(decorator=None, content=NewYearSpecialRewardView(), parent=None, behavior=OverlayBehavior(OverlayBehaviorFlags.IS_EXCLUSIVE))
        return
