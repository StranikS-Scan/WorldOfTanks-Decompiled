# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/controller.py
import typing
import logging
from functools import partial
from gui.Scaleform.genConsts.TUTORIAL_EFFECT_TYPES import TUTORIAL_EFFECT_TYPES as _EFFECT_TYPES
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from gui.impl.gen import R
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from tutorial.gui import GuiType, ComponentDescr, IGuiImpl
from skeletons.tutorial import IGuiController
from soft_exception import SoftException
from tutorial.doc_loader import gui_config
if typing.TYPE_CHECKING:
    from gui.impl.gen_utils import DynAccessor
    from tutorial.data.client_triggers import ClientTriggers
    from skeletons.tutorial import ComponentID
_logger = logging.getLogger(__name__)
_Event = events.TutorialEvent
_TRIGGER_TYPES = TUTORIAL_TRIGGER_TYPES
_EFFECT_COMPLETE_EVENTS = {_EFFECT_TYPES.TWEEN: _Event.ON_ANIMATION_COMPLETE,
 _EFFECT_TYPES.CLIP: _Event.ON_ANIMATION_COMPLETE}
_COMPONENT_PROPERTY_EFFECTS = {_EFFECT_TYPES.DISPLAY: ('visible',),
 _EFFECT_TYPES.ENABLED: ('enabled',),
 _EFFECT_TYPES.LAYOUT: ('layout',)}
_R_VIEWS_PREFIX = 'R.views.'

def _isRView(path):
    return path.startswith(_R_VIEWS_PREFIX) if path else False


def _parseRView(view):

    def _reducer(result, cur):
        return result.dyn(cur)

    return reduce(_reducer, view[len(_R_VIEWS_PREFIX):].split('.'), R.views)


def _getComponentDescr(componentID, cfgItem):
    if _isRView(cfgItem.view):
        viewType = GuiType.WULF
        viewId = _parseRView(cfgItem.view)
        if not viewId.isValid():
            _logger.error("Can't parse component's view. componentID: %s, viewId: %s", componentID, cfgItem.view)
        viewId = str(viewId())
    else:
        viewType = GuiType.SCALEFORM
        viewId = cfgItem.view
    return ComponentDescr(componentID, viewType, viewId, cfgItem.path)


def _getViewFilter(supportedTypes):

    def _filterFunc(descr):
        return descr.viewType in supportedTypes

    return _filterFunc


class _ComponentViewBinding(object):
    __slots__ = ('alias', 'desiredUniqueName', 'actualUniqueName')

    def __init__(self, alias, desiredUniqueName=None):
        self.alias = alias
        self.desiredUniqueName = desiredUniqueName
        self.actualUniqueName = None
        return


