# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/armory_yard_simple_tooltip_view.py
from operator import attrgetter
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IArmoryYardController
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import SimpleTooltipStates, TabId

class ArmoryYardSimpleTooltipView(ViewImpl):
    __slots__ = ('__state', '__id')
    _RES_ROOT = R.strings.armory_yard.tooltip
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self, state, id):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.ArmoryYardSimpleTooltipView())
        settings.model = SimpleTooltipContentModel()
        self.__state = state
        self.__id = id
        super(ArmoryYardSimpleTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ArmoryYardSimpleTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardSimpleTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setHeader(self.__getHeader())
            tx.setBody(self.__getBody())
            tx.setNote(self.__getNote())

    def __getHeader(self):
        if self.__state == SimpleTooltipStates.CHAPTER:
            return backport.text(self._RES_ROOT.chapter.disabled.header())
        if self.__state == SimpleTooltipStates.TAB:
            tab = 'progression' if self.__id == TabId.PROGRESS else 'quests'
            return backport.text(self._RES_ROOT.tab.dyn(tab).header())

    def __getBody(self):
        ctrl = self.__armoryYardCtrl
        if not ctrl.isEnabled():
            return ''
        if self.__state == SimpleTooltipStates.CHAPTER:
            currentSeason = ctrl.serverSettings.getCurrentSeason()
            prevChapterTokens = 0
            nowTime = time_utils.getServerUTCTime()
            for cycle in sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID')):
                if cycle.ID == self.__id and cycle.startDate <= nowTime:
                    return backport.text(self._RES_ROOT.chapter.disabled.doPrevious.body(), count=prevChapterTokens)
                prevChapterTokens = ctrl.totalTokensInChapter(cycle.ID) - ctrl.receivedTokensInChapter(cycle.ID)

        elif self.__state == SimpleTooltipStates.TAB:
            tab = 'progression' if self.__id == TabId.PROGRESS else 'quests'
            return backport.text(self._RES_ROOT.tab.dyn(tab).body())

    def __getNote(self):
        if not self.__armoryYardCtrl.isEnabled():
            return ''
        if self.__state == SimpleTooltipStates.CHAPTER:
            currentSeason = self.__armoryYardCtrl.serverSettings.getCurrentSeason()
            nowTime = time_utils.getServerUTCTime()
            for cycle in sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID')):
                if cycle.ID == self.__id and cycle.startDate > nowTime:
                    startDateString = backport.text(self._RES_ROOT.chapter.disabled.doFuture.noteDate(), color_open='%(brown_open)s', startDate=backport.getDateTimeFormat(cycle.startDate), color_close='%(brown_close)s')
                    return backport.text(self._RES_ROOT.chapter.disabled.doFuture.note(), startText=startDateString)

        elif self.__state == SimpleTooltipStates.TAB:
            if self.__id == TabId.QUESTS:
                startTime, endTime = self.__armoryYardCtrl.getProgressionTimes()
                periodString = backport.text(self._RES_ROOT.tab.quests.noteDate(), color_open='%(brown_open)s', startDate=backport.getDateTimeFormat(startTime), endDate=backport.getDateTimeFormat(endTime), color_close='%(brown_close)s')
                return backport.text(self._RES_ROOT.tab.quests.note(), periodText=periodString)
