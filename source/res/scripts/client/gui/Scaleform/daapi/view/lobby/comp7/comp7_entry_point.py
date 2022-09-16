# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/comp7/comp7_entry_point.py
from shared_utils import nextTick
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.meta.Comp7EntryPointMeta import Comp7EntryPointMeta
from gui.impl.pub import ViewImpl
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.comp7.views.banner_model import BannerModel, State
from gui.periodic_battles.models import PeriodType
from gui.prb_control.entities.comp7 import comp7_prb_helpers
from helpers import dependency, time_utils
from skeletons.gui.game_control import IComp7Controller
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES

def isComp7EntryPointAvailable():
    comp7Ctrl = dependency.instance(IComp7Controller)
    settings = comp7Ctrl.getModeSettings()
    return comp7Ctrl.isEnabled() and settings is not None and settings.seasons


class Comp7EntryPoint(Comp7EntryPointMeta):

    def isSingle(self, value):
        if self.__view:
            self.__view.setIsSingle(value)

    def _makeInjectView(self):
        self.__view = Comp7EntryPointView(flags=ViewFlags.COMPONENT)
        return self.__view


class Comp7EntryPointView(ViewImpl):
    __START_NOTIFICATIONS_PERIOD_LENGTH = time_utils.ONE_DAY * 14
    __END_NOTIFICATIONS_PERIOD_LENGTH = time_utils.ONE_DAY * 14
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.comp7.views.Banner())
        settings.flags = flags
        settings.model = BannerModel()
        super(Comp7EntryPointView, self).__init__(settings)
        self.__isSingle = True

    @property
    def viewModel(self):
        return super(Comp7EntryPointView, self).getViewModel()

    def setIsSingle(self, value):
        self.__isSingle = value
        self.__updateState()

    def _initialize(self, *args, **kwargs):
        super(Comp7EntryPointView, self)._initialize(*args, **kwargs)
        self.viewModel.onOpen += self.__onOpen
        self.__comp7Controller.onStatusUpdated += self.__onStatusUpdated
        self.__comp7Controller.onComp7ConfigChanged += self.__onConfigChanged

    def _finalize(self):
        self.viewModel.onOpen -= self.__onOpen
        self.__comp7Controller.onStatusUpdated -= self.__onStatusUpdated
        self.__comp7Controller.onComp7ConfigChanged -= self.__onConfigChanged
        super(Comp7EntryPointView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(Comp7EntryPointView, self)._onLoading(*args, **kwargs)
        self.__updateState()

    def __onStatusUpdated(self, _):
        self.__updateState()

    def __onConfigChanged(self):
        self.__updateState()

    def __updateState(self):
        if isComp7EntryPointAvailable():
            with self.viewModel.transaction() as tx:
                tx.setIsSingle(self.__isSingle)
                state, actualTime = self.__getPeriodStateAndActualTime()
                tx.setState(state)
                tx.setTimestamp(actualTime or 0)
        else:
            nextTick(self.destroy)()

    def __getPeriodStateAndActualTime(self):
        currentTime = time_utils.getCurrentLocalServerTimestamp()
        periodInfo = self.__comp7Controller.getPeriodInfo()
        if periodInfo.periodType in (PeriodType.BEFORE_SEASON, PeriodType.BEFORE_CYCLE, PeriodType.BETWEEN_SEASONS):
            return (State.NOTSTARTED, periodInfo.cycleBorderRight.timestamp)
        elif periodInfo.periodType in (PeriodType.AFTER_SEASON,
         PeriodType.AFTER_CYCLE,
         PeriodType.ALL_NOT_AVAILABLE_END,
         PeriodType.NOT_AVAILABLE_END,
         PeriodType.STANDALONE_NOT_AVAILABLE_END):
            return (State.END, None)
        elif periodInfo.periodType in (PeriodType.ALL_NOT_AVAILABLE, PeriodType.STANDALONE_NOT_AVAILABLE):
            return (State.DISABLED, periodInfo.primeDelta)
        else:
            if periodInfo.cycleBorderLeft.delta(currentTime) < self.__START_NOTIFICATIONS_PERIOD_LENGTH:
                status = State.JUSTSTARTED
            elif periodInfo.cycleBorderRight.delta(currentTime) < self.__END_NOTIFICATIONS_PERIOD_LENGTH:
                status = State.ENDSOON
            else:
                status = State.ACTIVE
            return (status, periodInfo.cycleBorderRight.timestamp)

    @staticmethod
    def __onOpen():
        comp7_prb_helpers.selectComp7()
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.COMP7)
