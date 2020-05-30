# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/effects_player.py
import logging
from collections import defaultdict
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from tutorial.data.events import GuiEventType
from shared_utils import first
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

    def _getContainer(self, viewType):
        if self._app is None:
            return
        else:
            manager = self._app.containerManager
            return None if manager is None else manager.getContainer(viewType)

    def _getTutorialLayout(self):
        return None if self._app is None else self._app.tutorialManager


class ComponentEffect(GUIEffect):
    __slots__ = ('_component',)

    def __init__(self):
        super(ComponentEffect, self).__init__()
        self._component = None
        return

    def clear(self):
        self._component = None
        super(ComponentEffect, self).clear()
        return

    def setComponent(self, component):
        self._component = component

    def play(self, effectData):
        if self._component is not None:
            return self._doPlay(effectData)
        else:
            _logger.error('Component still is not found to play effect %r', self)
            return False

    def _doPlay(self, effectData):
        raise NotImplementedError


class ShowDialogEffect(ApplicationEffect):
    __slots__ = ('_aliasMap', '_dialogID')

    def __init__(self, aliasMap):
        super(ShowDialogEffect, self).__init__()
        self._aliasMap = aliasMap
        self._dialogID = None
        return

    def clear(self):
        self._dialogID = None
        super(ShowDialogEffect, self).clear()
        return

    def play(self, effectData):
        effectData = effectData[0]
        result = False
        if 'type' in effectData and 'dialogID' in effectData:
            dialogType = effectData['type']
            dialogID = effectData['dialogID']
            if dialogID == self._dialogID:
                _logger.error('Dialog is displayed %r', effectData['dialogID'])
                return False
            if dialogType in self._aliasMap:
                alias = self._aliasMap[dialogType]
                self._dialogID = dialogID
                self._app.loadView(SFViewLoadParams(alias, dialogID), effectData)
                result = True
            else:
                _logger.error('Alias of dialog not found. effectData: %r, aliasMap: %r', effectData, self._aliasMap)
        else:
            _logger.error('Type or id of dialog not found %r', effectData)
        return result

    def stop(self, effectID=None, effectSubType=None):
        isForceStop = effectID is None
        if not isForceStop and effectID != self._dialogID:
            _logger.error('Dialog is not opened %r', effectID)
            return
        else:
            effectID = self._dialogID
            self._dialogID = None
            container = self._getContainer(ViewTypes.TOP_WINDOW)
            if container is not None:
                dialog = container.getView(criteria={POP_UP_CRITERIA.UNIQUE_NAME: effectID})
                if dialog is not None:
                    dialog.destroy()
            return

    def isStillRunning(self, effectID=None, effectSubType=None):
        if effectID is not None:
            result = self._dialogID == effectID
        else:
            result = self._dialogID is not None
        return result


class ShowWindowEffect(ApplicationEffect):
    __slots__ = ('_aliasMap', '_windowIDs')

    def __init__(self, aliasMap):
        super(ShowWindowEffect, self).__init__()
        self._aliasMap = aliasMap
        self._windowIDs = set()

    def clear(self):
        self._windowIDs.clear()
        super(ShowWindowEffect, self).clear()

    def play(self, effectData):
        windowID, windowType, content = effectData
        result = False
        if windowType in self._aliasMap:
            alias = self._aliasMap[windowType]
            self._windowIDs.add(windowID)
            self._app.loadView(SFViewLoadParams(alias, windowID), content)
            result = True
        else:
            _logger.error('Alias of window not found %r %r', windowType, self._aliasMap)
        return result

    def stop(self, effectID=None, effectSubType=None):
        isForceStop = effectID is None
        if not isForceStop:
            if effectID not in self._windowIDs:
                _logger.error('Window is not opened %r', effectID)
                return
            effectIDs = {effectID}
        else:
            effectIDs = self._windowIDs.copy()
        container = self._getContainer(ViewTypes.WINDOW)
        if container is None:
            container = self._getContainer(ViewTypes.OVERLAY)
        if container is not None:
            getView = container.getView
            for eID in effectIDs:
                window = getView(criteria={POP_UP_CRITERIA.UNIQUE_NAME: eID})
                if window is not None:
                    window.destroy()
                    self._windowIDs.remove(eID)
                if not isForceStop:
                    _logger.error('Window is not opened %r', eID)

        return

    def isStillRunning(self, effectID=None, effectSubType=None):
        if effectID is not None:
            result = effectID in self._windowIDs
        else:
            result = len(self._windowIDs)
        return result


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
        hintProps, triggers = effectData
        if hintProps.hintID in self._hintsDict:
            _logger.debug('Hint %r is already added', hintProps.hintID)
            return True
        else:
            layout = self._getTutorialLayout()
            if layout is not None:
                self._hintsDict.update({hintProps.hintID: hintProps.itemID})
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
                return layout.showInteractiveHint(hintProps.itemID, content, triggers)
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


