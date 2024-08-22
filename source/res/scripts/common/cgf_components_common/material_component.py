# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/cgf_components_common/material_component.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from material_kinds import EFFECT_MATERIALS

@registerComponent
class MaterialComponent(object):
    category = 'Material'
    editorTitle = 'Material'
    domain = CGF.DomainOption.DomainAll
    materials = {m:m for m in EFFECT_MATERIALS}
    kind = ComponentProperty(type=CGFMetaTypes.STRING, editorName='Kind', value='', annotations={'comboBox': materials})
