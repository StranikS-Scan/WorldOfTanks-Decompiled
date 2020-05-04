# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SE20ClientSelectableObject.py
import Math
from ClientSelectableEasterEgg import ClientSelectableEasterEgg
from helpers import dependency
from skeletons.gui.shared.utils import IHangarSpace
from gui.shared import g_eventBus, events
from se20.se20_client_selectable_object_behaviour import SE20ClientSelectableObjectBehaviour
from se20.se20_gramophone_behaviour import SE20HangarGramophoneBehaviour
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS

class SE20ClientSelectableObject(ClientSelectableEasterEgg):
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _PREVIEW_PANELS = (VEHPREVIEW_CONSTANTS.BUYING_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.EVENT_PROGRESSION_BUYING_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.TRADE_IN_BUYING_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.SECRET_EVENT_BUYING_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.SECRET_EVENT_BUYING_ACTION_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.SECRET_EVENT_BOUGHT_PANEL_PY_ALIAS,
     VEHPREVIEW_CONSTANTS.SECRET_EVENT_SOLD_PANEL_PY_ALIAS)
    _SELECTION_ID_BEHAVIOUR = {'hangarGramophone': SE20HangarGramophoneBehaviour}

    def __init__(self):
        super(SE20ClientSelectableObject, self).__init__()
        behaviourCls = self._SELECTION_ID_BEHAVIOUR.get(self.selectionId, SE20ClientSelectableObjectBehaviour)
        self._behaviour = behaviourCls(self)

    @property
    def isShowTooltip(self):
        return self._behaviour.isShowTooltip

    def onEnterWorld(self, prereqs):
        super(SE20ClientSelectableObject, self).onEnterWorld(prereqs)
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__onComponentsRegistered)
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_UNREGISTERED, self.__onComponentsUnRegistered)
        self._behaviour.onEnterWorld()

    def onLeaveWorld(self):
        self._behaviour.onLeaveWorld()
        super(SE20ClientSelectableObject, self).onLeaveWorld()
        g_eventBus.removeListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__onComponentsRegistered)
        g_eventBus.removeListener(events.ComponentEvent.COMPONENT_UNREGISTERED, self.__onComponentsUnRegistered)

    def onMouseClick(self):
        self._behaviour.onMouseClick()

    def _onAnimatorReady(self):
        self._behaviour.onAnimatorReady()

    def _getCollisionModelsPrereqs(self):
        collisionModels = ((0, self.modelName, self.boundingSphereSize),)
        return collisionModels

    def _getCollisionDataMatrix(self):
        matrix = super(SE20ClientSelectableObject, self)._getCollisionDataMatrix()
        offset = Math.Matrix()
        offset.translation = self.boundingSphereOffset
        result = Math.MatrixProduct()
        result.a = matrix
        result.b = offset
        return result

    def __onComponentsRegistered(self, event):
        if event.alias in self._PREVIEW_PANELS:
            self.setEnable(False)

    def __onComponentsUnRegistered(self, event):
        if event.alias in self._PREVIEW_PANELS:
            self.setEnable(True)
