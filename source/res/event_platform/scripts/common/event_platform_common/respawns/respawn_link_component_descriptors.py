# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/common/event_platform_common/respawns/respawn_link_component_descriptors.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import ComponentProperty

class RespawnPolicyVehicleLinkComponentDescr(object):
    category = 'Respawns'
    editorTitle = 'RespawnPolicyVehicleLinkComponent'
    domain = CGF.Domain.All
    vehicleId = ComponentProperty(type=CGF.PropertyType.Int, editorName='vehicleId', value=0)
