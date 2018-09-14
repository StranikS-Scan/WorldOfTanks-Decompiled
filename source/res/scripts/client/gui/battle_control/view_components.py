# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/view_components.py
import weakref
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.battle_control.battle_constants import VIEW_COMPONENT_RULE
from gui.battle_control.controllers.interfaces import IBattleController

class IViewComponentsController(IBattleController):
    __slots__ = ()

    def getControllerID(self):
        raise NotImplementedError

    def stopControl(self):
        raise NotImplementedError

    def startControl(self, *args):
        raise NotImplementedError

    def setViewComponents(self, *components):
        raise NotImplementedError

    def clearViewComponents(self):
        raise NotImplementedError


class ComponentsBridgeError(Exception):

    def __init__(self, message):
        super(ComponentsBridgeError, self).__init__(message)


class _ComponentsBridge(object):
    """
    Class makes communication between controller and view components.
    
    There are steps to making communication:
    
        1. Registers controllers:
            bridge = createComponentsBridge()
            bridge.registerController(
                BATTLE_CTRL.DEBUG, debugCtrl
            )
    
        2. Sets configuration:
            bridge.registerViewComponents(
                (BATTLE_CTRL.DEBUG, 'debugPanel'), ...
            )
    
        3. Adds view component when it is created.
            bridge.addViewComponent(
                'debugPanel', debugPanel
            )
    """

    def __init__(self):
        super(_ComponentsBridge, self).__init__()
        self.__components = {}
        self.__ctrls = {}
        self.__indexes = {}
        self.__componentToCrl = {}

    def clear(self):
        """
        Clears data.
        """
        self.__components.clear()
        self.__ctrls.clear()
        self.__indexes.clear()
        self.__componentToCrl.clear()

    def registerViewComponents(self, *data):
        """
        Sets view component data to find that components in routines
            addViewComponent, removeViewComponent.
        :param data: tuple((BATTLE_CTRL.*, (componentID, ...)), ...).
        """
        for item in data:
            if len(item) < 2:
                raise ComponentsBridgeError('Item is invalid: {}'.format(item))
            ctrlID, componentsIDs = item[:2]
            if not isinstance(componentsIDs, tuple):
                raise ComponentsBridgeError('Item is invalid: {}'.format(item))
            if ctrlID in self.__components:
                raise ComponentsBridgeError('Item already is exists: {}'.format(item))
            self.__components[ctrlID] = [None] * len(componentsIDs)
            self.__indexes[ctrlID] = componentsIDs
            for componentID in componentsIDs:
                if componentID in self.__componentToCrl:
                    raise ComponentsBridgeError('View component can be added to controller once: {} {}'.format(componentID, ctrlID))
                self.__componentToCrl[componentID] = ctrlID

        return

    def addViewComponent(self, componentID, component, rule=VIEW_COMPONENT_RULE.PROXY):
        """
        View component has been created, try to find controller expecting
            that component.
        :param componentID: string containing unique component ID.
        :param component: instance of component.
        :param rule: one of VIEW_COMPONENT_RULE.
        """
        if componentID not in self.__componentToCrl:
            return
        else:
            ctrlID = self.__componentToCrl[componentID]
            index = self.__getIndexByComponentID(ctrlID, componentID)
            if index is None:
                LOG_ERROR('View component data is broken', ctrlID, componentID, self.__indexes)
                return
            components = self.__components[ctrlID]
            if rule == VIEW_COMPONENT_RULE.PROXY:
                components[index] = weakref.proxy(component)
            else:
                components[index] = component
            if filter(lambda item: item is None, components):
                return
            if ctrlID in self.__ctrls:
                ctrl = self.__ctrls[ctrlID]
                ctrl.setViewComponents(*components)
            else:
                LOG_WARNING('Controller is not found', ctrlID)
            return

    def removeViewComponent(self, componentID):
        """
        View component has been removed.
        :param componentID: string containing unique component ID.
        """
        if componentID not in self.__componentToCrl:
            return
        else:
            ctrlID = self.__componentToCrl[componentID]
            index = self.__getIndexByComponentID(ctrlID, componentID)
            if index is None:
                LOG_ERROR('View component data is broken', ctrlID, componentID, self.__indexes)
                return
            components = self.__components[ctrlID]
            components[index] = None
            if filter(lambda item: item is not None, components):
                return
            if ctrlID in self.__ctrls:
                ctrl = self.__ctrls.pop(ctrlID)
                self.__components.pop(ctrlID)
                ctrl.clearViewComponents()
            return

    def registerController(self, ctrl):
        """
        Registers controller in the bridge.
        :param ctrl: instance of controller that must be extended
            IViewComponentsController.
        """
        if not isinstance(ctrl, IViewComponentsController):
            raise ComponentsBridgeError('Controller {0} is not extended IViewComponentsController'.format(ctrl))
        self.__ctrls[ctrl.getControllerID()] = weakref.proxy(ctrl)

    def registerControllers(self, *ctrls):
        """
        Registers controllers in the bridge.
        :param ctrls: tuple(ctrl, ...)
        """
        for ctrl in ctrls:
            self.registerController(ctrl)

    def __getIndexByComponentID(self, ctrlID, componentID):
        if ctrlID not in self.__indexes:
            return None
        else:
            indexes = self.__indexes[ctrlID]
            if componentID in indexes:
                return indexes.index(componentID)
            return None
            return None


def createComponentsBridge():
    return _ComponentsBridge()
