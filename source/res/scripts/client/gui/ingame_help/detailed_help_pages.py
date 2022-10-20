# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ingame_help/detailed_help_pages.py
import logging
import CommandMapping
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.utils.key_mapping import getReadableKey, getVirtualKey
from soft_exception import SoftException
from items.vehicles import getRolesActions
from constants import ACTION_TYPE_TO_LABEL, ROLE_TYPE_TO_LABEL
from gui.shared.formatters import text_styles
_logger = logging.getLogger(__name__)

def buildPagesData(ctx):
    datailedList = []
    defaultHeaderTitle = buildTitle(ctx)
    if ctx.get('isFunRandom'):
        datailedList.extend(buildFunRandomPages(backport.text(R.strings.ingame_help.detailsHelp.funRandom.title())))
    if ctx.get('roleType'):
        datailedList.extend(buildRoleTypePages(backport.text(R.strings.ingame_help.detailsHelp.role.title()), ctx.get('roleType')))
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
    if ctx.get('hasRocketAcceleration'):
        datailedList.extend(buildRocketAccelerationPages(defaultHeaderTitle))
    if ctx.get('isTrackWithinTrack'):
        datailedList.extend(buildTrackWithinTrackPages(defaultHeaderTitle))
    if ctx.get('isComp7'):
        comp7Header = backport.text(R.strings.comp7.detailsHelp.mainTitle())
        datailedList.extend(buildComp7Pages(comp7Header))
    return datailedList


def buildEventPagesData(ctx):
    R_HELP_STRINGS = R.strings.hw_ingame_help.detailsHelp
    R_HELP_IMAGES = R.images.halloween.gui.maps.icons.battleHelp
    pages = []
    headerTitle = backport.text(R.strings.hw_ingame_help.detailsHelp.title())
    for page in ('pageTask', 'pageRespawn', 'pageAbility', 'pageLanterns'):
        _addPage(pages, headerTitle, backport.text(R_HELP_STRINGS.dyn(page).title()), text_styles.mainBig(backport.text(R_HELP_STRINGS.dyn(page).desc())), [], [], backport.image(R_HELP_IMAGES.dyn(page)()))

    return pages


def buildTitle(ctx):
    title = backport.text(R.strings.ingame_help.detailsHelp.default.title())
    vehName = ctx.get('vehName')
    if vehName is not None:
        title = vehName
    return title


def buildSiegeModePages(headerTitle):
    pages = []
    siegeKey = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    keyName = siegeKeyName if siegeKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.twoModes(), key1=keyName)), [siegeKey], [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_two_mode()))
    return pages


def buildBurnoutPages(headerTitle):
    pages = []
    breakeKeyName = getReadableKey(CommandMapping.CMD_BLOCK_TRACKS)
    forwardKeyName = getReadableKey(CommandMapping.CMD_MOVE_FORWARD)
    breakeKey = getVirtualKey(CommandMapping.CMD_BLOCK_TRACKS)
    forwardKey = getVirtualKey(CommandMapping.CMD_MOVE_FORWARD)
    keyName1 = breakeKeyName if breakeKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
    keyName2 = forwardKeyName if forwardKeyName else backport.text(R.strings.ingame_help.detailsHelp.noKey())
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.burnout(), key1=keyName1, key2=keyName2)), [forwardKey, breakeKey], [forwardKeyName, breakeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_burnout()))
    return pages


def buildWheeledPages(headerTitle):
    pages = []
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.stableChassis())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_chassis()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.wheeledVeh.aboutTechnique())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.wheeledHelp.wheel_details()))
    return pages


def buildTrackWithinTrackPages(headerTitle):
    pages = []
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.trackWithinTrack.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.trackWithinTrack.description())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.trackWithinTrack.roll_away()))
    return pages


def buildComp7Pages(headerTitle):
    pages = []
    for pageName in ('poi', 'roleSkills', 'rules'):
        _addPage(datailedList=pages, headerTitle=headerTitle, title=backport.text(R.strings.comp7.detailsHelp.dyn(pageName).title()), descr=text_styles.mainBig(backport.text(R.strings.comp7.detailsHelp.dyn(pageName)())), vKeys=[], buttons=[], image=backport.image(R.images.gui.maps.icons.comp7.battleHelp.dyn(pageName)()))

    return pages


