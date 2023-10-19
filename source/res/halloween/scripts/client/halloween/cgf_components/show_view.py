# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/cgf_components/show_view.py
from functools import partial
import CGF
from helpers import dependency
from constants import IS_CLIENT
from cgf_script.component_meta_class import registerComponent, CGFMetaTypes, ComponentProperty
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
from cgf_components.hover_component import IsHoveredComponent, SelectionComponent
from halloween.skeletons.gui.visibility_layer_controller import IHalloweenVisibilityLayerController
from skeletons.gui.game_control import IHalloweenController
if IS_CLIENT:
    from halloween.gui.shared.event_dispatcher import showMetaView

@registerComponent
class ShowViewComponent(object):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Show view by special alias'
    category = 'halloween'
    viewAlias = ComponentProperty(type=CGFMetaTypes.STRING, editorName='viewAlias', value='')
    _SHOW_VIEW_FN = {'metaView': showMetaView} if IS_CLIENT else {}

    def showView(self):
        if self.viewAlias in self._SHOW_VIEW_FN:
            self._SHOW_VIEW_FN[self.viewAlias]()


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class ClickToOpenViewManager(CGF.ComponentManager):
    _visibilityLayerController = dependency.descriptor(IHalloweenVisibilityLayerController)
    _hwController = dependency.descriptor(IHalloweenController)

    @onAddedQuery(SelectionComponent, ShowViewComponent, CGF.GameObject)
    def handleComponentAdded(self, selectionComponent, showViewComponent, go):
        selectionComponent.onClickAction += partial(self.__showView, go, showViewComponent)

    @onRemovedQuery(SelectionComponent, ShowViewComponent, CGF.GameObject)
    def handleComponentRemoved(self, selectionComponent, showViewComponent, go):
        selectionComponent.onClickAction -= partial(self.__showView, go, showViewComponent)

    def __showView(self, go, showViewComponent):
        go.removeComponentByType(IsHoveredComponent)
        isEventHangar = self._hwController.isEventHangar()
        if isEventHangar and self._hwController.isEnabled():
            showViewComponent.showView()
