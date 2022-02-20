# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ingame_help/detailed_help_pages.py
import logging
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.AccountSettings import IN_GAME_HELP_PAGE_SECTION, SPG_HELP_PAGES_LEFT_TO_SHOW
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.utils.key_mapping import getReadableKey
from soft_exception import SoftException
from items.vehicles import getRolesActions
from constants import ACTION_TYPE_TO_LABEL, ROLE_TYPE_TO_LABEL, ARENA_GUI_TYPE
from gui.shared.formatters import text_styles
_logger = logging.getLogger(__name__)

def buildPagesData(ctx):
    datailedList = []
    defaultHeaderTitle = buildTitle(ctx)
    if ctx.get('roleType'):
        datailedList.extend(buildRoleTypePages(backport.text(R.strings.ingame_help.detailsHelp.role.title()), ctx.get('roleType')))
    spgHelpScreenGuiTypes = (ARENA_GUI_TYPE.TRAINING,) + ARENA_GUI_TYPE.RANDOM_RANGE
    if ctx.get('arenaGuiType') in spgHelpScreenGuiTypes:
        tempPagesSettings = AccountSettings.getSettings(IN_GAME_HELP_PAGE_SECTION).copy()
        spgHeaderTitle = backport.text(R.strings.ingame_help.detailsHelp.spgReworkTitle())
        if ctx.get('isSPG'):
            datailedList.extend(buildSPGPages(spgHeaderTitle, tempPagesSettings))
        elif tempPagesSettings.get(SPG_HELP_PAGES_LEFT_TO_SHOW, 0) > 0:
            datailedList.extend(buildSPGPagesForOtherVehicle(spgHeaderTitle, tempPagesSettings))
    if ctx.get('isWheeled') and ctx.get('hasSiegeMode'):
        datailedList.extend(buildSiegeModePages(defaultHeaderTitle))
    if ctx.get('hasBurnout'):
        datailedList.extend(buildBurnoutPages(defaultHeaderTitle))
    if ctx.get('isWheeled'):
        datailedList.extend(buildWheeledPages(defaultHeaderTitle))
    if ctx.get('isDualGun'):
        datailedList.extend(buildDualGunPages(defaultHeaderTitle))
    if ctx.get('battleRoyale') and ctx.get('mapGeometryName'):
        datailedList.extend(buildBattleRoyalePages(defaultHeaderTitle, ctx['mapGeometryName']))
    if ctx.get('hasTurboshaftEngine'):
        datailedList.extend(buildTurboshaftEnginePages(defaultHeaderTitle))
    if ctx.get('isTrackWithinTrack'):
        datailedList.extend(buildTrackWithinTrackPages(defaultHeaderTitle))
    return datailedList


def buildTitle(ctx):
    title = backport.text(R.strings.ingame_help.detailsHelp.default.title())
    vehName = ctx.get('vehName')
    if vehName is not None:
        title = vehName
    return title


def buildSiegeModePages(headerTitle):
    pages = []
    siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    keyName = siegeKeyName if siegeKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes(), key1=keyName)), [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_two_mode()))
    return pages


def buildBurnoutPages(headerTitle):
    pages = []
    breakeKeyName = getReadableKey(CommandMapping.CMD_BLOCK_TRACKS)
    forwardKeyName = getReadableKey(CommandMapping.CMD_MOVE_FORWARD)
    keyName1 = breakeKeyName if breakeKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
    keyName2 = forwardKeyName if forwardKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout(), key1=keyName1, key2=keyName2)), [forwardKeyName, breakeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_burnout()))
    return pages


def buildWheeledPages(headerTitle):
    pages = []
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis())), [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_chassis()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique())), [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_details()))
    return pages


def buildTrackWithinTrackPages(headerTitle):
    pages = []
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.trackWithinTrack.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.trackWithinTrack.description())), [], backport.image(R.images.gui.maps.icons.battleHelp.trackWithinTrack.roll_away()))
    return pages


def buildDualGunPages(headerTitle):
    pages = []
    shootKey = getReadableKey(CommandMapping.CMD_CM_SHOOT)
    chargeKey = getReadableKey(CommandMapping.CMD_CM_CHARGE_SHOT)
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire())), [chargeKey], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.volley_fire()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire())), [shootKey], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.quick_fire()))
    return pages


