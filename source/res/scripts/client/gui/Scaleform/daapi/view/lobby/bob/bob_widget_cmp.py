# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/bob/bob_widget_cmp.py
import logging
from frameworks.wulf import ViewFlags
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.bob.bob_widget_tooltip_model import BobWidgetTooltipModel
from gui.impl.gen.view_models.views.bob.bob_widget_view_model import BobWidgetViewModel
from gui.impl.pub import ViewImpl
from gui.marathon.bob_event import BobEvent, BobEventAddUrl
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IMarathonEventsController, IBobController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
_EXPIRY_TIME_UPDATE_TIMEOUT = time_utils.ONE_MINUTE

class BobWidgetComponent(InjectComponentAdaptor):

    def _makeInjectView(self):
        return BobWidgetView()


class BobWidgetView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __bobController = dependency.descriptor(IBobController)
    __marathonEventsController = dependency.descriptor(IMarathonEventsController)
    __slots__ = ('__secondsNotifier', '__skillJustActivated')

    def __init__(self, *args, **kwargs):
        super(BobWidgetView, self).__init__(R.views.lobby.bob.bob_widget_cmp.BobWidgetCmp(), ViewFlags.COMPONENT, BobWidgetViewModel, *args, **kwargs)
        self.__secondsNotifier = None
        self.__skillJustActivated = False
        return

    @property
    def viewModel(self):
        return super(BobWidgetView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return BobWidgetTooltip() if event.contentID == R.views.lobby.bob.bob_widget_cmp.BobWidgetTooltip() else super(BobWidgetView, self).createToolTipContent(event=event, contentID=contentID)

    def _initialize(self):
        super(BobWidgetView, self)._initialize()
        self.viewModel.onWidgetClick += self.__onWidgetClick
        self.viewModel.onSkillClick += self.__onSkillClick
        self.__itemsCache.onSyncCompleted += self.__updateBobWidget
        self.__bobController.onUpdated += self.__updateBobWidget
        self.__bobController.onSkillActivated += self.__onSkillActivated
        self.__secondsNotifier = PeriodicNotifier(self.__getNotificationDelta, self.__updateSkillData, (_EXPIRY_TIME_UPDATE_TIMEOUT,))
        self.__secondsNotifier.startNotification()
        self.__updateModel()

    def _finalize(self):
        super(BobWidgetView, self)._finalize()
        self.__bobController.onSkillActivated -= self.__onSkillActivated
        self.__bobController.onUpdated -= self.__updateBobWidget
        self.__itemsCache.onSyncCompleted -= self.__updateBobWidget
        self.viewModel.onSkillClick -= self.__onSkillClick
        self.viewModel.onWidgetClick -= self.__onWidgetClick
        self.__secondsNotifier.stopNotification()
        self.__secondsNotifier.clear()

    def __updateBobWidget(self, *_):
        self.__updateModel()

    def __updateModel(self):
        with self.viewModel.transaction() as tx:
            tx.setBloggerId(self.__bobController.getBloggerId())
            tx.setBloggerPlace(self.__itemsCache.items.bob.teamRank)
            points = self.__itemsCache.items.bob.teamScore
            tx.setBloggerPoints(points)
            tx.setUsePoints(self.__bobController.isNaAsiaRealm())
            self.__setSkillData(tx)

    def __getNotificationDelta(self):
        return _EXPIRY_TIME_UPDATE_TIMEOUT

    def __onSkillActivated(self):
        self.__skillJustActivated = True

    def __updateSkillData(self):
        with self.getViewModel().transaction() as tx:
            self.__setSkillData(model=tx)

    def __setSkillData(self, model):
        skillName = self.__bobController.getActiveSkill()
        hasSkill = bool(skillName)
        model.setHasSkill(hasSkill)
        model.setJustActivated(False)
        if hasSkill:
            model.setActiveSkillName(skillName)
            model.setSkillRemainingTime(self.__getSkillRemainingTimeText())
            if self.__skillJustActivated:
                self.__skillJustActivated = False
                model.setJustActivated(True)

    def __getSkillRemainingTimeText(self):
        remainingSkillTime = self.__bobController.getSkillRemainingTime()
        if remainingSkillTime > 0:
            skillRemainingText = backport.getTillTimeStringByRClass(remainingSkillTime, R.strings.bob.skill.timeLeft, True)
        else:
            skillRemainingText = backport.text(R.strings.bob.skill.disactivated())
        return skillRemainingText

    def __onWidgetClick(self):
        if self.__marathonEventsController.isAnyActive():
            showMissionsMarathon(marathonPrefix=BobEvent.BOB_EVENT_PREFIX)

    def __onSkillClick(self):
        if self.__marathonEventsController.isAnyActive():
            bobEvent = self.__marathonEventsController.getMarathon(BobEvent.BOB_EVENT_PREFIX)
            bobEvent.setAdditionalUrl(BobEventAddUrl.SKILLS)
            showMissionsMarathon(marathonPrefix=BobEvent.BOB_EVENT_PREFIX)


class BobWidgetTooltip(ViewImpl):
    __marathonEventsController = dependency.descriptor(IMarathonEventsController)
    __slots__ = ()

    def __init__(self):
        super(BobWidgetTooltip, self).__init__(R.views.lobby.bob.bob_widget_cmp.BobWidgetTooltip(), ViewFlags.COMPONENT, BobWidgetTooltipModel)

    @property
    def viewModel(self):
        return super(BobWidgetTooltip, self).getViewModel()
