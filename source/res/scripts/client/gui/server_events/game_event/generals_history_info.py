# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/generals_history_info.py
import logging
import generals_history_info_xml_reader
from wotdecorators import condition
_logger = logging.getLogger(__name__)
_CONFIG_XML_PATH = 'gui/event_general_history_info.xml'

class GeneralsHistoryInfo(object):
    ifStarted = condition('_started')

    def __init__(self):
        self._started = False
        self._generalsInfo = None
        return

    def start(self):
        if self._started:
            _logger.error('GeneralsHistoryInfo already started')
            return
        else:
            self._started = True
            if self._generalsInfo is None:
                self._generalsInfo = generals_history_info_xml_reader.readFromXML(_CONFIG_XML_PATH)
            return

    @ifStarted
    def stop(self):
        self._started = False
        self._generalsInfo = None
        return

    def getInfoFor(self, generalID):
        if self._generalsInfo is None:
            _logger.error('_generalsInfo is None')
            return []
        elif generalID not in self._generalsInfo:
            _logger.error('general %s is not in _generalsInfo', generalID)
            return []
        else:
            return self._generalsInfo[generalID]['history_blocks']
