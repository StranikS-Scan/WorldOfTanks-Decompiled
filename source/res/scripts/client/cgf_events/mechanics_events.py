# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_events/mechanics_events.py
from __future__ import absolute_import
import CGF
import Vehicular

def postSightPointerSectorEvent(spaceID, entityID, slotName, targetWidth, targetDistance, targetOpacity, duration):
    CGF.postEvent(spaceID, Vehicular.VariablesChangedEvent(entityID=entityID, slotName=slotName, varValueMap={'sectorVision/length': targetDistance,
     'sectorVision/width': targetWidth,
     'sectorVision/opacity': targetOpacity,
     'sectorVision/duration': duration}))
