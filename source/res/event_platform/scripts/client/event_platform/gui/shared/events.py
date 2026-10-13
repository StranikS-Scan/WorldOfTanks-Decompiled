# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/gui/shared/events.py
from __future__ import absolute_import
from gui.shared.event_bus import SharedEvent

class RespawnFrameworkEvent(SharedEvent):
    VEHICLES_LOADED = 'respawnFramework/respawnVehiclesLoaded'
    POSTMORTEM_ENTERED = 'respawnFramework/postmortemEntered'
    POSTMORTEM_LEFT = 'respawnFramework/postmortemLeft'