class GuiController(IGuiController):
    __slots__ = ('__guiImpls', '_isEnabled', '_componentViewBindings', '_components', '_componentProps', '_pendingComponentAnimations', '__hintsWithClientTriggers', '_config', '__hangarMenuButtonsOverride', '__headerMenuButtonsOverride', '__hangarHeaderEnabled', '__battleSelectorHintOverride', '__onComponentFoundHandlers', '__descriptions')

    def __init__(self):
        super(GuiController, self).__init__()
        self.__guiImpls = []
        self._isEnabled = False
        self._config = None
        self._componentViewBindings = {}
        self._components = {}
        self._componentProps = {}
        self._pendingComponentAnimations = {}
        self.__hintsWithClientTriggers = None
        self.__onComponentFoundHandlers = {}
        self.__descriptions = []
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

    def setHintsWithClientTriggers(self, clientTriggers):
        self.__hintsWithClientTriggers = clientTriggers

    def getViewTutorialID(self, name):
        return None if not self._isEnabled else name

    def getFoundComponentsIDs(self):
        return self._components.keys()

    def setCriteria(self, name, value):
        for gui in self.__guiImpls:
            gui.setCriteria(name, value)

    def setViewCriteria(self, componentID, viewUniqueName):
        self._componentViewBindings[componentID].desiredUniqueName = viewUniqueName
        for gui in self.__guiImpls:
            gui.setViewCriteria(componentID, viewUniqueName)

    def setTriggers(self, componentID, triggers):
        if not self._validate(componentID):
            return
        if componentID not in self._components:
            _logger.error('setTriggers: component is not on scene!: %r', componentID)
            return
        self.__setTriggers(componentID, triggers)

    def clearTriggers(self, componentID):
        if self.__hintsWithClientTriggers is not None:
            self.__hintsWithClientTriggers.removeActiveHints()
            self.__hintsWithClientTriggers.updateRealState(componentID)
        self.__setTriggers(componentID, ())
        return

    def showInteractiveHint(self, componentID, content, triggers=None, silent=False):
        if not self._validate(componentID):
            return False
        elif componentID not in self._components:
            if not silent:
                _logger.error('showInteractiveHint - target component is not on scene!: %r', componentID)
            return False
        else:
            if 'padding' not in content:
                content['padding'] = self._config.getItem(componentID).padding
            self.__doShowEffect(componentID, _EFFECT_TYPES.HINT, content)
            if triggers is not None:
                triggers.extend(self.__getClientTrigger(componentID))
                self.__setTriggers(componentID, triggers)
            return True

    def closeInteractiveHint(self, componentID):
        if not self._validate(componentID):
            return
        if componentID in self._components:
            clientTriggers = self.__getClientTrigger(componentID)
            self.__setTriggers(componentID, clientTriggers)
            self.__doHideEffect(componentID, _EFFECT_TYPES.HINT)
        else:
            _logger.debug("closeInteractiveHint: can't find component: %s", componentID)

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
                _logger.error('invalid animation type: %r', animType)
                return False
            if componentID in self._components:
                self.__doShowEffect(componentID, animType, animParams)
            elif componentID not in self._pendingComponentAnimations:
                _logger.debug('deferring playComponentAnimation (component not yet on scene): %r, %r, %r', componentID, animType, animParams)
                self._pendingComponentAnimations[componentID] = (animType, animParams)
            else:
                _logger.error('playComponentAnimation call already deferred - ignoring another one: %r, %r, %r', componentID, animType, animParams)
            return True

    def stopComponentAnimation(self, componentID, animType):
        if not self._validate(componentID):
            return
        else:
            _logger.debug('stopComponentAnimation: %r, %r', componentID, animType)
            if componentID in self._components:
                self.__doHideEffect(componentID, animType)
            else:
                deferredAnim = self._pendingComponentAnimations.get(componentID)
                if deferredAnim is not None:
                    deferredAnimType, _ = deferredAnim
                    if deferredAnimType == animType:
                        _logger.debug('canceling deferred playComponentAnimation call: %r, %r', componentID, self._pendingComponentAnimations[componentID])
                        del self._pendingComponentAnimations[componentID]
                    else:
                        _logger.error('last deferred playComponentAnimation call had a different type: %r, %r, %r', componentID, animType, deferredAnimType)
            return

    def showBootcampHint(self, componentID):
        if not self._validate(componentID):
            return False
        if componentID not in self._components:
            _logger.error('showBootcampHint - target component is not on scene!: %r', componentID)
            return False
        params = self._config.getItem(componentID).bootcampHint
        _logger.debug('showBootcampHint: %r, %r', componentID, params)
        self.__doShowEffect(componentID, _EFFECT_TYPES.BOOTCAMP_HINT, params)
        return True

    def hideBootcampHint(self, componentID):
        if not self._validate(componentID):
            return
        if componentID not in self._components:
            _logger.error("hideBootcampHint: can't find component %s", componentID)
            return
        _logger.debug('hideBootcampHint: %r', componentID)
        self.__doHideEffect(componentID, _EFFECT_TYPES.BOOTCAMP_HINT)

    def setupViewContextHints(self, viewTutorialID, hintsData, hintsArgs=None):
        hintsDataCopy = hintsData.copy()
        for hint in hintsDataCopy.get('hints', []):
            hintArgs = hintsArgs.get(hint.get('tooltipSpecial'))
            if hintArgs is not None:
                hint['args'] = hintArgs

        builder = hintsDataCopy.pop('builderLnk', '')
        effectType = _EFFECT_TYPES.DEFAULT_OVERLAY
        for gui in self.__guiImpls:
            gui.showEffect('', viewTutorialID, effectType, hintsDataCopy, builder)

        return

    def overrideHangarMenuButtons(self, buttonsList=None):
        if buttonsList != self.__hangarMenuButtonsOverride:
            self.__hangarMenuButtonsOverride = buttonsList
            g_eventBus.handleEvent(_Event(_Event.OVERRIDE_HANGAR_MENU_BUTTONS, targetID=buttonsList), scope=EVENT_BUS_SCOPE.LOBBY)

    def overrideHeaderMenuButtons(self, buttonsList=None):
        if buttonsList != self.__headerMenuButtonsOverride:
            self.__headerMenuButtonsOverride = buttonsList
            g_eventBus.handleEvent(_Event(_Event.OVERRIDE_HEADER_MENU_BUTTONS, targetID=buttonsList), scope=EVENT_BUS_SCOPE.LOBBY)

    def setHangarHeaderEnabled(self, enabled):
        if enabled != self.__hangarHeaderEnabled:
            self.__hangarHeaderEnabled = enabled
            g_eventBus.handleEvent(_Event(_Event.SET_HANGAR_HEADER_ENABLED, targetID=enabled), scope=EVENT_BUS_SCOPE.LOBBY)

    def overrideBattleSelectorHint(self, overrideType=None):
        if overrideType != self.__battleSelectorHintOverride:
            self.__battleSelectorHintOverride = overrideType
            g_eventBus.handleEvent(_Event(_Event.OVERRIDE_BATTLE_SELECTOR_HINT, targetID=overrideType), scope=EVENT_BUS_SCOPE.LOBBY)

    def clear(self):
        _logger.debug('clear')
        self._isEnabled = False
        self._config = None
        self.__hangarMenuButtonsOverride = None
        self.__headerMenuButtonsOverride = None
        self.__hangarHeaderEnabled = True
        self.__battleSelectorHintOverride = None
        self.__hintsWithClientTriggers = None
        self._components.clear()
        self._componentProps.clear()
        self._componentViewBindings.clear()
        self._pendingComponentAnimations.clear()
        del self.__descriptions[:]
        self.__removeImplsListeners()
        for gui in self.__guiImpls:
            if gui.isInited():
                gui.setSystemEnabled(False)
            gui.clear()

        return

    def init(self, guiImpls):
        _logger.debug('init: %r', guiImpls)
        self.__guiImpls.extend(guiImpls)

    def setup(self, isEnabled=False, path=''):
        _logger.debug('setup: %r %r', isEnabled, path)
        self._isEnabled = isEnabled
        if isEnabled:
            self.__addImplsListeners()
            self._config = gui_config.readConfig(path)
            for componentID, item in self._config.getItems():
                cmpDescr = _getComponentDescr(componentID, item)
                self.__descriptions.append(cmpDescr)
                self._componentViewBindings[componentID] = _ComponentViewBinding(cmpDescr.viewId)

        else:
            self.__removeImplsListeners()
            self._config = None
        self.__tryToSetupGui()
        return

    def fini(self):
        _logger.debug('fini')
        self.clear()
        for gui in self.__guiImpls:
            gui.fini()

        del self.__guiImpls[:]
        self.__onComponentFoundHandlers.clear()

    def _validate(self, componentID):
        if not self._isEnabled or self._config is None:
            return False
        else:
            component = self._config.getItem(componentID)
            if component is None:
                _logger.error('Component is not found: %r', componentID)
                return False
            return True

    def _getGui(self, componentID):
        if componentID not in self._components:
            raise SoftException("Can't find component id: {}".format(componentID))
        return self._components[componentID]

    def __onComponentFound(self, gui, componentID, viewTutorialID):
        _logger.debug('onComponentFound: %r, %r', componentID, viewTutorialID)
        bindings = self._componentViewBindings[componentID]
        if bindings.desiredUniqueName is not None and bindings.desiredUniqueName != viewTutorialID:
            _logger.error('ignoring onComponentFound in unexpected view instance - expected: %r', bindings.desiredUniqueName)
            return
        else:
            self._components[componentID] = gui
            bindings.actualUniqueName = viewTutorialID
            props = self._componentProps.get(componentID, None)
            if props:
                self.__doSetComponentProps(componentID, props)
            deferredAnim = self._pendingComponentAnimations.pop(componentID, None)
            if deferredAnim is not None:
                animType, animParams = deferredAnim
                self.__doShowEffect(componentID, animType, animParams)
            clientTriggers = self.__getClientTrigger(componentID)
            if clientTriggers:
                self.__setTriggers(componentID, clientTriggers)
            g_eventBus.handleEvent(_Event(_Event.ON_COMPONENT_FOUND, targetID=componentID), scope=EVENT_BUS_SCOPE.GLOBAL)
            return

    def __onComponentDisposed(self, componentID):
        found = componentID in self._components
        _logger.debug('onComponentDisposed: %r %s', componentID, '' if found else '(not found)')
        self._componentViewBindings[componentID].actualUniqueName = None
        if self.__hintsWithClientTriggers is not None:
            self.__hintsWithClientTriggers.updateRealState(componentID)
            self.__hintsWithClientTriggers.removeActiveHints()
        g_eventBus.handleEvent(_Event(_Event.ON_COMPONENT_LOST, targetID=componentID), scope=EVENT_BUS_SCOPE.GLOBAL)
        self._components.pop(componentID, None)
        return

    def __onTriggerActivated(self, componentID, triggerType, state):
        g_eventBus.handleEvent(_Event(_Event.ON_TRIGGER_ACTIVATED, targetID=componentID, settingsID=triggerType, state=state), scope=EVENT_BUS_SCOPE.GLOBAL)

    def __onEffectCompleted(self, componentID, effectType):
        _logger.debug('onEffectCompleted: %r, %r', componentID, effectType)
        eventType = _EFFECT_COMPLETE_EVENTS.get(effectType, None)
        if eventType is not None:
            g_eventBus.handleEvent(_Event(eventType, targetID=componentID, settingsID=effectType), scope=EVENT_BUS_SCOPE.GLOBAL)
        return

    def __tryToSetupGui(self):
        if not any([ not api.isInited() for api in self.__guiImpls ]):
            self.__setEnabled()
            self.__setDescriptions()

    def __onGuiInited(self):
        self.__tryToSetupGui()

    def __setEnabled(self):
        for gui in self.__guiImpls:
            gui.setSystemEnabled(self._isEnabled)

    def __setDescriptions(self):
        if self._isEnabled and self.__descriptions:
            for gui in self.__guiImpls:
                gui.setDescriptions(filter(_getViewFilter(gui.supportedViewTypes()), self.__descriptions))

    def __setTriggers(self, componentID, triggers):
        triggers = triggers or ()
        gui = self._components.get(componentID)
        if gui:
            gui.setTriggers(componentID, triggers)
        else:
            _logger.info('clearTriggers: component is not on scene: %r', componentID)
            for gui in self.__guiImpls:
                gui.setTriggers(componentID, triggers)

    def __getComponentViewID(self, componentID):
        binding = self._componentViewBindings[componentID]
        if binding.desiredUniqueName is not None:
            return binding.desiredUniqueName
        else:
            return binding.actualUniqueName if binding.actualUniqueName is not None else binding.alias

    def __doShowEffect(self, componentID, effectType, effectData):
        viewTutorialID = self.__getComponentViewID(componentID)
        effectBuilder = self._config.getItem(componentID).effectBuilders.get(effectType, '')
        gui = self._getGui(componentID)
        _logger.debug('showEffect: %r %r %r %r %r', componentID, viewTutorialID, effectType, effectData, effectBuilder)
        gui.showEffect(componentID, viewTutorialID, effectType, effectData, effectBuilder)

    def __doHideEffect(self, componentID, effectType):
        _logger.debug('hideEffect: %s %s', componentID, effectType)
        viewTutorialID = self.__getComponentViewID(componentID)
        effectBuilder = self._config.getItem(componentID).effectBuilders.get(effectType, '')
        gui = self._getGui(componentID)
        gui.hideEffect(componentID, viewTutorialID, effectType, effectBuilder)

    def __doSetComponentProps(self, componentID, props):
        props = props.copy()
        for effectType, propertyNames in _COMPONENT_PROPERTY_EFFECTS.iteritems():
            effectProps = {key:props.pop(key) for key in propertyNames if key in props}
            if effectProps:
                _logger.debug('__doSetComponentProps: triggering AS effect: %r, %r, %r', componentID, effectType, effectProps)
                self.__doShowEffect(componentID, effectType, effectProps)

        if props:
            _logger.error('__doSetComponentProps: unsupported properties: %r, %r', componentID, props)

    def __getClientTrigger(self, componentID):
        if self.__hintsWithClientTriggers is None:
            return
        else:
            triggers = self.__hintsWithClientTriggers.getNeededTriggersForComponent(componentID)
            return triggers

    def __addImplsListeners(self):
        for gui in self.__guiImpls:
            self.__onComponentFoundHandlers[gui] = partial(self.__onComponentFound, gui)
            gui.onComponentFound += self.__onComponentFoundHandlers[gui]
            gui.onComponentDisposed += self.__onComponentDisposed
            gui.onTriggerActivated += self.__onTriggerActivated
            gui.onEffectCompleted += self.__onEffectCompleted
            gui.onInit += self.__onGuiInited

    def __removeImplsListeners(self):
        for gui in self.__guiImpls:
            if self.__onComponentFoundHandlers:
                gui.onComponentFound -= self.__onComponentFoundHandlers.pop(gui)
            gui.onComponentDisposed -= self.__onComponentDisposed
            gui.onTriggerActivated -= self.__onTriggerActivated
            gui.onEffectCompleted -= self.__onEffectCompleted
            gui.onInit -= self.__onGuiInited
