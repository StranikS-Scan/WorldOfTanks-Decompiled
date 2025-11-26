# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/pet_system/cgf_components/storage_state_component.py
import CGF
from cgf_script.component_meta_class import CGFMetaTypes, ComponentProperty, registerComponent
from gui.pet_system.constants import StorageStateKey

@registerComponent
class StorageStateComponent(object):
    domain = CGF.DomainOption.DomainClient
    editorTitle = 'Pet Storage State Component'
    category = 'Pet system'
    names = {name:name for name in StorageStateKey.ALL}
    storageObjectKey = ComponentProperty(type=CGFMetaTypes.STRING, editorName='storage object key', value='active', annotations={'comboBox': names})
