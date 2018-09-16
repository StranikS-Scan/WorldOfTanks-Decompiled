# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/lobby/functional.py
from tutorial.control.functional import FunctionalEffect, FunctionalConditions, FunctionalChapterContext
from tutorial.logger import LOG_ERROR

class FunctionalShowHintEffect(FunctionalEffect):

    def triggerEffect(self):
        hint = self.getTarget()
        if hint is not None:
            return self._gui.playEffect('ShowHint', hint.getData())
        else:
            LOG_ERROR('Hint not found', self._effect.getTargetID())
            return False


class FunctionalCloseHintEffect(FunctionalEffect):

    def triggerEffect(self):
        self._gui.stopEffect('ShowHint', self._effect.getTargetID())
        return True


class FunctionalLobbyChapterContext(FunctionalChapterContext):

    def __init__(self):
        super(FunctionalLobbyChapterContext, self).__init__()
        chapter = self._data
        chapterID = chapter.getID()
        self._conditions = None
        conditions = chapter.getHasIDEntity(chapterID)
        if conditions:
            self._conditions = FunctionalConditions(conditions)
        self._isShow = False
        return

    def invalidate(self):
        super(FunctionalLobbyChapterContext, self).invalidate()
        if self._conditions is None:
            return
        else:
            ok = self._conditions.allConditionsOk()
            if ok and not self._isShow:
                chapter = self._data
                self._gui.setChapterInfo(chapter.getTitle(), chapter.getDescription(afterBattle=self._cache.isAfterBattle()))
                self._isShow = True
            elif not ok and self._isShow:
                self._gui.clearChapterInfo()
                self._isShow = False
            return
