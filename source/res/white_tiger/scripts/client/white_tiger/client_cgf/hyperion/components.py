# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/client_cgf/hyperion/components.py
import CGF
from cgf_script.component_meta_class import registerComponent

@registerComponent
class WTHyperionNotificationComponent(object):
    category = 'White Tiger'
    editorTitle = 'Hyperion Notification'
    domain = CGF.DomainOption.DomainEditor | CGF.DomainOption.DomainClient

    def __init__(self):
        self.enterReactionID = None
        self.exitReactionID = None
        return