def buildDualGunPages(headerTitle):
    pages = []
    shootKeyName = getReadableKey(CommandMapping.CMD_CM_SHOOT)
    shootKey = getVirtualKey(CommandMapping.CMD_CM_SHOOT)
    chargeKeyName = getReadableKey(CommandMapping.CMD_CM_CHARGE_SHOT)
    chargeKey = getVirtualKey(CommandMapping.CMD_CM_CHARGE_SHOT)
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.dualGun.volley_fire())), [chargeKey], [chargeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.volley_fire()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.dualGun.quick_fire())), [shootKey], [shootKeyName], backport.image(R.images.gui.maps.icons.battleHelp.dualGunHelp.quick_fire()))
    return pages


def buildBattleRoyalePages(headerTitle, mapGeometryName):
    pages = []
    mapResourceName = 'c_' + replaceHyphenToUnderscore(mapGeometryName)
    imagePath = R.images.gui.maps.icons.battleHelp.battleRoyale.dyn(mapResourceName)
    if not imagePath.isValid():
        raise SoftException('No icons found for map {}'.format(mapGeometryName))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.radar.description())), [], [], backport.image(imagePath.br_radar()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.zone.description())), [], [], backport.image(imagePath.br_zone()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.sectorVision.description())), [], [], backport.image(imagePath.br_sector()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.airDrop.description())), [], [], backport.image(imagePath.br_airdrop()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.upgrade.description())), [], [], backport.image(imagePath.br_tree()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.battleRoyale.uniqueAbilities.description())), [], [], backport.image(imagePath.br_unique_abilities()))
    return pages


def buildTurboshaftEnginePages(headerTitle):
    pages = []
    siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    siegeKey = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage1())), [siegeKey], [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_1()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.engineMode.engineModePage2())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.turboshaftEngineHelp.engine_mode_page_2()))
    return pages


def buildRocketAccelerationPages(headerTitle):
    pages = []
    siegeKeyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    siegeKey = getVirtualKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.rocketAcceleration.page1.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.rocketAcceleration.page1())), [siegeKey], [siegeKeyName], backport.image(R.images.gui.maps.icons.battleHelp.rocketAcceleration.page_1()))
    _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.rocketAcceleration.page2.title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.rocketAcceleration.page2())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.rocketAcceleration.page_2()))
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
    _addPage(pages, headerTitle, text_styles.superPromoTitle(backport.text(R.strings.menu.roleExp.roleName.dyn(roleTypeLabel)(), groupName=makeHtmlString('html_templates:vehicleRoles', 'roleTitle', {'message': backport.text(R.strings.menu.roleExp.roleGroupName.dyn(roleTypeLabel)())}))), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.role.description())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.rolesHelp.dyn(roleTypeLabel)()), roleImage=backport.image(R.images.gui.maps.icons.roleExp.roles.c_100x100.dyn(roleTypeLabel)()), roleActions=roleActions)
    return pages


def buildFunRandomPages(headerTitle):
    pages = []
    numPages = R.images.gui.maps.icons.battleHelp.funRandom.length()
    for i in xrange(numPages):
        dynKey = 'mode%s' % (i + 1)
        _addPage(pages, headerTitle, backport.text(R.strings.ingame_help.detailsHelp.funRandom.dyn(dynKey).title()), text_styles.mainBig(backport.text(R.strings.ingame_help.detailsHelp.funRandom.dyn(dynKey).description())), [], [], backport.image(R.images.gui.maps.icons.battleHelp.funRandom.dyn(dynKey)()))

    return pages


def _addPage(datailedList, headerTitle, title, descr, vKeys, buttons, image, roleImage=None, roleActions=None):
    data = {'headerTitle': headerTitle,
     'title': title,
     'descr': descr,
     'vKeys': vKeys,
     'buttons': buttons,
     'image': image,
     'roleImage': roleImage,
     'roleActions': roleActions}
    datailedList.append(data)
