# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/impl/gui_impl.py
import typing
import logging
from collections import defaultdict
from Event import Event, EventManager
from gui.Scaleform.genConsts.TUTORIAL_EFFECT_TYPES import TUTORIAL_EFFECT_TYPES
from gui.Scaleform.genConsts.TUTORIAL_TRIGGER_TYPES import TUTORIAL_TRIGGER_TYPES
from gui.impl.gen.view_models.common.tutorial.component_description_model import ComponentDescriptionModel
from gui.impl.gen.view_models.common.tutorial.criterion_model import CriterionModel
from gui.impl.gen.view_models.common.tutorial.triggers_model import TriggersModel
from gui.impl.gen.view_models.common.tutorial.view_criterion_model import ViewCriterionModel
from gui.impl.gen.view_models.common.tutorial.view_description_model import ViewDescriptionModel
from gui.impl.gen.view_models.common.tutorial.tutorial_model import TutorialModel
from gui.impl.gui_decorators import args2params
from gui.impl.utils.data import findIndexes, findItems
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from tutorial.gui import GuiType, IGuiImpl
from soft_exception import SoftException
from tutorial.gui.impl import effects as effects_impl
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.ui_kit.list_model import ListModel
    from gui.impl.gen.view_models.common.tutorial.descriptions_model import DescriptionsModel
    from gui.impl.gen.view_models.common.tutorial.effect_model import EffectModel
    from skeletons.tutorial import ComponentID
    from tutorial.gui import ComponentDescr
_logger = logging.getLogger(__name__)

