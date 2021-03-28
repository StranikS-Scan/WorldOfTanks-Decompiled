# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ingame_help/detailed_help_pages.py
import logging
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IN_GAME_HELP_PAGE_SECTION, SPG_HELP_PAGES_LEFT_TO_SHOW
from constants import ARENA_GUI_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.utils.key_mapping import getReadableKey
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

def buildPagesData(ctx):
    datailedList = []
    tempPagesSettings = AccountSettings.getSettings(IN_GAME_HELP_PAGE_SECTION).copy()
    spgHelpScreenGuiTypes = (ARENA_GUI_TYPE.TRAINING,) + ARENA_GUI_TYPE.RANDOM_RANGE
    if ctx.get('isSPG') and ctx.get('arenaGuiType') in spgHelpScreenGuiTypes:
        datailedList.extend(buildSPGPages(tempPagesSettings))
    elif tempPagesSettings.get(SPG_HELP_PAGES_LEFT_TO_SHOW, 0) > 0 and ctx.get('arenaGuiType') in spgHelpScreenGuiTypes:
        datailedList.extend(buildSPGPagesForOtherVehicle(tempPagesSettings))
    if ctx.get('isWheeled') and ctx.get('hasSiegeMode'):
        datailedList.extend(buildSiegeModePages())
    if ctx.get('hasBurnout'):
        datailedList.extend(buildBurnoutPages())
    if ctx.get('isWheeled'):
        datailedList.extend(buildWheeledPages())
    if ctx.get('isDualGun'):
        datailedList.extend(buildDualGunPages())
    if ctx.get('battleRoyale') and ctx.get('mapGeometryName'):
        datailedList.extend(_buildBattleRoyalePages(ctx['mapGeometryName']))
    if ctx.get('hasTurboshaftEngine'):
        datailedList.extend(buildTurboshaftEnginePages())
    return datailedList


def buildTitle(ctx):
    if ctx.get('isSPG'):
        return backport.text(R.strings.ingame_help.detailsHelp.spgReworkTitle())
    else:
        title = backport.text(R.strings.ingame_help.detailsHelp.default.title())
        vehName = ctx.get('vehName')
        if vehName is not None:
            title = vehName
        return title


def buildSiegeModePages():
    pages = []
    siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    keyName = siegeKeyName if siegeKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes.title()), backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes(), key1=keyName), [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_two_mode()))
    return pages


def buildBurnoutPages():
    pages = []
    breakeKeyName = getReadableKey(CommandMapping.CMD_BLOCK_TRACKS)
    forwardKeyName = getReadableKey(CommandMapping.CMD_MOVE_FORWARD)
    keyName1 = breakeKeyName if breakeKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
    keyName2 = forwardKeyName if forwardKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout.title()), backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout(), key1=keyName1, key2=keyName2), [forwardKeyName, breakeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_burnout()))
    return pages


def buildWheeledPages():
    pages = []
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis.title()), backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis()), [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_chassis()))
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique.title()), backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique()), [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_details()))
    return pages


def buildDualGunPages():
    pages = []
    shootKey = getReadableKey(CommandMapping.CMD_CM_SHOOT)
    chargeKey = getReadableKey(CommandMapping.CMD_CM_CHARGE_SHOT)
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire.title()), backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire()), [chargeKey], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.volley_fire()))
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire.title()), backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire()), [shootKey], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.quick_fire()))
    return pages


def _buildBattleRoyalePages(mapGeometryName):
    pages = []
    mapResourceName = 'c_' + replaceHyphenToUnderscore(mapGeometryName)
    imagePath = R.images.gui.maps.icons.battleHelp.battleRoyale.dyn(mapResourceName)
    if not imagePath.isValid():
        raise SoftException('No icons found for map {}'.format(mapGeometryName))
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.title()), backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.description()), [], backport.image(imagePath.br_radar()))
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.title()), backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.description()), [], backport.image(imagePath.br_zone()))
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.title()), backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.description()), [], backport.image(imagePath.br_sector()))
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.title()), backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.description()), [], backport.image(imagePath.br_airdrop()))
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.title()), backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.description()), [], backport.image(imagePath.br_tree()))
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.title()), backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.description()), [], backport.image(imagePath.br_unique_abilities()))
    return pages


def buildTurboshaftEnginePages():
    pages = []
    siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1.title()), backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1()), [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_1()))
    _addPage(pages, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2.title()), backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2()), [], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_2()))
    return pages


def buildSPGPages(tempPagesSettings):
    pages = []
    spgTempPages = ['differentTrajectories',
     'miniMap',
     'tracers',
     'intuition']
    spgConstantPages = ['lamp', 'shotsResultIndicator']
    tempPagesLeftToShow = tempPagesSettings.get(SPG_HELP_PAGES_LEFT_TO_SHOW, 0)
    if tempPagesLeftToShow > 0:
        _addSimplePages(pagesPathName='spgRework', pages=pages, pageNames=spgTempPages)
    _addSimplePages(pagesPathName='spgRework', pages=pages, pageNames=spgConstantPages)
    tempPagesSettings[SPG_HELP_PAGES_LEFT_TO_SHOW] = max(0, tempPagesLeftToShow - 1)
    AccountSettings.setSettings(IN_GAME_HELP_PAGE_SECTION, tempPagesSettings)
    return pages


def buildSPGPagesForOtherVehicle(tempPagesSettings):
    pages = []
    tempPagesLeftToShow = tempPagesSettings.get(SPG_HELP_PAGES_LEFT_TO_SHOW, 0)
    pageNames = ['miniMap',
     'tracers',
     'lamp',
     'intuition']
    _addSimplePages(pagesPathName='spgRework', pages=pages, pageNames=pageNames, mainTitle=backport.text(R.strings.ingame_help.detailsHelp.spgReworkTitle()))
    tempPagesSettings[SPG_HELP_PAGES_LEFT_TO_SHOW] = max(0, tempPagesLeftToShow - 1)
    AccountSettings.setSettings(IN_GAME_HELP_PAGE_SECTION, tempPagesSettings)
    return pages


def _addPage(datailedList, title, descr, buttons, image, mainTitle=None):
    data = {'title': title,
     'descr': descr,
     'buttons': buttons,
     'image': image,
     'overrideMainTitle': mainTitle is not None,
     'mainTitle': mainTitle if mainTitle is not None else ''}
    datailedList.append(data)
    return


def _addSimplePages(pagesPathName, pages, pageNames, mainTitle=None):
    textPath = R.strings.ingame_help.detailsHelp.dyn(pagesPathName)
    imagePath = R.images.gui.maps.icons.battleHelp.dyn(pagesPathName)
    if textPath and imagePath:
        for pageName in pageNames:
            _addPage(pages, backport.text(textPath.dyn(pageName).title()), backport.text(textPath.dyn(pageName).description()), [], backport.image(imagePath.dyn(pageName)()), mainTitle=mainTitle)
