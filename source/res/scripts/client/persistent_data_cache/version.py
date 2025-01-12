# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/persistent_data_cache/version.py
import typing
import constants
from helpers import version
from persistent_data_cache_common.common import getLogger
_logger = getLogger('Version')

def getClientPDCVersion():
    clientVersion = version.getClientVersion()
    locVersion = version.getLocalizationVersion()
    result = (clientVersion.version,
     clientVersion.meta.overrides,
     clientVersion.meta.client,
     clientVersion.meta.realm,
     locVersion.version,
     locVersion.revision,
     locVersion.language)
    if not constants.IS_DEVELOPMENT and '' in result:
        _logger.error('Invalid client version: %s', result)
        return None
    else:
        return result