class WulfGuiImpl(IGuiImpl):
    __slots__ = ('__model', '__proxy', '__eventMgr', '__effectsFactory')
    _SUPPORTED_TRIGGERS = frozenset((TUTORIAL_TRIGGER_TYPES.ENABLED,
     TUTORIAL_TRIGGER_TYPES.DISABLED,
     TUTORIAL_TRIGGER_TYPES.VISIBLE_CHANGE,
     TUTORIAL_TRIGGER_TYPES.ENABLED_CHANGE,
     TUTORIAL_TRIGGER_TYPES.ESCAPE))
    _FORCE_PROXIED_TRIGGERS = frozenset((TUTORIAL_TRIGGER_TYPES.ESCAPE,))
    _PROXIED_TRIGGERS = frozenset(TUTORIAL_TRIGGER_TYPES.ALL) - _SUPPORTED_TRIGGERS | _FORCE_PROXIED_TRIGGERS
    _SUPPORTED_EFFECTS = frozenset((TUTORIAL_EFFECT_TYPES.DISPLAY, TUTORIAL_EFFECT_TYPES.ENABLED))

    def __init__(self, proxy):
        super(WulfGuiImpl, self).__init__()
        self.__effectsFactory = effects_impl.getFactory()
        self.__proxy = proxy
        guiLoader = dependency.instance(IGuiLoader)
        self.__model = typing.cast(TutorialModel, guiLoader.tutorial.getModel())
        self.__model.onComponentFound += self.__onComponentFound
        self.__model.onComponentDisposed += self.__onComponentDisposed
        self.__model.onEffectCompleted += self.__onEffectCompleted
        self.__model.onTriggerActivated += self.__onTriggerActivated
        self.__eventMgr = EventManager()
        self.onComponentFound = Event(self.__eventMgr)
        self.onComponentDisposed = Event(self.__eventMgr)
        self.onTriggerActivated = Event(self.__eventMgr)
        self.onEffectCompleted = Event(self.__eventMgr)
        self.onInit = Event(self.__eventMgr)

    def showEffect(self, componentId, viewId, effectType, effectData, effectBuilder=''):
        if effectType not in self._SUPPORTED_EFFECTS:
            self.__proxy.showEffect(componentId, viewId, effectType, effectData, effectBuilder)
            return

        def _findPredicate(ef):
            return ef.getComponentId() == componentId and ef.getViewId() == viewId and ef.getType() == effectType and ef.getBuilder() == effectBuilder

        foundEffects = findItems(self.__model.effects.getItems(), _findPredicate)
        with self.__model.effects.transaction() as effects:
            if foundEffects:
                effect = foundEffects[0]
            else:
                effect = self.__effectsFactory.createEffect(effectType)
                if effect:
                    effect.setComponentId(componentId)
                    effect.setViewId(viewId)
                    effect.setBuilder(effectBuilder)
                    effects.getItems().addViewModel(effect)
                    effects.getItems().invalidate()
            if effect:
                self.__effectsFactory.updateEffect(effect, effectData)

    def hideEffect(self, componentId, viewId, effectType, effectBuilder=''):
        if effectType not in self._SUPPORTED_EFFECTS:
            self.__proxy.hideEffect(componentId, viewId, effectType, effectBuilder)
            return

        def _predicate(e):
            return e.getViewId() == viewId and e.getComponentId() == componentId and e.getType() == effectType and e.getBuilder() == effectBuilder

        effects = self.__model.effects.getItems()
        indexes = findIndexes(effects, _predicate)
        if indexes:
            effects.removeValues(indexes)
            effects.invalidate()

    def setDescriptions(self, descriptions):
        views = defaultdict(ViewDescriptionModel)
        for descr in descriptions:
            cmpDescr = ComponentDescriptionModel()
            cmpDescr.setViewId(descr.viewId)
            cmpDescr.setComponentId(descr.ID)
            cmpDescr.setPath(descr.path)
            views[descr.viewId].getComponents().addViewModel(cmpDescr)
            views[descr.viewId].setViewId(descr.viewId)

        with self.__model.descriptions.transaction() as descriptionsModel:
            for view in views.values():
                descriptionsModel.getViews().addViewModel(view)

            descriptionsModel.getViews().invalidate()

    def setSystemEnabled(self, enabled):
        self.__model.setEnabled(enabled)

    def setCriteria(self, name, value):
        with self.__model.criteria.transaction() as criteria:
            items = criteria.getItems()
            foundCriteria = findItems(items, lambda item: item.getName() == name)
            if foundCriteria:
                criterion = foundCriteria[0]
            else:
                criterion = CriterionModel()
                criterion.setName(name)
                items.addViewModel(criterion)
                items.invalidate()
            criterion.setValue(value)

    def setViewCriteria(self, componentId, viewUniqueName):
        with self.__model.viewCriteria.transaction() as viewCriteria:
            items = viewCriteria.getItems()
            criteria = findItems(items, lambda item: item.getComponentId() == componentId)
            if criteria:
                criterion = criteria[0]
            else:
                criterion = ViewCriterionModel()
                criterion.setComponentId(componentId)
                items.addViewModel(criterion)
                items.invalidate()
            criterion.setViewUniqueId(viewUniqueName)

    def setTriggers(self, componentId, triggers):

        def _findPredicate(trgrs):
            return trgrs.getComponentId() == componentId

        if not triggers:
            self.__proxy.setTriggers(componentId, triggers)
            foundIndexes = findIndexes(self.__model.triggers.getItems(), _findPredicate)
            if foundIndexes:
                self.__model.triggers.getItems().remove(foundIndexes[0])
                self.__model.triggers.getItems().invalidate()
            return
        allTriggers = set(triggers)
        proxiedTriggers = allTriggers & self._PROXIED_TRIGGERS
        if proxiedTriggers:
            self.__proxy.setTriggers(componentId, proxiedTriggers)
        supportedTriggers = allTriggers & self._SUPPORTED_TRIGGERS
        if supportedTriggers:
            with self.__model.triggers.transaction() as triggersList:
                foundTriggers = findItems(triggersList.getItems(), _findPredicate)
                if foundTriggers:
                    triggersModel = foundTriggers[0]
                    triggersModel.getTriggers().clear()
                else:
                    triggersModel = TriggersModel()
                    triggersModel.setComponentId(componentId)
                for trType in supportedTriggers:
                    triggersModel.getTriggers().addString(trType)

                triggersModel.getTriggers().invalidate()
                if not foundTriggers:
                    triggersList.getItems().addViewModel(triggersModel)
                    triggersList.getItems().invalidate()

    def supportedViewTypes(self):
        return (GuiType.WULF,)

    def isInited(self):
        return self.__model is not None

    def fini(self):
        self.clear()
        self.__eventMgr.clear()
        if self.__model is not None:
            self.__model.onComponentFound -= self.__onComponentFound
            self.__model.onComponentDisposed -= self.__onComponentDisposed
            self.__model.onEffectCompleted -= self.__onEffectCompleted
            self.__model.onTriggerActivated -= self.__onTriggerActivated
        self.__model = None
        self.__proxy = None
        return

    def clear(self):
        if self.__model is not None:
            self.__model.descriptions.getViews().clear()
            self.__model.effects.getItems().clear()
            self.__model.triggers.getItems().clear()
            self.__model.criteria.getItems().clear()
            self.__model.viewCriteria.getItems().clear()
            self.__model.foundComponents.getItems().clear()
        return

    def __onComponentFound(self, args):
        componentId = args['componentId']
        viewId = args['viewId']
        self.onComponentFound(componentId, viewId)

    def __onComponentDisposed(self, args):
        componentId = args['componentId']
        self.onComponentDisposed(componentId)

    @args2params(str, str, str, str)
    def __onEffectCompleted(self, componentId, viewId, effectType, effectBuilder):

        def _predicate(e):
            return e.getComponentId() == componentId and e.getViewId() == viewId and effectType == e.getType() and effectBuilder == e.getBuilder()

        effects = self.__model.effects.getItems()
        indexes = findIndexes(effects, _predicate)
        if not indexes:
            raise SoftException("Can't find effect. viewId: {}, componentId: {}, type: {}".format(viewId, componentId, effectType))
        effects.remove(indexes[0])
        effects.invalidate()
        self.onEffectCompleted(componentId, effectType)

    @args2params(str, str, bool)
    def __onTriggerActivated(self, componentId, triggerType, state):
        self.onTriggerActivated(componentId, triggerType, state)
