# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/battle_v2/effects.py
from tutorial.logger import LOG_ERROR, LOG_DEBUG
from tutorial.gui.Scaleform.effects_player import ComponentEffect

class ShowGreetingEffect(ComponentEffect):
    __slots__ = ('_greetingID',)

    def __init__(self):
        super(ShowGreetingEffect, self).__init__()
        self._greetingID = None
        return

    def isStillRunning(self, effectID=None):
        if effectID is not None:
            result = self._greetingID == effectID
        else:
            result = self._greetingID is not None
        return result

    def stop(self, effectID=None):
        if effectID is not None and effectID != self._greetingID:
            LOG_DEBUG('Greeting is not added', effectID)
            return
        else:
            if self._component is not None:
                self._component.as_hideGreetingS(effectID)
            return

    def _doPlay(self, effectData):
        if len(effectData) < 3:
            LOG_ERROR('Data is not full', effectData)
            return False
        self._greetingID, title, message = effectData[:3]
        self._component.as_showGreetingS(self._greetingID, title, message)
        return True


class ShowHintEffect(ComponentEffect):
    __slots__ = ()

    def _doPlay(self, effectData):
        if len(effectData) < 4:
            LOG_ERROR('Data is not full', effectData)
            return False
        self._component.as_showHintS(*effectData[:4])
        return True


class NextTaskEffect(ComponentEffect):
    __slots__ = ()

    def _doPlay(self, effectData):
        if len(effectData) < 3:
            LOG_ERROR('Data is not full', effectData)
            return False
        self._component.as_showNextTaskS(*effectData[:3])
        return True