class UpdateContentEffect(ApplicationEffect):
    __slots__ = ()

    def play(self, effectData):
        effectData = effectData[0]
        result = False
        effectID = None
        viewType = None
        if 'dialogID' in effectData:
            effectID = effectData['dialogID']
            viewType = ViewTypes.TOP_WINDOW
        if effectID is not None:
            container = self._getContainer(viewType)
            if container is not None:
                view = container.getView(criteria={POP_UP_CRITERIA.UNIQUE_NAME: effectID})
                if view is not None:
                    if hasattr(view, 'as_updateContentS'):
                        view.as_updateContentS(effectData)
                        result = True
                    else:
                        _logger.error('View %r is invalid', view)
                else:
                    _logger.debug('View is not on scene. effectID: %r', effectID)
                    result = True
        return result


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


class SetViewCriteriaEffect(ApplicationEffect):
    __slots__ = ()

    def play(self, effectData):
        itemIDs, value = effectData
        layout = self._getTutorialLayout()
        if layout is not None:
            for itemID in itemIDs:
                layout.setViewCriteria(itemID, value)

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


class SetItemPropsEffect(ApplicationEffect):
    __slots__ = ()

    def play(self, effectData):
        itemID, props = effectData
        layout = self._getTutorialLayout()
        return False if layout is None else layout.setComponentProps(itemID, props)


class PlayAnimationEffect(ApplicationEffect):
    __slots__ = ('_activeEffects',)

    def __init__(self):
        super(PlayAnimationEffect, self).__init__()
        self._activeEffects = {}

    def isStillRunning(self, effectID=None, effectSubType=None):
        return first(self._iterEffects(effectID, effectSubType)) is not None

    def play(self, effectData):
        itemID, animID = effectData
        if itemID in self._activeEffects:
            _logger.error('Another animation is already playing on item %r. ' + 'Multiple animations on one item are not supported.', itemID)
            return False
        layout = self._getTutorialLayout()
        if layout is None:
            return False
        elif layout.playComponentAnimation(itemID, animID):
            self._activeEffects[itemID] = animID
            return True
        else:
            return False

    def stop(self, effectID=None, effectSubType=None):
        layout = self._getTutorialLayout()
        if layout is None:
            return
        else:
            for itemID, animID in self._iterEffects(effectID, effectSubType):
                layout.stopComponentAnimation(itemID, animID)
                del self._activeEffects[itemID]

            return

    def cancel(self, scopeType, scopeName):
        if scopeType == GUIEffectScope.COMPONENT:
            self.stop(scopeName)

    def _iterEffects(self, effectID, effectSubType):
        itemID, animID = effectID, effectSubType
        if itemID is None:
            items = self._activeEffects.items()
        elif itemID in self._activeEffects:
            items = ((itemID, self._activeEffects[itemID]),)
        else:
            items = ()
        for _itemID, _animID in items:
            if animID in (_animID, None):
                yield (_itemID, _animID)

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
