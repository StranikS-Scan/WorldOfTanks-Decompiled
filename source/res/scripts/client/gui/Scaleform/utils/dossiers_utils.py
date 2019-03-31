# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/utils/dossiers_utils.py
# Compiled at: 2011-11-29 15:55:20
import BigWorld
from items.vehicles import getVehicleType
from helpers.i18n import makeString
import dossiers
from gui.Scaleform.utils.functions import makeTooltip
from gui.Scaleform.utils.requesters import DossierRequester, StatsRequester
from constants import DOSSIER_TYPE, CLAN_MEMBER_FLAGS
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from PlayerEvents import g_playerEvents
from adisp import process, async
TOTAL_BLOCKS = (('common', ('battlesCount', 'wins', 'losses', 'survivedBattles')), ('battleeffect', ('frags', 'maxFrags', 'effectiveShots', 'damageDealt')), ('credits', ('xp', 'avgExperience', 'maxXP')))
VEHICLE_BLOCKS = (('common', ('battlesCount', 'wins', 'losses', 'survivedBattles')), ('battleeffect', ('frags', 'maxFrags', 'effectiveShots', 'damageDealt')), ('credits', ('xp', 'avgExperience', 'maxXP')))
MEDALS_BLOCKS = (('warrior', 'invader', 'sniper', 'defender', 'steelwall', 'supporter', 'scout'),
 ('medalKay', 'medalCarius', 'medalKnispel', 'medalPoppel', 'medalAbrams', 'medalLeClerc', 'medalLavrinenko', 'medalEkins'),
 ('medalWittmann', 'medalOrlik', 'medalOskin', 'medalHalonen', 'medalBurda', 'medalBillotte', 'medalKolobanov', 'medalFadin'),
 ('beasthunter', 'mousebane', 'tankExpert', 'titleSniper', 'invincible', 'diehard', 'raider', 'handOfDeath', 'armorPiercer', 'kamikaze', 'lumberjack'))
TANKMEN_MEDALS_BLOCKS = (('warrior', 'invader', 'sniper', 'defender', 'steelwall', 'supporter', 'scout'),
 set([]),
 ('medalWittmann', 'medalOrlik', 'medalOskin', 'medalHalonen', 'medalBurda', 'medalBillotte', 'medalKolobanov', 'medalFadin'),
 set([]))
MEDALS_UNIC_FOR_RANK = ('medalKay', 'medalCarius', 'medalKnispel', 'medalPoppel', 'medalAbrams', 'medalLeClerc', 'medalLavrinenko', 'medalEkins')
MEDALS_TITLES = ('tankExpert', 'lumberjack')
MEDALS_SERIES = {'titleSniper': {'cur': 'sniperSeries',
                 'max': 'maxSniperSeries',
                 'format': ('maxSniperSeries',)},
 'invincible': {'cur': 'invincibleSeries',
                'max': 'maxInvincibleSeries',
                'format': ('maxInvincibleSeries',)},
 'diehard': {'cur': 'diehardSeries',
             'max': 'maxDiehardSeries',
             'format': ('maxDiehardSeries',)},
 'handOfDeath': {'cur': 'killingSeries',
                 'max': 'maxKillingSeries',
                 'format': ('maxKillingSeries',)},
 'armorPiercer': {'cur': 'piercingSeries',
                  'max': 'maxPiercingSeries',
                  'format': ('maxPiercingSeries',)}}
CLAN_MEMBERS = {CLAN_MEMBER_FLAGS.LEADER: 'leader',
 CLAN_MEMBER_FLAGS.VICE_LEADER: 'vice_leader',
 CLAN_MEMBER_FLAGS.RECRUITER: 'recruiter',
 CLAN_MEMBER_FLAGS.TREASURER: 'treasurer',
 CLAN_MEMBER_FLAGS.DIPLOMAT: 'diplomat',
 CLAN_MEMBER_FLAGS.COMMANDER: 'commander',
 CLAN_MEMBER_FLAGS.PRIVATE: 'private',
 CLAN_MEMBER_FLAGS.RECRUIT: 'recruit'}
_ICONS_MASK = '../maps/icons/vehicle/small/%s.tga'
__g_dossiersCache = {}

def getUserDossier(userName):
    global __g_dossiersCache
    if not __g_dossiersCache.has_key(userName):
        __g_dossiersCache[userName] = DossierRequester(userName)
    return __g_dossiersCache[userName]


def closeUserDossier(userName):
    if __g_dossiersCache.has_key(userName):
        if not __g_dossiersCache[userName].isValid:
            return
        del __g_dossiersCache[userName]
    else:
        LOG_DEBUG('Attempt to clear empty user dossier: %s' % str(userName))


