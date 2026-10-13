# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/cgf/cgf_module.py
from __future__ import absolute_import
import CGF
from CapturePointComponent import CapturePointMarkerAnchor
from cgf_script.registration import registerModule, bonusCapsPredicate
from fort_rush.cgf.capture_point import CapturePointMarkerAnchorGizmoSystem, CapturePointSystem
from fort_rush.cgf.damage_resistance import FortRushDamageResistanceSystem
from fort_rush_common.fort_rush_constants import ARENA_BONUS_TYPE_CAPS
from VehicleExpirableComponent import VehicleExpirableComponent

@registerModule
class FortRushClientModule(object):
    name = 'Fort Rush Client Module'
    desc = 'Fort Rush systems that works on client'
    group = 'Fort Rush'
    systems = [CGF.RegisterSystem(CapturePointSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.FORT_RUSH, spaceID)), CGF.RegisterSystem(FortRushDamageResistanceSystem, domain=CGF.Domain.Client, predicate=lambda spaceID: bonusCapsPredicate(ARENA_BONUS_TYPE_CAPS.FORT_RUSH, spaceID)), CGF.RegisterSystem(CapturePointMarkerAnchorGizmoSystem, domain=CGF.Domain.Editor)]
    components = [CapturePointMarkerAnchor, VehicleExpirableComponent]
