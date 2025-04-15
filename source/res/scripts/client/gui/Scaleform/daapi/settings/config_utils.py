# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/settings/config_utils.py
import logging
import aih_constants
from gui.Scaleform.daapi.view.lobby.vehicle_preview.shared import EXT_PREVIEW_ITEMS
from messenger.formatters.collections_by_type import SERVER_FORMATTERS
from soft_exception import SoftException
from gui.Scaleform.daapi.settings.config import _LOBBY_TOOLTIPS_BUILDERS_PATHS
from AvatarInputHandler import _CTRL_TYPE, OVERWRITE_CTRLS_DESC_MAP, _CTRLS_DESC_MAP
from BattleReplay import _IGNORED_SWITCHING_CTRL_MODES
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

def addTooltipBuilder(builderSettings, personality):
    if any((lobbySetting for lobbySetting in _LOBBY_TOOLTIPS_BUILDERS_PATHS if lobbySetting[0] == builderSettings[0])):
        raise SoftException('_LOBBY_TOOLTIPS_BUILDERS_PATHS already has {builerPath}->{tooltipType}. Personality: {personality}'.format(builerPath=builderSettings[0], tooltipType=builderSettings[1], personality=personality))
    _LOBBY_TOOLTIPS_BUILDERS_PATHS.append(builderSettings)
    msg = '_LOBBY_TOOLTIPS_BUILDERS_PATHS: {builderPath}->{tooltipType} was added to _LOBBY_TOOLTIPS_BUILDERS_PATHS. Personality: {p}'.format(builderPath=builderSettings[0], tooltipType=builderSettings[1], p=personality)
    logging.debug(msg)


def addServerSysMsgFormatters(serverFormatters, personality):
    for sysMsgType, formatter in serverFormatters.items():
        if sysMsgType in SERVER_FORMATTERS.keys():
            raise SoftException('SERVER_FORMATTERS already has sysMsgType:{sysMsgType}. Personality: {personality}'.format(sysMsgType=sysMsgType, personality=personality))
        SERVER_FORMATTERS[sysMsgType] = formatter

    msg = 'serverFormatters:{serverFormatters} was added to SERVER_FORMATTERS. Personality: {p}'.format(serverFormatters=serverFormatters, p=personality)
    logging.debug(msg)


def addCtrlDesc(ctrlName, desc):
    if ctrlName in aih_constants.CTRL_MODES:
        raise SoftException('CTRL_MODES already has mode name:{ctrlName}'.format(ctrlName=ctrlName))
    aih_constants.CTRL_MODES.append(ctrlName)
    _IGNORED_SWITCHING_CTRL_MODES.append(ctrlName)
    if ctrlName in _CTRLS_DESC_MAP:
        raise SoftException('_CTRLS_DESC_MAP already has mode name:{ctrlName}'.format(ctrlName=ctrlName))
    _CTRLS_DESC_MAP[ctrlName] = desc


def addOverwriteCtrlsDescMap(arenaBonusType, ovrModeName, ctrlCflassType, modeName):
    if arenaBonusType in OVERWRITE_CTRLS_DESC_MAP:
        raise SoftException('OVERWRITE_CTRLS_DESC_MAP already has arenaBonusType:{arenaBonusType}'.format(arenaBonusType=arenaBonusType))
    OVERWRITE_CTRLS_DESC_MAP[arenaBonusType] = {ovrModeName: (ctrlCflassType, modeName, _CTRL_TYPE.USUAL)}


def addExtPreviewAliasItem(previewAliasItem, personality):
    if previewAliasItem[0] in EXT_PREVIEW_ITEMS:
        raise SoftException('EXT_PREVIEW_ITEMS already has arenaGuiType:{previewAliasItem}. Personality: {personality}'.format(previewAliasItem=previewAliasItem, personality=personality))
    EXT_PREVIEW_ITEMS.update((previewAliasItem,))
    msg = 'previewAliasItem:{previewAliasItem} was added to EXT_PREVIEW_ITEMS. Personality: {p}'.format(previewAliasItem=previewAliasItem, p=personality)
    logging.debug(msg)
