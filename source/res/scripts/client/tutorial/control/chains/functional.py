# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/chains/functional.py
from adisp import process
from debug_utils import LOG_DEBUG
from gui.shared.utils import isPopupsWindowsOpenDisabled
from tutorial.control.functional import FunctionalEffect
from tutorial.data.hints import HintProps
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_ERROR

class FunctionalShowHint(FunctionalEffect):

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        return self._gui.isEffectRunning(GUI_EFFECT_NAME.SHOW_HINT, self._effect.getTargetID())

    def triggerEffect(self):
        hint = self.getTarget()
        if hint is None:
            LOG_ERROR('Chain hint is not found', self._effect.getTargetID())
            return False
        else:
            text = hint.getText()
            if text:
                text = self._tutorial.getVars().get(text, default=text)
            hintID = hint.getID()
            uniqueID = '{}_{}'.format(self._data.getID(), hintID)
            props = HintProps(uniqueID, hintID, hint.getTargetID(), text, hint.hasBox(), hint.getArrow(), hint.getPadding(), updateRuntime=False, checkViewArea=False)
            return self._gui.playEffect(GUI_EFFECT_NAME.SHOW_HINT, (props, hint.getActionTypes()))


class FunctionalCloseHint(FunctionalEffect):

    def triggerEffect(self):
        hint = self.getTarget()
        if hint is None:
            LOG_ERROR('Chain hint is not found', self._effect.getTargetID())
            return False
        else:
            self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, hint.getID())
            return True


class FunctionalSwitchToRandom(FunctionalEffect):

    def triggerEffect(self):
        from gui.prb_control.dispatcher import g_prbLoader
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is not None:
            self.__doSelect(dispatcher)
            return True
        else:
            LOG_ERROR('Prebattle dispatcher is not defined')
            return False

    @process
    def __doSelect(self, dispatcher):
        from gui.prb_control.entities.base.ctx import PrbAction
        from gui.prb_control.settings import PREBATTLE_ACTION_NAME
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))


class FunctionalShowAwardWindow(FunctionalEffect):

    def triggerEffect(self):
        window = self.getTarget()
        if window is not None:
            if isPopupsWindowsOpenDisabled():
                LOG_DEBUG("Awards windows are disabled by setting 'popupsWindowsDisabled' in preferences.xml")
            else:
                content = window.getContent()
                if not window.isContentFull():
                    query = self._ctrlFactory.createContentQuery(window.getType())
                    query.invoke(content, window.getVarRef())
                self._gui.showAwardWindow(window.getID(), window.getType(), content)
                return True
        LOG_ERROR('PopUp not found', self._effect.getTargetID())
        return False