def buildBattleRoyalePages(headerTitle, mapGeometryName):
    pages = []
    mapResourceName = 'c_' + replaceHyphenToUnderscore(mapGeometryName)
    imagePath = R.images.gui.maps.icons.battleHelp.battleRoyale.dyn(mapResourceName)
    if not imagePath.isValid():
        raise SoftException('No icons found for map {}'.format(mapGeometryName))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.description())), [], backport.image(imagePath.br_radar()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.description())), [], backport.image(imagePath.br_zone()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.description())), [], backport.image(imagePath.br_sector()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.description())), [], backport.image(imagePath.br_airdrop()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.description())), [], backport.image(imagePath.br_tree()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.description())), [], backport.image(imagePath.br_unique_abilities()))
    return pages


def buildTurboshaftEnginePages(headerTitle):
    pages = []
    siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1())), [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_1()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2())), [], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_2()))
    return pages


def buildRoleTypePages(headerTitle, roleType):
    roleActions = []
    rolesToActions = getRolesActions()
    for action in rolesToActions[roleType]:
        actionLabel = ACTION_TYPE_TO_LABEL[action]
        roleActions.append({'image': backport.image(R.images.gui.maps.icons.roleExp.actions.c_128x128.dyn(actionLabel)()),
         'description': backport.text(R.strings.menu.roleExp.action.dyn(actionLabel)())})

    roleTypeLabel = ROLE_TYPE_TO_LABEL[roleType]
    pages = []
    _addPage(pages, headerTitle, text_styles.superPromoTitle(backport.text(R.strings.menu.roleExp.roleName.dyn(roleTypeLabel)(), groupName=makeHtmlString('html_templates:vehicleRoles', 'roleTitle', {'message': backport.text(R.strings.menu.roleExp.roleGroupName.dyn(roleTypeLabel)())}))), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.role.description())), [], backport.image(R.images.gui.maps.icons.battleHelp.rolesHelp.dyn(roleTypeLabel)()), roleImage=backport.image(R.images.gui.maps.icons.roleExp.roles.c_100x100.dyn(roleTypeLabel)()), roleActions=roleActions)
    return pages


def buildSPGPages(headerTitle, tempPagesSettings):
    pages = []
    spgTempPages = ['differentTrajectories',
     'miniMap',
     'tracers',
     'intuition']
    spgConstantPages = ['lamp', 'shotsResultIndicator']
    tempPagesLeftToShow = tempPagesSettings.get(SPG_HELP_PAGES_LEFT_TO_SHOW, 0)
    if tempPagesLeftToShow > 0:
        _addSimplePages(headerTitle, pagesPathName='spgRework', pages=pages, pageNames=spgTempPages)
    _addSimplePages(headerTitle, pagesPathName='spgRework', pages=pages, pageNames=spgConstantPages)
    tempPagesSettings[SPG_HELP_PAGES_LEFT_TO_SHOW] = max(0, tempPagesLeftToShow - 1)
    AccountSettings.setSettings(IN_GAME_HELP_PAGE_SECTION, tempPagesSettings)
    return pages


def buildSPGPagesForOtherVehicle(headerTitle, tempPagesSettings):
    pages = []
    tempPagesLeftToShow = tempPagesSettings.get(SPG_HELP_PAGES_LEFT_TO_SHOW, 0)
    pageNames = ['miniMap',
     'tracers',
     'lamp',
     'intuition']
    _addSimplePages(headerTitle, pagesPathName='spgRework', pages=pages, pageNames=pageNames)
    tempPagesSettings[SPG_HELP_PAGES_LEFT_TO_SHOW] = max(0, tempPagesLeftToShow - 1)
    AccountSettings.setSettings(IN_GAME_HELP_PAGE_SECTION, tempPagesSettings)
    return pages


def _addPage(datailedList, headerTitle, title, descr, buttons, image, roleImage=None, roleActions=None):
    data = {'headerTitle': headerTitle,
     'title': title,
     'descr': descr,
     'buttons': buttons,
     'image': image,
     'roleImage': roleImage,
     'roleActions': roleActions}
    datailedList.append(data)


def _addSimplePages(headerTitle, pagesPathName, pages, pageNames):
    textPath = R.strings.ingame_help.detailsHelp.dyn(pagesPathName)
    imagePath = R.images.gui.maps.icons.battleHelp.dyn(pagesPathName)
    if textPath and imagePath:
        for pageName in pageNames:
            _addPage(pages, headerTitle, backport.text(textPath.dyn(pageName).title()), backport.text(textPath.dyn(pageName).description()), [], backport.image(imagePath.dyn(pageName)()))
