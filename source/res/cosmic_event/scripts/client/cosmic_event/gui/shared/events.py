# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/shared/events.py
from gui.shared.events import HasCtxEvent

class ArtifactScanningEvent(HasCtxEvent):
    VEHICLES_IN_ZONE_CHANGED = 'artifact/vehiclesInZoneChanged'
    ANNOUNCEMENT_CREATED = 'artifact/announced'
    ARTIFACT_SCANNING_READY = 'artifact/scanningReady'
    ARTIFACT_DESTROYED = 'artifact/destroyed'
