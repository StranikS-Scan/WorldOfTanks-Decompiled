# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/arena_vscript_config/config.py
import typing
import logging
from extension_utils import ResMgr
import section2dict
from arena_vscript_config.schemas import configSchema
if typing.TYPE_CHECKING:
    from arena_vscript_config.schemas import ConfigModel
_CONFIG_FILE = 'scripts/item_defs/arena_vscripts.xml'
_g_config = None
_logger = logging.getLogger(__name__)

def _readFromXml(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _logger.error('Broken xml schemas source: %s.', xmlPath)
        return
    else:
        rawData = section2dict.parse(section)
        ResMgr.purge(xmlPath, True)
        return configSchema.deserialize(rawData)


def init():
    global _g_config
    if _g_config is None:
        _g_config = _readFromXml(_CONFIG_FILE)
        _logger.info('Arena vscripts ConfigModel created from: %s.', _CONFIG_FILE)
    return


def getInstance():
    if _g_config is None:
        _logger.error('Arena vscripts ConfigModel not initialized.')
    return _g_config
