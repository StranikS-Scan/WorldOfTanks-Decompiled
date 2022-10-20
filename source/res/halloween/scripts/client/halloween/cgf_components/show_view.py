# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/cgf_components/show_view.py
from functools import partial
import CGF
from helpers import dependency
from constants import IS_CLIENT
from cgf_script.component_meta_class import CGFComponent, CGFMetaTypes, ComponentProperty
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from cgf_components.on_click_components import OnClickComponent
from cgf_components.hover_component import IsHovered
from halloween.skeletons.gui.visibility_layer_controller import IHalloweenVisibilityLayerController
if IS_CLIENT:
    from halloween.gui.shared.event_dispatcher import showMetaView

class ShowViewComponent(CGFComponent):
    editorTitle = 'Show view by special alias'
    category = 'halloween'
    viewAlias = ComponentProperty(type=CGFMetaTypes.STRING, editorName='viewAlias', value='')
    _SHOW_VIEW_FN = {'metaView': showMetaView} if IS_CLIENT else {}

    def showView(self):
        if self.viewAlias in self._SHOW_VIEW_FN:
            self._SHOW_VIEW_FN[self.viewAlias]()


class ClickToOpenViewManager(CGF.ComponentManager):
    _visibilityLayerController = dependency.descriptor(IHalloweenVisibilityLayerController)

    @onAddedQuery(OnClickComponent, ShowViewComponent, CGF.GameObject)
    def handleComponentAdded(self, onClickComponent, showViewComponent, go):
        onClickComponent.onClickAction += partial(self.__showView, go, showViewComponent)

    @onRemovedQuery(OnClickComponent, ShowViewComponent, CGF.GameObject)
    def handleComponentRemoved(self, onClickComponent, showViewComponent, go):
        onClickComponent.onClickAction -= partial(self.__showView, go, showViewComponent)

    def __showView(self, go, showViewComponent):
        go.removeComponentByType(IsHovered)
        showViewComponent.showView()
