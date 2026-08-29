# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/prefab_path_component.py
from __future__ import absolute_import
import CGF
from cgf_script.registration import registerComponent, ComponentProperty

@registerComponent
class PyPrefabPathComponent(object):
    domain = CGF.Domain.ClientEditor
    editorTitle = 'PyPrefab path component'
    category = 'Common'
    vseVisible = False
    prefabPath = ComponentProperty(type=CGF.PropertyType.String, value='', editorName='prefab path', annotations={'path': '*.prefab'})
