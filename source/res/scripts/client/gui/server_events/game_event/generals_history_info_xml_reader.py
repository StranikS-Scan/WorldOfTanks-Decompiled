# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/generals_history_info_xml_reader.py
import logging
import resource_helper
from gui.Scaleform.genConsts.EVENT_TEMPLATES import EVENT_TEMPLATES
_logger = logging.getLogger(__name__)

def readFromXML(xmlPath):
    generalsInfo = {}
    with resource_helper.root_generator(xmlPath) as ctx, root:
        generalsInfo = _readGenerals(*resource_helper.getSubSection(ctx, root, 'generals'))
    return generalsInfo


def _readGenerals(generalsCtx, generalsSection):
    return {_readGeneralID(ctx, section):_readGeneral(ctx, section) for ctx, section in resource_helper.getIterator(generalsCtx, generalsSection)}


def _readGeneralID(ctx, section):
    return resource_helper.readIntItem(*resource_helper.getSubSection(ctx, section, 'id')).value


def _readGeneral(ctx, section):
    return {'history_blocks': _readHistoryBlocks(*resource_helper.getSubSection(ctx, section, 'history_blocks'))}


def _readHistoryBlocks(historyBlocksCtx, historyBlocksSection):
    return [ _readHistoryBlock(ctx, section) for ctx, section in resource_helper.getIterator(historyBlocksCtx, historyBlocksSection) ]


def _readHistoryBlock(historyBlockCtx, historyBlockSection):
    blockInfo = {name:_getCustomSectionValue(historyBlockCtx, historyBlockSection, name) for name, subSection in historyBlockSection.items()}
    if 'template' not in blockInfo:
        _logger.error('wrong xml data format')
        return {}
    blockInfo['template'] = getattr(EVENT_TEMPLATES, blockInfo['template'].upper())
    return blockInfo


def _getCustomSectionItem(ctx, section, name, safe=False):
    valueCtx, valueSection = resource_helper.getSubSection(ctx, section, name, safe)
    return None if valueSection is None else resource_helper.readItem(valueCtx, valueSection, name)


def _getCustomSectionValue(ctx, section, name, safe=False):
    return _getCustomSectionItem(ctx, section, name, safe).value
