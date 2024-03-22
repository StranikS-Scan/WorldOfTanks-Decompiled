# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/effects_player.py
import logging
from collections import defaultdict
from helpers import dependency
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from skeletons.tutorial import ITutorialLoader
from tutorial.data.events import GuiEventType
_logger = logging.getLogger(__name__)

class GUIEffectScope(object):
    COMPONENT = 0
    SCENE = 1


class GUIEffect(object):
    __slots__ = ()

    def clear(self):
        pass

    def play(self, effectData):
        return False

    def stop(self, effectID=None, effectSubType=None):
        pass

    def cancel(self, scopeType, scopeName):
        pass

    def isStillRunning(self, effectID=None, effectSubType=None):
        return False


class ApplicationEffect(GUIEffect):
    __tutorialLoader = dependency.descriptor(ITutorialLoader)
    __slots__ = ('_app',)

    def __init__(self):
        super(GUIEffect, self).__init__()
        self._app = None
        return

    def clear(self):
        self._app = None
        super(ApplicationEffect, self).clear()
        return

    def setApplication(self, app):
        self._app = app

    def _getContainer(self, layer):
        if self._app is None:
            return
        else:
            manager = self._app.containerManager
            return None if manager is None else manager.getContainer(layer)

    def _getTutorialLayout(self):
        return self.__tutorialLoader.gui


_GUI_EVENT_TO_TRIGGER_TYPE = {GuiEventType.CLICK: TUTORIAL_TRIGGER_TYPES.CLICK_TYPE,
 GuiEventType.CLICK_OUTSIDE: TUTORIAL_TRIGGER_TYPES.CLICK_OUTSIDE_TYPE,
 GuiEventType.ESC: TUTORIAL_TRIGGER_TYPES.ESCAPE,
 GuiEventType.ENABLE: TUTORIAL_TRIGGER_TYPES.ENABLED,
 GuiEventType.DISABLE: TUTORIAL_TRIGGER_TYPES.DISABLED,
 GuiEventType.ENABLED_CHANGE: TUTORIAL_TRIGGER_TYPES.ENABLED_CHANGE,
 GuiEventType.VISIBLE_CHANGE: TUTORIAL_TRIGGER_TYPES.VISIBLE_CHANGE}

class ShowChainHint(ApplicationEffect):
    __slots__ = ('_hintsDict',)

    def __init__(self):
        super(ShowChainHint, self).__init__()
        self._hintsDict = {}

    def isStillRunning(self, effectID=None, effectSubType=None):
        if effectID is not None:
            result = effectID in self._hintsDict
        else:
            result = bool(self._hintsDict)
        return result

    def play(self, effectData):
        hintProps, triggers, silent = effectData
        if hintProps.hintID in self._hintsDict:
            _logger.debug('Hint %r is already added', hintProps.hintID)
            return True
        else:
            layout = self._getTutorialLayout()
            if layout is not None:
                content = {'uniqueID': hintProps.uniqueID,
                 'hintText': hintProps.text,
                 'hasBox': hintProps.hasBox,
                 'hasArrow': False,
                 'arrowDir': '',
                 'arrowLoop': False,
                 'updateRuntime': hintProps.updateRuntime,
                 'hideImmediately': hintProps.hideImmediately,
                 'checkViewArea': hintProps.checkViewArea}
                arrow = hintProps.arrow
                if arrow is not None:
                    content['hasArrow'] = True
                    content['arrowDir'] = arrow.direction
                    content['arrowLoop'] = arrow.loop
                    content['positionValue'] = arrow.positionValue
                    content['textPadding'] = arrow.textPadding
                padding = hintProps.padding
                if padding is not None:
                    content['padding'] = padding._asdict()
                triggers = [ _GUI_EVENT_TO_TRIGGER_TYPE[item] for item in triggers ]
                _logger.debug('layout %r showInteractiveHint with id %r, content %r, triggers %r', layout, hintProps.itemID, content, triggers)
                result = layout.showInteractiveHint(hintProps.itemID, content, triggers, silent)
                if result:
                    self._hintsDict.update({hintProps.hintID: hintProps.itemID})
                return result
            return False

    def stop(self, effectID=None, effectSubType=None):
        if effectID and effectID not in self._hintsDict:
            _logger.debug('Hint is not added. effectID: %r', effectID)
            return
        layout = self._getTutorialLayout()
        if layout and effectID:
            layout.closeInteractiveHint(self._hintsDict.pop(effectID))
        elif layout:
            for itemId in self._hintsDict.itervalues():
                layout.closeInteractiveHint(itemId)

    def cancel(self, scopeType, scopeName):
        _logger.debug('Hint cancel. scopeType: %r, scopeName: %r., _hintsDict: %r', scopeType, scopeName, self._hintsDict)
        if scopeType == GUIEffectScope.COMPONENT and scopeName in self._hintsDict:
            self.stop(scopeName)
        elif scopeType == GUIEffectScope.SCENE:
            self.stop()


