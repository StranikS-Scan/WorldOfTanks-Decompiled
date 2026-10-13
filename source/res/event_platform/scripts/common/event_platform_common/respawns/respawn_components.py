# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/common/event_platform_common/respawns/respawn_components.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import registerComponent

@registerComponent
class RespawnBlockComponent(object):
    category = 'Respawns'
    editorTitle = 'RespawnBlockComponent'
    domain = CGF.Domain.All

    def __init__(self, initBlock):
        super(RespawnBlockComponent, self).__init__()
        self.blockers = set()
        self.blockers.add(initBlock)


@registerComponent
class PerformRespawnComponent(object):
    category = 'Respawns'
    editorTitle = 'PerformRespawnComponent'
    domain = CGF.Domain.All
