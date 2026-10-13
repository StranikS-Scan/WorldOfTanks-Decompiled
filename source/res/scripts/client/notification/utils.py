# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/utils.py
from __future__ import absolute_import
import typing
from frameworks.wulf import WindowLayer
from gui.impl.lobby.gf_notifications import GFNotificationInject
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent
    from typing import Dict, Any

def dynamicNotificationRegister(owner, component, alias, gfViewName, isPopUp, linkageData, onDone):
    idx = WindowLayer.UNDEFINED
    guiLoader = dependency.instance(IGuiLoader)
    componentPy = guiLoader.entitiesFactory.initialize(GFNotificationInject(gfViewName, isPopUp, linkageData), component, idx)
    owner.components[alias] = componentPy
    componentPy.setEnvironment(owner.app)
    componentPy.create()
    g_eventBus.handleEvent(events.ComponentEvent(events.ComponentEvent.COMPONENT_REGISTERED, owner, componentPy, alias), EVENT_BUS_SCOPE.GLOBAL)
    onDone(componentPy, alias)