def __onCenterIsLongDisconnected(isLongDisconnected):
    global __g_dossiersCache
    if isLongDisconnected:
        return
    __g_dossiersCache = dict(filter(lambda item: item[1].isAvailable, __g_dossiersCache.iteritems()))


g_playerEvents.onCenterIsLongDisconnected += __onCenterIsLongDisconnected

def getCommonInfo(userName, dossier, clanInfo, clanEmblemFile):
    value = [clanInfo is not None,
     userName,
     '%s %s' % (BigWorld.wg_getLongDateFormat(dossier['creationTime']), BigWorld.wg_getLongTimeFormat(dossier['creationTime'])),
     '%s %s' % (BigWorld.wg_getLongDateFormat(dossier['lastBattleTime']), BigWorld.wg_getLongTimeFormat(dossier['lastBattleTime']))]

    def getGoldFmt(str):
        return "<font color='#FBCD5E'>" + str + '</font>'

    if clanInfo is not None:
        value.append("[<font color='#ffffff'>%s</font>] %s" % (clanInfo[1], clanInfo[0]))
        value.append(makeString('#menu:profile/header/clan/joinDate') % getGoldFmt(BigWorld.wg_getLongDateFormat(clanInfo[4])))
        clanPosition = makeString('#menu:profile/header/clan/position/%s' % CLAN_MEMBERS[clanInfo[3]] if clanInfo[3] in CLAN_MEMBERS else '')
        value.append(makeString('#menu:profile/header/clan/position') % getGoldFmt(clanPosition) if clanInfo[3] in CLAN_MEMBERS else '')
        clanEmblemId = None
        if clanEmblemFile:
            clanEmblemId = 'userInfoId' + userName
            BigWorld.wg_addTempScaleformTexture(clanEmblemId, clanEmblemFile)
        value.append(clanEmblemId)
    else:
        value.extend(['',
         '',
         '',
         None])
    return value


@async
@process
def getClanEmblemTextureID(clanDBID, isBig, textureID, callback):
    import imghdr
    if clanDBID is not None and clanDBID != 0:
        clanEmblemUrl, clanEmblemFile = yield StatsRequester().getFileFromServer(clanDBID, 'clan_emblems_small' if not isBig else 'clan_emblems')
        if clanEmblemFile and imghdr.what(None, clanEmblemFile) is not None:
            BigWorld.wg_addTempScaleformTexture(textureID, clanEmblemFile)
            callback(True)
            return
    callback(False)
    return


def getDossierVehicleList(dossier, isOnlyTotal=False):
    battlesCount = float(dossier['battlesCount'])
    winsCount = float(dossier['wins'])
    data = ['ALL',
     '#menu:profile/list/totalName',
     _ICONS_MASK % 'all',
     0,
     -1,
     __getData('battlesCount', dossier),
     '%d%%' % round(100 * winsCount / battlesCount) if battlesCount != 0 else '']
    if not isOnlyTotal:
        vehList = dossier['vehDossiersCut'].items()
        vehList.sort(cmp=__dossierComparator)
        for vehTypeCompactDesr, battles in vehList:
            try:
                vehType = getVehicleType(vehTypeCompactDesr)
                data.append(vehTypeCompactDesr)
                data.append(vehType.userString)
                data.append(_ICONS_MASK % vehType.name.replace(':', '-'))
                data.append(vehType.level)
                data.append(vehType.id[0])
                data.append(battles[0])
                data.append('%d%%' % round(100 * float(battles[1]) / battles[0]) if battles[0] != 0 else '')
            except Exception:
                LOG_ERROR('Get vehicle info error vehTypeCompactDesr: %s' % str(vehTypeCompactDesr))
                LOG_CURRENT_EXCEPTION()

    return data


