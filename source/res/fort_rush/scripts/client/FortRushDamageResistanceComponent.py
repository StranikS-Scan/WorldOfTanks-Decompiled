# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/FortRushDamageResistanceComponent.py
from __future__ import absolute_import
from cgf_client_common.entity_dyn_components import ReplicableDynamicScriptComponent
from cgf_script.registration import registerReplicableComponent
from fort_rush_common.cgf.damage_resistance import FortRushDamageResistanceComponentDescr

@registerReplicableComponent
class FortRushDamageResistanceComponent(ReplicableDynamicScriptComponent, FortRushDamageResistanceComponentDescr):
    pass
