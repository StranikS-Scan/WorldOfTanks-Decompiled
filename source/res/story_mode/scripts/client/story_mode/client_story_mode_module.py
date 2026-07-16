# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/client_story_mode_module.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import registerModule
from story_mode.cgf_components.bunkers import BunkersSystem
from BunkerLogicComponent import BunkerLogicComponent

@registerModule
class ClientStoryModeModule(object):
    name = 'Client Story Mode Module'
    desc = 'Client Story Mode Functionalities'
    group = 'Store Mode'
    systems = [CGF.RegisterSystem(BunkersSystem, domain=CGF.Domain.Client, updateAfter=(CGF.TransformUpdateSystem,))]
    components = [BunkerLogicComponent]
