# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/sales/functional.py
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, events
from tutorial.control.functional import FunctionalEffect
from tutorial.data.hints import HintProps
from tutorial.gui import GUI_EFFECT_NAME

class LoadViewEffect(FunctionalEffect):

    def __init__(self, effect):
        self._isRunning = False
        super(LoadViewEffect, self).__init__(effect)

    def triggerEffect(self):
        viewData = self.getTarget()
        if viewData is not None:
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(viewData.getAlias()), ctx=viewData.getCtx()), scope=viewData.getScope())
            return True
        else:
            return False


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
            props = HintProps(uniqueID, hintID, hint.getTargetID(), text, hint.hasBox(), hint.getArrow(), hint.getPadding(), updateRuntime=False, hideImmediately=hint.getHideImmediately(), checkViewArea=False)
            silent = False
            return self._gui.playEffect(GUI_EFFECT_NAME.SHOW_HINT, (props, hint.getActionTypes(), silent))


class FunctionalCloseHint(FunctionalEffect):

    def triggerEffect(self):
        hint = self.getTarget()
        if hint is None:
            LOG_ERROR('Chain hint is not found', self._effect.getTargetID())
            return False
        else:
            self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, hint.getID())
            return True
