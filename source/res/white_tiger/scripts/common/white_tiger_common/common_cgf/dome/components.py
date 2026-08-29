# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/common_cgf/dome/components.py
import typing
import CGF
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent, registerReplicableComponent
if typing.TYPE_CHECKING:
    from typing import Optional, Dict
    from white_tiger_common.wt_constants import WT_TEAMS

@registerReplicableComponent
class WTDomeComponent(object):
    editorTitle = 'WT Dome'
    category = 'White Tiger'
    duration = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Dome duration', value=20.0)


@registerComponent
class WTDomeAreaComponent(object):
    editorTitle = 'WT Dome Area'
    category = 'White Tiger'
    domain = CGF.DomainOption.DomainAll

    def __init__(self):
        self.enterReactionID = 0
        self.exitReactionID = 0
        self.factors = None
        self.affectedTeam = None
        return