def getDossierMedals(dossier, dossier_type=DOSSIER_TYPE.ACCOUNT):
    medals = []
    blocks = []
    if dossier_type == DOSSIER_TYPE.ACCOUNT:
        blocks = MEDALS_BLOCKS
    elif dossier_type == DOSSIER_TYPE.TANKMAN:
        blocks = TANKMEN_MEDALS_BLOCKS
    for group in blocks:
        for type in group:
            if dossier[type]:
                medals.append(type)
                max_value = dossiers.getRecordMaxValue(type)
                if type in MEDALS_UNIC_FOR_RANK:
                    medals.append(dossier[type])
                elif type in MEDALS_SERIES.keys():
                    medals.append(dossier[MEDALS_SERIES[type]['max']])
                elif dossier[type] >= max_value:
                    medals.append(makeString('#achievements:achievement/maxMedalValue') % (max_value - 1))
                else:
                    medals.append(dossier[type])
                medals.append(type in MEDALS_UNIC_FOR_RANK)
                medals.append(type in MEDALS_TITLES)
                achiev_name = makeString('#achievements:%s' % type)
                if type in MEDALS_UNIC_FOR_RANK:
                    achiev_name = achiev_name % makeString('#achievements:achievement/rank%d' % dossier[type])
                achiev_tooltip_body = None
                if type in MEDALS_SERIES.keys():
                    format_args = []
                    for arg_type in MEDALS_SERIES[type].get('format', []):
                        format_args.append(dossier[arg_type])

                    achiev_tooltip_body = makeString('#tooltips:achievement/%s/body' % type) % tuple(format_args)
                medals.append(makeTooltip(achiev_name, achiev_tooltip_body, makeString('#tooltips:achievement/note')))
                medals.append(makeString('#achievements:%s_descr' % type))
                medals.append(False)

        if len(medals) != 0:
            medals[-1] = blocks[-1] != group

    return medals


def getMedal(achievementType, rank):
    medal = []
    for group in MEDALS_BLOCKS:
        for type in group:
            if type == achievementType:
                medal.append(type)
                medal.append(rank)
                medal.append(type in MEDALS_UNIC_FOR_RANK)
                tooltip = makeString('#achievements:%s' % type)
                medal.append(tooltip % makeString('#achievements:achievement/rank%d' % rank) if type in MEDALS_UNIC_FOR_RANK else tooltip)
                medal.append(makeString('#achievements:%s_descr' % type))

    return medal


def getDossierTotalBlocks(dossier):
    data = ['#menu:profile/list/totalName', len(TOTAL_BLOCKS)]
    for blockType, fields in TOTAL_BLOCKS:
        data.append(blockType)
        data.append(len(fields))
        for fieldType in fields:
            data.append(fieldType)
            data.append(__getData(fieldType, dossier))
            data.append(__getDataExtra(blockType, fieldType, dossier, True))

    return data


def getDossierTotalBlocksSummary(dossier):
    data = []
    for blockType, fields in TOTAL_BLOCKS:
        for fieldType in fields:
            data.append('#menu:profile/stats/items/' + fieldType)
            data.append(__getData(fieldType, dossier))
            data.append(__getDataExtra(blockType, fieldType, dossier, True))

    return data


def getDossierVehicleBlocks(dossier, vehTypeId):
    vehType = getVehicleType(int(vehTypeId))
    data = [makeString('#menu:profile/list/descr', vehType.userString), len(VEHICLE_BLOCKS)]
    for blockType, fields in VEHICLE_BLOCKS:
        data.append(blockType)
        data.append(len(fields))
        for fieldType in fields:
            data.append(fieldType)
            data.append(__getData(fieldType, dossier))
            data.append(__getDataExtra(blockType, fieldType, dossier))

    return data


def __getData(fieldType, dossier):
    if fieldType == 'effectiveShots':
        if dossier['shots'] != 0:
            return '%d%%' % round(float(dossier['hits']) / dossier['shots'] * 100)
        return '0%'
    if fieldType == 'avgExperience':
        if dossier['battlesCount'] != 0:
            return BigWorld.wg_getIntegralFormat(round(float(dossier['xp']) / dossier['battlesCount']))
        return BigWorld.wg_getIntegralFormat(0)
    return BigWorld.wg_getIntegralFormat(dossier[fieldType])


def __getDataExtra(blockType, fieldType, dossier, isTotal=False):
    extra = ''
    if blockType == 'common':
        if fieldType != 'battlesCount' and dossier['battlesCount'] != 0:
            extra = '(%d%%)' % round(float(dossier[fieldType]) / dossier['battlesCount'] * 100)
    if isTotal:
        if fieldType == 'maxFrags' and dossier['maxFrags'] != 0:
            extra = getVehicleType(dossier['maxFragsVehicle']).userString
        if fieldType == 'maxXP' and dossier['maxXP'] != 0:
            extra = getVehicleType(dossier['maxXPVehicle']).userString
    return extra


def __dossierComparator(x1, x2):
    if x1[1][0] < x2[1][0]:
        return 1
    if x1[1][0] > x2[1][0]:
        return -1
    if x1[1][1] < x2[1][1]:
        return 1
    if x1[1][1] > x2[1][1]:
        return -1
