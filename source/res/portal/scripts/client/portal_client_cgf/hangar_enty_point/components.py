# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal_client_cgf/hangar_enty_point/components.py
import CGF
from cgf_script.component_meta_class import registerComponent

@registerComponent
class PortalOutlineGoComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Portal Outline Game object'
    category = 'Portal'
