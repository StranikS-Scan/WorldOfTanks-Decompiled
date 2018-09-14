# Embedded file name: scripts/client/tutorial/control/chains/functional.py
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.daapi.view.lobby.server_events.events_helpers import EVENT_STATUS
from gui.shared.ItemsCache import g_itemsCache
from tutorial.control.functional import FunctionalEffect
from tutorial.data.hints import HintProps
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_ERROR
from gui.server_events import events_dispatcher

class FunctionalShowHint(FunctionalEffect):

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        return self._gui.isEffectRunning(GUI_EFFECT_NAME.SHOW_HINT, self._effect.getTargetID())

    def triggerEffect(self):
        hint = self.getTarget()
        if hint is None:
            LOG_ERROR('Chain hint is not found', self._effect.getTargetID())
            return
        else:
            text = hint.getText()
            if text:
                text = self._tutorial.getVars().get(text, default=text)
            hintID = hint.getID()
            uniqueID = '{}_{}'.format(self._data.getID(), hintID)
            props = HintProps(uniqueID, hintID, hint.getTargetID(), text, hint.hasBox(), hint.getArrow(), hint.getPadding())
            self._gui.playEffect(GUI_EFFECT_NAME.SHOW_HINT, (props, hint.getActionTypes()))
            return


class FunctionalCloseHint(FunctionalEffect):

    def triggerEffect(self):
        hint = self.getTarget()
        if hint is None:
            LOG_ERROR('Chain hint is not found', self._effect.getTargetID())
            return
        else:
            self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, hint.getID())
            return


class FunctionalSwitchToRandom(FunctionalEffect):

    def triggerEffect(self):
        from gui.prb_control.context import PrebattleAction
        from gui.prb_control.dispatcher import g_prbLoader
        from gui.prb_control.settings import PREBATTLE_ACTION_NAME
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            dispatcher.doSelectAction(PrebattleAction(PREBATTLE_ACTION_NAME.RANDOM_QUEUE))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return


class FunctionalShowUnlockedChapter(FunctionalEffect):

    def triggerEffect(self):
        chapterID = self._tutorial.getVars().get(self.getTargetID())
        descriptor = events_helpers.getTutorialEventsDescriptor()
        completed = g_itemsCache.items.stats.tutorialsCompleted
        chapterIdx = descriptor.getChapterIdx(chapterID)
        chaptersCount = descriptor.getNumberOfChapters()
        nextChapterID = self.__getOpenedChapterID(descriptor, completed, chapterIdx, chaptersCount) or self.__getOpenedChapterID(descriptor, completed, 0, chapterIdx)
        events_dispatcher.showTutorialTabInEventsWindow(nextChapterID)

    def __getOpenedChapterID(self, descriptor, completed, startIdx, stopIdx):
        for i in range(startIdx, stopIdx):
            chapter = descriptor.getChapterByIdx(i)
            if chapter.getChapterStatus(descriptor, completed) == EVENT_STATUS.NONE:
                return chapter.getID()

        return None


class FunctionalShowAwardWindow(FunctionalEffect):

    def triggerEffect(self):
        window = self.getTarget()
        if window is not None:
            content = window.getContent()
            if not window.isContentFull():
                query = self._tutorial._ctrlFactory.createContentQuery(window.getType())
                query.invoke(content, window.getVarRef())
            self._gui.showAwardWindow(window.getID(), window.getType(), content)
        else:
            LOG_ERROR('PopUp not found', self._effect.getTargetID())
        return
