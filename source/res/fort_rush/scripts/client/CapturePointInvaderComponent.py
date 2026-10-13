# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/CapturePointInvaderComponent.py
from __future__ import absolute_import
import logging
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from fort_rush.gui.shared.events import CaptureInvaderEvent
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = logging.getLogger(__name__)

class CapturePointInvaderComponent(DynamicScriptComponent):

    def _onAvatarReady(self):
        vehicleID = self.entity.id
        baseName = (self.capturablePointName or '').upper()
        _logger.debug('[FORT_RUSH][INVADER] added vehicleID=%s base=%s', vehicleID, baseName)
        g_eventBus.handleEvent(CaptureInvaderEvent(CaptureInvaderEvent.INVADER_ADDED, vehicleID, baseName), EVENT_BUS_SCOPE.BATTLE)

    def onDestroy(self):
        vehicleID = self.entity.id
        baseName = (self.capturablePointName or '').upper()
        _logger.debug('[FORT_RUSH][INVADER] removed vehicleID=%s base=%s', vehicleID, baseName)
        g_eventBus.handleEvent(CaptureInvaderEvent(CaptureInvaderEvent.INVADER_REMOVED, vehicleID, baseName), EVENT_BUS_SCOPE.BATTLE)
        super(CapturePointInvaderComponent, self).onDestroy()
