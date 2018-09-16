# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/managers/TutorialManager.py
from collections import defaultdict
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.framework.entities.abstract.TutorialManagerMeta import TutorialManagerMeta
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from gui.Scaleform.genConsts.TUTORIAL_EFFECT_TYPES import TUTORIAL_EFFECT_TYPES as _EFFECT_TYPES
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.TUTORIAL_EFFECT_BUILDERS import TUTORIAL_EFFECT_BUILDERS
try:
    from tutorial.doc_loader import gui_config
except ImportError:
    LOG_ERROR('Can not load package tutorial')

    class gui_config(object):

        @classmethod
        def readConfig(cls, path, forced=False):
            return None


_Event = events.TutorialEvent
_TRIGGER_TYPES = TUTORIAL_TRIGGER_TYPES
_EFFECT_COMPLETE_EVENTS = {_EFFECT_TYPES.TWEEN: _Event.ON_ANIMATION_COMPLETE,
 _EFFECT_TYPES.CLIP: _Event.ON_ANIMATION_COMPLETE}
_COMPONENT_PROPERTY_EFFECTS = {_EFFECT_TYPES.DISPLAY: ('visible',),
 _EFFECT_TYPES.ENABLED: ('enabled',),
 _EFFECT_TYPES.LAYOUT: ('layout',)}

class _ComponentViewBinding(object):
    __slots__ = ('alias', 'desiredUniqueName', 'actualUniqueName')

    def __init__(self, alias, desiredUniqueName=None):
        self.alias = alias
        self.desiredUniqueName = desiredUniqueName
        self.actualUniqueName = None
        return


