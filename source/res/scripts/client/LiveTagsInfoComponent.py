# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/LiveTagsInfoComponent.py
import logging
from Event import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = logging.getLogger(__name__)

class LiveTagsInfoComponent(DynamicScriptComponent):

    def __init__(self):
        super(LiveTagsInfoComponent, self).__init__()
        self.onStateUpdate = Event()

    def set_liveTags(self, _):
        _logger.debug('[COMMS][LiveTag] Arena.TeamInfo.set_liveTags: %s', self.liveTags)
        self.onStateUpdate()
