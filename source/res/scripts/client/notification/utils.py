# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/utils.py
import typing
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import g_entitiesFactories
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.impl.lobby.gf_notifications import GFNotificationInject
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
    from typing import Dict, Any

def dynamicNotificationRegister(owner, component, alias, gfViewName, isPopUp, linkageData, onDone):
    idx = WindowLayer.UNDEFINED
    componentPy = g_entitiesFactories.initialize(GFNotificationInject(gfViewName, isPopUp, linkageData), component, idx)
    owner.components[alias] = componentPy
    componentPy.setEnvironment(owner.app)
    componentPy.create()
    g_eventBus.handleEvent(events.ComponentEvent(events.ComponentEvent.COMPONENT_REGISTERED, owner, componentPy, alias), EVENT_BUS_SCOPE.GLOBAL)
    onDone(componentPy, alias)