class ShowOnceOnlyHint(ShowChainHint):
    __slots__ = ()

    def stop(self, effectID=None, effectSubType=None):
        if effectID is not None:
            super(ShowOnceOnlyHint, self).stop(effectID)
        return


class SetCriteriaEffect(ApplicationEffect):
    __slots__ = ()

    def play(self, effectData):
        itemID, value = effectData
        layout = self._getTutorialLayout()
        if layout is not None:
            layout.setCriteria(itemID, value)
            return True
        else:
            return False


_ACTION_TO_TRIGGER_TYPE = {GuiEventType.CLICK: TUTORIAL_TRIGGER_TYPES.CLICK_TYPE,
 GuiEventType.CLICK_OUTSIDE: TUTORIAL_TRIGGER_TYPES.CLICK_OUTSIDE_TYPE,
 GuiEventType.ESC: TUTORIAL_TRIGGER_TYPES.ESCAPE,
 GuiEventType.ENABLE: TUTORIAL_TRIGGER_TYPES.ENABLED,
 GuiEventType.DISABLE: TUTORIAL_TRIGGER_TYPES.DISABLED,
 GuiEventType.ENABLED_CHANGE: TUTORIAL_TRIGGER_TYPES.ENABLED_CHANGE,
 GuiEventType.VISIBLE_CHANGE: TUTORIAL_TRIGGER_TYPES.VISIBLE_CHANGE}

class SetTriggerEffect(ApplicationEffect):
    __slots__ = ('_triggersByItem',)

    def __init__(self):
        super(SetTriggerEffect, self).__init__()
        self._triggersByItem = defaultdict(list)

    def play(self, effectData):
        itemID, actionType = effectData
        if actionType not in _ACTION_TO_TRIGGER_TYPE:
            _logger.error('Cannot find trigger type. itemID: %r, actionType: %r', itemID, actionType)
            return False
        else:
            triggerType = _ACTION_TO_TRIGGER_TYPE[actionType]
            layout = self._getTutorialLayout()
            if layout is None:
                return False
            itemTriggers = self._triggersByItem[itemID]
            if itemID in itemTriggers:
                _logger.error('Trigger is already set for item. itemID: %r, triggerType: %r', itemID, triggerType)
                return False
            itemTriggers.append(triggerType)
            layout.setTriggers(itemID, itemTriggers)
            return True

    def stop(self, effectID=None, effectSubType=None):
        layout = self._getTutorialLayout()
        itemID, actionType = effectID, effectSubType
        if itemID is None:
            if layout is not None:
                for _itemID in self._triggersByItem.iterkeys():
                    layout.clearTriggers(_itemID)

            self._triggersByItem.clear()
        elif actionType is None:
            if itemID in self._triggersByItem:
                if layout is not None:
                    layout.clearTriggers(itemID)
                del self._triggersByItem[itemID]
        elif itemID in self._triggersByItem:
            itemTriggers = self._triggersByItem[itemID]
            if actionType in _ACTION_TO_TRIGGER_TYPE:
                triggerType = _ACTION_TO_TRIGGER_TYPE[actionType]
                if triggerType in itemTriggers:
                    itemTriggers.remove(triggerType)
                    if layout is not None:
                        if itemTriggers:
                            layout.setTriggers(itemID, itemTriggers)
                        else:
                            layout.clearTriggers(itemID)
                    if not itemTriggers:
                        del self._triggersByItem[itemID]
            else:
                _logger.error('Cannot find trigger type. itemID: %r, actionType: %r', itemID, actionType)
        return


class EffectsPlayer(object):
    __slots__ = ('_effects',)

    def __init__(self, effects):
        super(EffectsPlayer, self).__init__()
        self._effects = effects

    def iterEffects(self):
        for name, effect in self._effects.iteritems():
            yield (name, effect)

    def filterByName(self, *names):
        for name, effect in self._effects.iteritems():
            if name in names:
                yield effect

    def clear(self):
        while self._effects:
            _, effect = self._effects.popitem()
            effect.clear()

    def play(self, effectName, effectData):
        result = False
        if effectName in self._effects:
            result = self._effects[effectName].play(effectData)
        else:
            _logger.error('GUI effect %r not found', effectName)
        return result

    def stop(self, effectName, effectID, effectSubType=None):
        if effectName in self._effects:
            self._effects[effectName].stop(effectID=effectID, effectSubType=effectSubType)
        else:
            _logger.error('GUI effect %r not found', effectName)

    def cancel(self, scopeType, scopeName):
        for effect in self._effects.itervalues():
            effect.cancel(scopeType, scopeName)

    def stopAll(self):
        for effect in self._effects.itervalues():
            effect.stop()

    def isStillRunning(self, effectName, effectID=None, effectSubType=None):
        result = False
        if effectName in self._effects:
            result = self._effects[effectName].isStillRunning(effectID=effectID, effectSubType=effectSubType)
        else:
            _logger.error('GUI effect %r not found', effectName)
        return result
