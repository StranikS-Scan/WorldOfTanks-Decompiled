# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/hangar_enty_point/managers.py
import CGF
from cgf_components.highlight_component import IsHighlighted
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery, autoregister
from cgf_components.hover_component import SelectionComponent
from portal.sounds.sound_constants import EntryPointSound
from portal.sounds.sound_helpers import play2DSound
from portal_client_cgf.hangar_enty_point.components import PortalOutlineGoComponent
from helpers import dependency
from portal.skeletons.portal_event_controller import IPortalEventController
from portal_account_settings import setEventEntrypointIsNew
from shared_utils import nextTick

@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class PortalClickManager(CGF.ComponentManager):
    __portalController = dependency.descriptor(IPortalEventController)

    @onAddedQuery(PortalOutlineGoComponent, SelectionComponent)
    def handlePortalClickAdded(self, outlineComponent, selectionComponent):
        selectionComponent.onClickAction += self.__onClickAction

    @onRemovedQuery(PortalOutlineGoComponent, SelectionComponent)
    def handlePortalClickRemoved(self, outlineComponent, selectionComponent):
        selectionComponent.onClickAction -= self.__onClickAction

    @onAddedQuery(IsHighlighted, PortalOutlineGoComponent)
    def onHoveredOn(self, *_):
        play2DSound(EntryPointSound.HOVER_ON)

    @onRemovedQuery(IsHighlighted, PortalOutlineGoComponent)
    def onHoveredOff(self, *_):
        play2DSound(EntryPointSound.HOVER_OFF)

    def __onClickAction(self):
        play2DSound(EntryPointSound.CLICK)
        nextTick(self.__portalController.selectPortal)()
        setEventEntrypointIsNew(False)