class TutorialManager(TutorialManagerMeta):

    def __init__(self, app, isEnabled=False, path=''):
        super(TutorialManager, self).__init__()
        self._isEnabled = isEnabled
        self._componentViewBindings = {}
        self._components = set()
        self._componentProps = {}
        self._pendingComponentAnimations = {}
        self.setEnvironment(app)
        if isEnabled:
            self._config = gui_config.readConfig(path)
        else:
            self._config = None
        self.__hangarMenuButtonsOverride = None
        self.__headerMenuButtonsOverride = None
        self.__hangarHeaderEnabled = True
        self.__battleSelectorHintOverride = None
        return

    @property
    def lastHangarMenuButtonsOverride(self):
        return self.__hangarMenuButtonsOverride

    @property
    def lastHeaderMenuButtonsOverride(self):
        return self.__headerMenuButtonsOverride

    @property
    def hangarHeaderEnabled(self):
        return self.__hangarHeaderEnabled

    @property
    def lastBattleSelectorHintOverride(self):
        return self.__battleSelectorHintOverride

    def getViewTutorialID(self, name):
        return None if not self._isEnabled else name

    def getFoundComponentsIDs(self):
        return self._components

    def setCriteria(self, name, value):
        self.as_setCriteriaS(name, value)

    def setViewCriteria(self, componentID, viewUniqueName):
        self._componentViewBindings[componentID].desiredUniqueName = viewUniqueName
        self.as_setComponentViewCriteriaS(componentID, viewUniqueName)

    def setTriggers(self, componentID, triggers):
        if not self._validate(componentID):
            return
        self.as_setTriggersS(componentID, triggers)

    def clearTriggers(self, componentID):
        self.setTriggers(componentID, ())

    def showInteractiveHint(self, componentID, content, triggers=None):
        if not self._validate(componentID):
            return False
        elif componentID not in self._components:
            LOG_ERROR('showInteractiveHint - target component is not on scene!', componentID)
            return False
        else:
            if 'padding' not in content:
                content['padding'] = self._config.getItem(componentID).padding
            self.__doShowEffect(componentID, _EFFECT_TYPES.HINT, content)
            if triggers is not None:
                self.as_setTriggersS(componentID, triggers)
            return True

    def closeInteractiveHint(self, componentID):
        if not self._validate(componentID):
            return
        self.as_setTriggersS(componentID, ())
        self.__doHideEffect(componentID, _EFFECT_TYPES.HINT)

    def setComponentProps(self, componentID, props):
        if not self._validate(componentID):
            return False
        if not props:
            return True
        self._componentProps.setdefault(componentID, {}).update(props)
        if componentID in self._components:
            self.__doSetComponentProps(componentID, props)
        return True

    def playComponentAnimation(self, componentID, animType):
        if not self._validate(componentID):
            return False
        else:
            animParams = self._config.getItem(componentID).anim.get(animType, None)
            if animParams is None:
                LOG_ERROR('invalid animation type', animType)
                return False
            if componentID in self._components:
                self.__doShowEffect(componentID, animType, animParams)
            elif componentID not in self._pendingComponentAnimations:
                LOG_DEBUG('deferring playComponentAnimation (component not yet on scene)', componentID, animType, animParams)
                self._pendingComponentAnimations[componentID] = (animType, animParams)
            else:
                LOG_ERROR('playComponentAnimation call already deferred - ignoring another one', componentID, animType, animParams)
            return True

    def stopComponentAnimation(self, componentID, animType):
        if not self._validate(componentID):
            return
        else:
            LOG_DEBUG('stopComponentAnimation', componentID, animType)
            if componentID in self._components:
                self.__doHideEffect(componentID, animType)
            else:
                deferredAnim = self._pendingComponentAnimations.get(componentID)
                if deferredAnim is not None:
                    deferredAnimType, _ = deferredAnim
                    if deferredAnimType == animType:
                        LOG_DEBUG('canceling deferred playComponentAnimation call', componentID, self._pendingComponentAnimations[componentID])
                        del self._pendingComponentAnimations[componentID]
                    else:
                        LOG_ERROR('last deferred playComponentAnimation call had a different type', componentID, animType, deferredAnimType)
            return

    def showBootcampHint(self, componentID):
        if not self._validate(componentID):
            return False
        if componentID not in self._components:
            LOG_ERROR('showBootcampHint - target component is not on scene!', componentID)
            return False
        params = self._config.getItem(componentID).bootcampHint
        LOG_DEBUG('showBootcampHint', componentID, params)
        self.__doShowEffect(componentID, _EFFECT_TYPES.BOOTCAMP_HINT, params)
        return True

    def hideBootcampHint(self, componentID):
        if not self._validate(componentID):
            return
        LOG_DEBUG('hideBootcampHint', componentID)
        self.__doHideEffect(componentID, _EFFECT_TYPES.BOOTCAMP_HINT)

    def setupViewContextHints(self, viewTutorialID, hintsData):
        builder = hintsData.pop('builderLnk', TUTORIAL_EFFECT_BUILDERS.DEFAULT_OVERLAY)
        effectData = {'data': hintsData,
         'builderLnk': builder}
        self.as_showEffectS(viewTutorialID, '', effectData)

    def onComponentFound(self, componentID, viewTutorialID):
        LOG_DEBUG('onComponentFound', componentID, viewTutorialID)
        bindings = self._componentViewBindings[componentID]
        if bindings.desiredUniqueName is not None and bindings.desiredUniqueName != viewTutorialID:
            LOG_ERROR('ignoring onComponentFound in unexpected view instance - expected', bindings.desiredUniqueName)
            return
        else:
            self._components.add(componentID)
            bindings.actualUniqueName = viewTutorialID
            props = self._componentProps.get(componentID, None)
            if props:
                self.__doSetComponentProps(componentID, props)
            deferredAnim = self._pendingComponentAnimations.pop(componentID, None)
            if deferredAnim is not None:
                animType, animParams = deferredAnim
                self.__doShowEffect(componentID, animType, animParams)
            self.fireEvent(_Event(_Event.ON_COMPONENT_FOUND, targetID=componentID), scope=EVENT_BUS_SCOPE.GLOBAL)
            return

    def onComponentDisposed(self, componentID):
        LOG_DEBUG('onComponentDisposed', componentID)
        self._components.discard(componentID)
        self._componentViewBindings[componentID].actualUniqueName = None
        self.fireEvent(_Event(_Event.ON_COMPONENT_LOST, targetID=componentID), scope=EVENT_BUS_SCOPE.GLOBAL)
        return

    def onTriggerActivated(self, componentID, triggerType):
        self.fireEvent(_Event(_Event.ON_TRIGGER_ACTIVATED, targetID=componentID, settingsID=triggerType), scope=EVENT_BUS_SCOPE.GLOBAL)

    def onEffectCompleted(self, componentID, effectType):
        LOG_DEBUG('onEffectCompleted', componentID, effectType)
        eventType = _EFFECT_COMPLETE_EVENTS.get(effectType, None)
        if eventType is not None:
            self.fireEvent(_Event(eventType, targetID=componentID, settingsID=effectType), scope=EVENT_BUS_SCOPE.GLOBAL)
        return

    def overrideHangarMenuButtons(self, buttonsList=None):
        if buttonsList != self.__hangarMenuButtonsOverride:
            self.__hangarMenuButtonsOverride = buttonsList
            self.fireEvent(_Event(_Event.OVERRIDE_HANGAR_MENU_BUTTONS, targetID=buttonsList), scope=EVENT_BUS_SCOPE.LOBBY)

    def overrideHeaderMenuButtons(self, buttonsList=None):
        if buttonsList != self.__headerMenuButtonsOverride:
            self.__headerMenuButtonsOverride = buttonsList
            self.fireEvent(_Event(_Event.OVERRIDE_HEADER_MENU_BUTTONS, targetID=buttonsList), scope=EVENT_BUS_SCOPE.LOBBY)

    def setHangarHeaderEnabled(self, enabled):
        if enabled != self.__hangarHeaderEnabled:
            self.__hangarHeaderEnabled = enabled
            self.fireEvent(_Event(_Event.SET_HANGAR_HEADER_ENABLED, targetID=enabled), scope=EVENT_BUS_SCOPE.LOBBY)

    def overrideBattleSelectorHint(self, overrideType=None):
        if overrideType != self.__battleSelectorHintOverride:
            self.__battleSelectorHintOverride = overrideType
            self.fireEvent(_Event(_Event.OVERRIDE_BATTLE_SELECTOR_HINT, targetID=overrideType), scope=EVENT_BUS_SCOPE.LOBBY)

    def clear(self):
        self.__hangarMenuButtonsOverride = None
        self.__headerMenuButtonsOverride = None
        self.__hangarHeaderEnabled = True
        self.__battleSelectorHintOverride = None
        self._componentProps.clear()
        self._pendingComponentAnimations.clear()
        return

    def _populate(self):
        super(TutorialManager, self)._populate()
        self.as_setSystemEnabledS(self._isEnabled)
        if self._isEnabled and self._config:
            descriptions = defaultdict(list)
            for componentID, item in self._config.getItems():
                descriptions[item.view].append({'id': componentID,
                 'viewName': item.view,
                 'path': item.path})
                self._componentViewBindings[componentID] = _ComponentViewBinding(item.view)

            self.as_setDescriptionsS(descriptions)

    def _validate(self, componentID):
        if not self._isEnabled or self._config is None:
            return False
        else:
            component = self._config.getItem(componentID)
            if component is None:
                LOG_ERROR('Component is not found', componentID)
                return False
            return True

    def _dispose(self):
        self._isEnabled = False
        self._config = None
        self._componentViewBindings.clear()
        self._components.clear()
        self.clear()
        super(TutorialManager, self)._dispose()
        return

    def __getComponentViewID(self, componentID):
        binding = self._componentViewBindings[componentID]
        if binding.desiredUniqueName is not None:
            return binding.desiredUniqueName
        else:
            return binding.actualUniqueName if binding.actualUniqueName is not None else binding.alias

    def __doShowEffect(self, componentID, effectType, effectData):
        viewTutorialID = self.__getComponentViewID(componentID)
        effectBuilder = self._config.getItem(componentID).effectBuilders.get(effectType, '')
        if not effectBuilder:
            LOG_ERROR('no effect builder specified for effect type', effectType, componentID)
        self.as_showEffectS(viewTutorialID, componentID, {'data': effectData,
         'builderLnk': effectBuilder})

    def __doHideEffect(self, componentID, effectType):
        viewTutorialID = self.__getComponentViewID(componentID)
        effectBuilder = self._config.getItem(componentID).effectBuilders.get(effectType, '')
        self.as_hideEffectS(viewTutorialID, componentID, effectBuilder)

    def __doSetComponentProps(self, componentID, props):
        props = props.copy()
        for effectType, propertyNames in _COMPONENT_PROPERTY_EFFECTS.iteritems():
            effectProps = {key:props.pop(key) for key in propertyNames if key in props}
            if effectProps:
                LOG_DEBUG('__doSetComponentProps: triggering AS effect', componentID, effectType, effectProps)
                self.__doShowEffect(componentID, effectType, effectProps)

        if props:
            LOG_ERROR('__doSetComponentProps: unsupported properties:', componentID, props)
