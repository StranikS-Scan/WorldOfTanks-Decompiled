# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/sales/functional.py
import re
from debug_utils import LOG_ERROR
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import g_eventBus, events
from tutorial.control.functional import FunctionalEffect
from tutorial.data.hints import HintProps
from tutorial.gui import GUI_EFFECT_NAME
_var_search = re.compile('(\\$([A-Za-z0-9_]+)\\$)')

def _substituteVars(text, variables):
    for marker, varID in _var_search.findall(text):
        text = text.replace(marker, str(variables.get(varID, default=marker)))

    return text


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

    def __init__(self, effect):
        super(FunctionalShowHint, self).__init__(effect)
        self.__extraTriggers = []

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
                variables = self._tutorial.getVars()
                text = variables.get(text, default=text)
                text = _substituteVars(text, variables)
            hintID = hint.getID()
            uniqueID = '{}_{}'.format(self._data.getID(), hintID)
            props = HintProps(uniqueID, hintID, hint.getTargetID(), text, hint.hasBox(), hint.getArrow(), hint.getPadding(), updateRuntime=hint.getUpdateRuntime(), hideImmediately=hint.getHideImmediately(), checkViewArea=False)
            silent = False
            result = self._gui.playEffect(GUI_EFFECT_NAME.SHOW_HINT, (props, hint.getActionTypes(), silent))
            if result:
                self.__setExtraTriggers(hint)
            return result

    def stop(self):
        hint = self.getTarget()
        if hint is not None:
            self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, hint.getID())
        self.__clearExtraTriggers()
        return

    def __setExtraTriggers(self, hint):
        hintTargetID = hint.getTargetID()
        for action in hint.getActions():
            targetID = action.getTargetID()
            actionType = action.getType()
            if targetID == hintTargetID:
                continue
            if self._gui.playEffect(GUI_EFFECT_NAME.SET_TRIGGER, (targetID, actionType)):
                self.__extraTriggers.append((targetID, actionType))

    def __clearExtraTriggers(self):
        while self.__extraTriggers:
            targetID, actionType = self.__extraTriggers.pop()
            self._gui.stopEffect(GUI_EFFECT_NAME.SET_TRIGGER, targetID, actionType)


class FunctionalCloseHint(FunctionalEffect):

    def triggerEffect(self):
        hint = self.getTarget()
        if hint is None:
            LOG_ERROR('Chain hint is not found', self._effect.getTargetID())
            return False
        else:
            self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_HINT, hint.getID())
            self.__clearExtraTriggers(hint)
            return True

    def __clearExtraTriggers(self, hint):
        hintTargetID = hint.getTargetID()
        for action in hint.getActions():
            targetID = action.getTargetID()
            if targetID != hintTargetID:
                self._gui.stopEffect(GUI_EFFECT_NAME.SET_TRIGGER, targetID, action.getType())
