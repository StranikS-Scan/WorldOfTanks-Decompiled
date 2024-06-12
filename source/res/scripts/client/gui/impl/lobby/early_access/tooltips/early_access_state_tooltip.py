# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/tooltips/early_access_state_tooltip.py
import typing
from operator import attrgetter
from enum import Enum
from early_access_common import EARLY_ACCESS_POSTPR_KEY
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel
from gui.impl.gen.view_models.views.lobby.early_access.early_access_quests_view_model import QuestsViewTooltipStates
from gui.impl.gen.view_models.views.lobby.early_access.early_access_vehicle_model import VehicleViewTooltipStates
from gui.impl.gen.view_models.views.lobby.early_access.early_access_state_enum import State
from gui.impl.pub import ViewImpl
from skeletons.gui.game_control import IEarlyAccessController
from helpers import dependency, time_utils, int2roman

class TooltipBuilder(object):
    _RES_ROOT = R.strings.early_access
    _earlyAccessCtrl = dependency.descriptor(IEarlyAccessController)

    def __init__(self, state, id):
        self._state = state
        self._id = id

    def getHeader(self):
        pass

    def getBody(self):
        pass

    def getNote(self):
        pass

    def _formNoteText(self, startDate):
        startDateString = backport.text(self._RES_ROOT.questsView.chapter.disabled.doFuture.noteDate(), color_open='%(brown_open)s', startDate=backport.getDateTimeFormat(startDate), color_close='%(brown_close)s')
        return backport.text(self._RES_ROOT.questsView.chapter.disabled.doFuture.note(), startText=startDateString)

    def _formNoteRangeDate(self, startDate, endDate, endSeasonDate):
        mainProgressString = backport.text(self._RES_ROOT.tankView.questsWidget.mainProgress.noteDate(), color_open='%(brown_open)s', startDate=backport.getShortDateFormat(startDate), endDate=backport.getShortDateFormat(endDate), color_close='%(brown_close)s')
        postProgressString = backport.text(self._RES_ROOT.tankView.questsWidget.postprogression.noteDate(), color_open='%(brown_open)s', endDate=backport.getShortDateFormat(endSeasonDate), color_close='%(brown_close)s')
        return backport.text(self._RES_ROOT.tankView.questsWidget.progress(), mainProgress=mainProgressString, postProgress=postProgressString)


class QuestsTooltipBuilder(TooltipBuilder):

    class CycleState(Enum):
        NOTSTARTED = 0
        DOINFUTURE = 1
        FINISHED = 2

    def __init__(self, state, id):
        super(QuestsTooltipBuilder, self).__init__(state, id)
        cycleState, cycle = self.__getCycleState()
        self.__cycleState = cycleState
        self.__cycle = cycle

    def getHeader(self):
        if self._state == QuestsViewTooltipStates.CHAPTER.value:
            return backport.text(self._RES_ROOT.questsView.chapter.disabled.doFuture.header())
        return backport.text(self._RES_ROOT.questsView.quest.disabled.doFuture.header()) if self._state == QuestsViewTooltipStates.QUEST.value else ''

    def getBody(self):
        if self._state == QuestsViewTooltipStates.CHAPTER.value:
            if self._id == EARLY_ACCESS_POSTPR_KEY:
                return self.__formRequiredVehiclesText()
            if self.__cycleState == self.CycleState.DOINFUTURE:
                return backport.text(self._RES_ROOT.questsView.chapter.disabled.doFuture.body())
            if self.__cycleState == self.CycleState.FINISHED:
                return backport.text(self._RES_ROOT.questsView.chapter.disabled.cycleFinished.body())
        elif self._state == QuestsViewTooltipStates.QUEST.value:
            if self.__cycleState == self.CycleState.FINISHED:
                return backport.text(self._RES_ROOT.questsView.quest.disabled.cycleFinished.body())
            if self.__cycleState == self.CycleState.NOTSTARTED:
                return ''
            return backport.text(self._RES_ROOT.questsView.quest.disabled.doFuture.body())

    def getNote(self):
        if self._state == QuestsViewTooltipStates.CHAPTER.value:
            if self.__cycleState == self.CycleState.NOTSTARTED:
                return self._formNoteText(self.__cycle.startDate)
        if self._state == QuestsViewTooltipStates.QUEST.value:
            if self.__cycleState == self.CycleState.NOTSTARTED:
                return self._formNoteText(self.__cycle.startDate)

    def __formRequiredVehiclesText(self):
        _, minLvl, maxLvl = self._earlyAccessCtrl.getRequiredVehicleTypeAndLevelsForQuest(None)
        return backport.text(self._RES_ROOT.questsView.chapter.postprogression.disabled.doFuture.samelvl.body(), lvl=int2roman(minLvl)) if minLvl == maxLvl else backport.text(self._RES_ROOT.questsView.chapter.postprogression.disabled.doFuture.body(), minLvl=int2roman(minLvl), maxLvl=int2roman(maxLvl))

    def __getCycleState(self):
        nowTime = time_utils.getServerUTCTime()
        currentSeason = self._earlyAccessCtrl.getCurrentSeason()
        eaState = self._earlyAccessCtrl.getState()
        if eaState == State.POSTPROGRESSION or eaState == State.BUY:
            return (self.CycleState.FINISHED, None)
        else:
            for cycle in sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID')):
                if self._id == str(cycle.ID):
                    if nowTime < cycle.startDate:
                        return (self.CycleState.NOTSTARTED, cycle)
                    if nowTime > cycle.startDate:
                        return (self.CycleState.DOINFUTURE, cycle)

            return (self.CycleState.DOINFUTURE, None)


class VehicleTooltipBuilder(TooltipBuilder):

    def getHeader(self):
        return backport.text(self._RES_ROOT.tankView.questsWidget.header()) if self._state == VehicleViewTooltipStates.QUESTSWIDGET.value else ''

    def getBody(self):
        return backport.text(self._RES_ROOT.tankView.questsWidget.body()) if self._state == VehicleViewTooltipStates.QUESTSWIDGET.value else ''

    def getNote(self):
        if self._state == VehicleViewTooltipStates.QUESTSWIDGET.value:
            currentSeason = self._earlyAccessCtrl.getCurrentSeason()
            startDate, endDate = self._earlyAccessCtrl.getProgressionTimes()
            return self._formNoteRangeDate(startDate, endDate, currentSeason.getEndDate())


class TooltipBuilderProvider(object):

    @classmethod
    def getBuilder(cls, tooltipState, id):
        if tooltipState in [ state.value for state in QuestsViewTooltipStates ]:
            return QuestsTooltipBuilder(tooltipState, id)
        else:
            return VehicleTooltipBuilder(tooltipState, id) if tooltipState in [ state.value for state in VehicleViewTooltipStates ] else None


class EarlyAccessStateTooltipView(ViewImpl):
    __slots__ = ('__state', '__id')

    def __init__(self, state, id=''):
        settings = ViewSettings(R.views.lobby.early_access.tooltips.EarlyAccessSimpleTooltipView())
        settings.model = SimpleTooltipContentModel()
        self.__state = state
        self.__id = id
        super(EarlyAccessStateTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(EarlyAccessStateTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessStateTooltipView, self)._onLoading(*args, **kwargs)
        builder = TooltipBuilderProvider.getBuilder(self.__state, self.__id)
        if builder is not None:
            with self.viewModel.transaction() as tx:
                tx.setHeader(builder.getHeader())
                tx.setBody(builder.getBody())
                tx.setNote(builder.getNote())
        return
