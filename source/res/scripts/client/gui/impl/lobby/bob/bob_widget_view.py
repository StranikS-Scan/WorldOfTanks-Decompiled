# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bob/bob_widget_view.py
import logging
import typing
import WWISE
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.bob.bob_helpers import getShortSkillName, getSkillTimeLeft
from gui.game_control.bob_sound_controller import BOB_HANGAR_SKILL_UP
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bob.bob_widget_skills_model import BobWidgetSkillsModel
from gui.impl.gen.view_models.views.lobby.bob.bob_widget_view_model import BobWidgetViewModel
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.marathon.bob_event import BobEvent, BobEventAddUrl
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IBobController, IMarathonEventsController
_logger = logging.getLogger(__name__)

class BobWidgetComponent(InjectComponentAdaptor):
    __slots__ = ('__view',)

    def _dispose(self):
        self.__view = None
        super(BobWidgetComponent, self)._dispose()
        return

    def _makeInjectView(self):
        self.__view = BobWidgetView(flags=ViewFlags.COMPONENT)
        return self.__view


class BobWidgetView(ViewImpl):
    __slots__ = ('__notifier', '__tooltipWindow')
    __bobController = dependency.descriptor(IBobController)
    __marathonsCtrl = dependency.descriptor(IMarathonEventsController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.bob.BobWidgetView())
        settings.flags = flags
        settings.model = BobWidgetViewModel()
        self.__notifier = None
        self.__tooltipWindow = None
        super(BobWidgetView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BobWidgetView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            if tooltipData is None:
                return
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            self.__tooltipWindow = window
            window.load()
            return window
        else:
            return super(BobWidgetView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        self.__updateViewModel()

    def _initialize(self, *args, **kwargs):
        self.__addListeners()

    def _finalize(self):
        self.__removeListeners()
        self.__clearNotifier()
        self.__clearTooltip()

    def __updateViewModel(self):
        with self.viewModel.transaction() as model:
            self.__updateTeamModel(model=model)
            self.__updateSkillModel(model=model)

    @replaceNoneKwargsModel
    def __updateSkillModel(self, model=None):
        skillModel = model.skill
        skill = self.__bobController.teamSkillsRequester.getCurrentTeamSkill()
        self.__clearNotifier()
        if skill is not None and skill.isActiveAt(time_utils.getServerUTCTime()):
            if skillModel.getState() == BobWidgetSkillsModel.STATE_INACTIVE:
                WWISE.WW_eventGlobal(BOB_HANGAR_SKILL_UP)
            skillModel.setState(BobWidgetSkillsModel.STATE_ACTIVE)
            skillModel.setSkill(getShortSkillName(skill.skill))
            skillModel.setCount(skill.count_left)
            skillModel.setTimeLeft(getSkillTimeLeft(skill.timeLeft))
            self.__notifier = PeriodicNotifier(lambda : skill.timeLeft, self.__tickSkillTime)
            self.__notifier.startNotification()
        else:
            skillModel.setState(BobWidgetSkillsModel.STATE_INACTIVE)
        return

    @replaceNoneKwargsModel
    def __updateTeamModel(self, model=None):
        teamID = self.__bobController.getCurrentTeamID()
        if teamID is None:
            _logger.warning('Player is not registered.')
            return
        else:
            teamData = self.__bobController.teamsRequester.getTeam(teamID)
            model.setTeamID(teamID)
            if self.__bobController.isAllZeroScore():
                state = BobWidgetViewModel.STATE_HIDDEN
            elif teamData is None:
                state = BobWidgetViewModel.STATE_BROKEN
            else:
                state = BobWidgetViewModel.STATE_NORMAL
                model.setRank(teamData.rank)
            model.setRankState(state)
            return

    @staticmethod
    def __onProgressionClick():
        showMissionsMarathon(marathonPrefix=BobEvent.BOB_EVENT_PREFIX)

    def __onSkillsClick(self):
        bobEvent = self.__marathonsCtrl.getMarathon(BobEvent.BOB_EVENT_PREFIX)
        bobEvent.setAdditionalUrl(BobEventAddUrl.SKILLS)
        showMissionsMarathon(marathonPrefix=BobEvent.BOB_EVENT_PREFIX)

    @replaceNoneKwargsModel
    def __tickSkillTime(self, model=None):
        skill = self.__bobController.teamSkillsRequester.getCurrentTeamSkill()
        if skill is not None and skill.isActiveAt(time_utils.getServerUTCTime()):
            model.skill.setTimeLeft(getSkillTimeLeft(skill.timeLeft))
        else:
            model.skill.setState(BobWidgetSkillsModel.STATE_INACTIVE)
        return

    def __onSkillsUpdated(self):
        self.__updateSkillModel()

    def __onTeamsUpdated(self):
        self.__updateTeamModel()

    def __onBobUpdated(self):
        self.__updateViewModel()

    def __addListeners(self):
        self.viewModel.onProgressionClick += self.__onProgressionClick
        self.viewModel.onSkillsClick += self.__onSkillsClick
        self.__bobController.teamSkillsRequester.onUpdated += self.__onSkillsUpdated
        self.__bobController.teamsRequester.onUpdated += self.__onTeamsUpdated
        self.__bobController.onUpdated += self.__onBobUpdated

    def __removeListeners(self):
        self.viewModel.onProgressionClick -= self.__onProgressionClick
        self.viewModel.onSkillsClick -= self.__onSkillsClick
        self.__bobController.teamSkillsRequester.onUpdated -= self.__onSkillsUpdated
        self.__bobController.teamsRequester.onUpdated -= self.__onTeamsUpdated
        self.__bobController.onUpdated -= self.__onBobUpdated

    def __clearNotifier(self):
        if self.__notifier:
            self.__notifier.stopNotification()
            self.__notifier.clear()

    def __clearTooltip(self):
        if self.__tooltipWindow is not None:
            self.__tooltipWindow.destroy()
            self.__tooltipWindow = None
        return

    @staticmethod
    def __getTooltipData(event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            if tooltipId == BobWidgetViewModel.PROGRESSIVE_TOOLTIP:
                teamID = event.getArgument('teamID')
                if teamID is not None:
                    return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BOB_PROGRESSIVE_INFO, specialArgs=[teamID])
            elif tooltipId == BobWidgetViewModel.SKILL_TOOLTIP:
                teamID = event.getArgument('teamID')
                if teamID is not None:
                    return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BOB_SKILL_INFO, specialArgs=[teamID])
            return
