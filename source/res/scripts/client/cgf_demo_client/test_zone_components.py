# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_demo_client/test_zone_components.py
import logging
import BigWorld
import CGF
from functools import partial
from cgf_demo.demo_category import DEMO_CATEGORY
from cgf_components.zone_components import ZoneMarker, ZoneUINotification
from cgf_script.component_meta_class import ComponentProperty as CompProp, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery
_logger = logging.getLogger(__name__)
ZONE_DURATION = 30.0

@registerComponent
class ZoneDuration(object):
    category = DEMO_CATEGORY
    domain = CGF.DomainOption.DomainClient
    editor_title = 'TestZoneDuration'
    duration = CompProp(type=CGFMetaTypes.FLOAT, editorName='Duration', value=ZONE_DURATION)
    minimap = CompProp(type=CGFMetaTypes.LINK, editorName='MiniMap', value=CGF.GameObject)

    def __init__(self):
        self.callback = None
        return


@autoregister(presentInAllWorlds=True, domain=CGF.DomainOption.DomainClient)
class ZoneDurationManager(CGF.ComponentManager):

    @onAddedQuery(CGF.GameObject, ZoneDuration)
    def onAddedDuration(self, go, duration):
        duration.callback = BigWorld.callback(duration.duration, partial(self.__changeMiniMap, duration))
        self.__setupMarker(go, duration)

    @onRemovedQuery(ZoneDuration)
    def onRemovedDuration(self, duration):
        if duration.callback:
            BigWorld.cancelCallback(duration.callback)
            duration.callback = None
        return

    @onAddedQuery(ZoneDuration, ZoneMarker)
    def onAddedZone(self, duration, zone):
        start = BigWorld.serverTime()
        end = start + duration.duration
        zone.startTime = start
        zone.finishTime = end

    @onAddedQuery(ZoneDuration, ZoneUINotification)
    def onAddedNotification(self, duration, notification):
        start = BigWorld.serverTime()
        end = start + duration.duration
        notification.startTime = start
        notification.finishTime = end

    def __setupMarker(self, go, duration):
        start = BigWorld.serverTime()
        end = start + duration.duration
        hierarchy = CGF.HierarchyManager(self.spaceID)
        markers = hierarchy.findComponentsInHierarchy(go, ZoneMarker)
        for zoneMarker in markers:
            go, marker = zoneMarker
            marker.startTime = start
            marker.finishTime = end

    def __changeMiniMap(self, duration):
        if duration.minimap:
            duration.minimap.activate()
        duration.callback = None
        return
