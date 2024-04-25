# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/services_config.py
import logging
from historical_battles.gui import server_events
__all__ = ('updateServicesConfig',)
_logger = logging.getLogger(__name__)

def updateServicesConfig(manager):
    manager.addConfig(server_events.getCustomizableObjectsManagar)
    manager.addConfig(server_events.getHBSoundController)
