# Embedded file name: scripts/client/tutorial/control/chains/functional.py
from collections import namedtuple
from tutorial.control.functional import FunctionalEffect
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_ERROR
_HintProps = namedtuple('_HintProps', ('uniqueID', 'hintID', 'itemID', 'text', 'hasBox', 'arrow', 'padding'))

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
            props = _HintProps(uniqueID, hintID, hint.getTargetID(), text, hint.hasBox(), hint.getArrow(), hint.getPadding())
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
            dispatcher.doSelectAction(PrebattleAction(PREBATTLE_ACTION_NAME.JOIN_RANDOM_QUEUE))
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
        return
