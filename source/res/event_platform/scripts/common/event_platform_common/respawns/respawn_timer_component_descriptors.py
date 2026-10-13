# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/common/event_platform_common/respawns/respawn_timer_component_descriptors.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty

class IndividualRespawnTimerComponentDescr(object):
    category = 'Respawns'
    editorTitle = 'IndividualRespawnTimerComponent'
    domain = CGF.Domain.All
    respawnDelay = ComponentProperty(type=CGF.PropertyType.Int, editorName='respawnDelay', value=1)
    timeOfDeath = ComponentProperty(type=CGF.PropertyType.Float, editorName='timeOfDeath', value=0.0)
