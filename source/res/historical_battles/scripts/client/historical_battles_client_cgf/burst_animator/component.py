# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles_client_cgf/burst_animator/component.py
import CGF
from cgf_script.component_meta_class import registerComponent

@registerComponent
class BurstAnimatorComponent(object):
    domain = CGF.DomainOption.DomainEditor | CGF.DomainOption.DomainClient
