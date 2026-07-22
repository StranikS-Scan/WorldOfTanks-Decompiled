# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/tooltips/armory_yard_simple_tooltip_view.py
from enum import Enum
from operator import attrgetter
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl import backport
from gui.impl.gen.view_models.windows.simple_tooltip_content_model import SimpleTooltipContentModel
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IArmoryYardController
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import SimpleTooltipStates, TabId
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sound_constants import getStageVoTapeRecorderName

class Media(Enum):
    VIDEO = 'video'
    AUDIO = 'audio'


class ArmoryYardSimpleTooltipView(ViewImpl):
    __slots__ = ('__state', '__id', '__step', '__stageManager')
    _RES_ROOT = R.strings.armory_yard.tooltip
    _RES_SHOP_ROOT = R.strings.armory_shop.tooltip
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)

    def __init__(self, state, id=0, step=0, stageManager=None):
        settings = ViewSettings(R.views.armory_yard.lobby.feature.tooltips.ArmoryYardSimpleTooltipView())
        settings.model = SimpleTooltipContentModel()
        self.__state = state
        self.__id = id
        self.__step = int(step) if step else 0
        self.__stageManager = stageManager
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
            return backport.text(self._RES_ROOT.tab.dyn(self.__getTabByTabID()).header())
        if self.__state == SimpleTooltipStates.SHOPINFO:
            return backport.text(self._RES_SHOP_ROOT.shop.info.header())
        if self.__state == SimpleTooltipStates.STEP:
            if self.__step >= self.__armoryYardCtrl.startStepOfPostProgression:
                return backport.text(self._RES_ROOT.step.postprogression.header())
            return backport.text(self._RES_ROOT.step.header())

    def __getBody(self):
        ctrl = self.__armoryYardCtrl
        if not ctrl.isEnabled():
            return ''
        if self.__state == SimpleTooltipStates.CHAPTER:
            currentSeason = ctrl.serverSettings.getCurrentSeason()
            prevChapterTokens = 0
            nowTime = time_utils.getServerUTCTime()
            for cycle in sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID')):
                if cycle.ID == self.__id:
                    if cycle.startDate <= nowTime:
                        return backport.ntext(self._RES_ROOT.chapter.disabled.doPrevious.body(), prevChapterTokens, count=prevChapterTokens)
                    return ''
                prevChapterTokens = ctrl.totalTokensInChapter(cycle.ID) - ctrl.receivedTokensInChapter(cycle.ID)

            notPassedChaptersCount = ctrl.startStepOfPostProgression - ctrl.getProgressionTokenCount()
            return backport.ntext(self._RES_ROOT.chapter.disabled.postProgression.doPrevious.body(), int(notPassedChaptersCount), count=int(notPassedChaptersCount))
        if self.__state == SimpleTooltipStates.TAB:
            return backport.text(self._RES_ROOT.tab.dyn(self.__getTabByTabID()).body())
        if self.__state == SimpleTooltipStates.SHOPINFO:
            return backport.text(self._RES_SHOP_ROOT.shop.info.body())
        if self.__state == SimpleTooltipStates.STEP:
            currentLvl = self.__armoryYardCtrl.getCurrentProgress()
            if self.__step > currentLvl:
                return backport.text(self._RES_ROOT.step.future.body())
            if self.__armoryYardCtrl.getProgressionLevel() < self.__step <= currentLvl:
                return backport.text(self._RES_ROOT.step.present.body())
            return backport.text(self._RES_ROOT.step.past.body())

    def __getTabByTabID(self):
        defaultTab = 'progression'
        if self.__id == TabId.PROGRESS:
            return 'progression'
        if self.__id == TabId.QUESTS:
            return 'quests'
        return 'shop' if self.__id == TabId.SHOP else defaultTab

    def __getMediaByStepID(self):
        soundName = getStageVoTapeRecorderName(self.__step)
        if R.sounds.dyn(soundName).isValid():
            return Media.AUDIO
        return Media.VIDEO if self.__stageManager.getStageVideoName(self.__step) else None

    def __getNote(self):
        if not self.__armoryYardCtrl.isEnabled():
            return ''
        if self.__state == SimpleTooltipStates.CHAPTER:
            currentSeason = self.__armoryYardCtrl.serverSettings.getCurrentSeason()
            nowTime = time_utils.getServerUTCTime()
            for cycle in sorted(currentSeason.getAllCycles().values(), key=attrgetter('ID')):
                if cycle.ID == self.__id and cycle.startDate > nowTime:
                    return backport.text(self._RES_ROOT.chapter.disabled.doFuture.note(), color_open='%(brown_open)s', startDate=self._getFormattedLocalTime(cycle.startDate), color_close='%(brown_close)s')

        elif self.__state == SimpleTooltipStates.TAB:
            if self.__id == TabId.QUESTS:
                startTime, endTime = self.__armoryYardCtrl.getProgressionTimes()
                return backport.text(self._RES_ROOT.tab.quests.note(), color_open='%(brown_open)s', startDate=self._getFormattedLocalTime(startTime), endDate=self._getFormattedLocalTime(endTime), color_close='%(brown_close)s')
        elif self.__state == SimpleTooltipStates.STEP and self.__armoryYardCtrl.getCurrentProgress() >= self.__step:
            media = self.__getMediaByStepID()
            if media:
                return backport.text(self._RES_ROOT.step.dyn(media.value).note())

    def _getFormattedLocalTime(self, timestamp):
        localTime = time_utils.getTimeStructInLocal(timestamp)
        return backport.text(self._RES_ROOT.tab.quests.noteDate(), day=localTime.tm_mday, month=backport.text(R.strings.menu.dateTime.months.num(localTime.tm_mon)()), year=localTime.tm_year, startTime='{:02d}:{:02d}'.format(localTime.tm_hour, localTime.tm_min))
