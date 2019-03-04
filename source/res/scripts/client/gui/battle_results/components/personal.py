# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/personal.py
import BigWorld
from constants import DEATH_REASON_ALIVE
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.battle_results.components import base
from gui.battle_results.components import shared
from gui.battle_results.components import style
from gui.shared.crits_mask_parser import CRIT_MASK_SUB_TYPES
from gui.shared.formatters import numbers
from gui.shared.formatters import text_styles
from gui.shared.gui_items.Vehicle import getSmallIconPath, getTypeBigIconPath, getNationLessName, getIconShopPath
from gui.shared.utils.functions import makeTooltip
from helpers import i18n
_UNDEFINED_EFFICIENCY_VALUE = '-'

class PremiumAccountFlag(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return reusable.isPostBattlePremium


class IsTeamKillerFlag(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return reusable.personal.isTeamKiller


class CanUpgradeToPremiumFlag(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return reusable.canUpgradeToPremium and reusable.personal.getCreditsDiff() > 0 and reusable.personal.getXPDiff() > 0


class StunDataFlag(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return reusable.isStunEnabled


class PremiumBuyBlock(base.StatsBlock):
    __slots__ = ('clientIndex', 'creditsDiff', 'xpDiff')

    def __init__(self, meta=None, field='', *path):
        super(PremiumBuyBlock, self).__init__(meta, field, *path)
        self.clientIndex = 0
        self.creditsDiff = 0
        self.xpDiff = 0

    def setRecord(self, result, reusable):
        self.clientIndex = reusable.clientIndex
        self.creditsDiff = reusable.personal.getCreditsDiff()
        self.xpDiff = reusable.personal.getXPDiff()


class PlayerNoClanFlag(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return not reusable.getPlayerInfo().clanDBID


class PlayerRank(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        avatarInfo = reusable.getAvatarInfo()
        return avatarInfo.extensionInfo['playerRank']['rank'] if 'playerRank' in avatarInfo.extensionInfo else 0


class PersonalPlayerNameBlock(shared.PlayerNameBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        self.setPlayerInfo(reusable.getPlayerInfo())


class KillerPlayerNameBlock(shared.PlayerNameBlock):
    __slots__ = ()


class DetailsPlayerNameBlock(shared.PlayerNameBlock):
    __slots__ = ()


class PersonalVehicleNamesBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        for _, item in reusable.personal.getVehicleItemsIterator():
            self.addNextComponent(base.DirectStatsItem('', item.userName))


class PersonalVehicleTypeIconsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        for _, item in reusable.personal.getVehicleItemsIterator():
            self.addNextComponent(base.DirectStatsItem('', getTypeBigIconPath(item.type)))


class EpicVehicleNamesBlock(PersonalVehicleNamesBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        self.addNextComponent(base.DirectStatsItem('', i18n.makeString(BATTLE_RESULTS.ALLVEHICLES)))
        super(EpicVehicleNamesBlock, self).setRecord(result, reusable)


class PersonalVehicleBlock(base.StatsBlock):
    __slots__ = ('isVehicleStatusDefined', 'vehicleIcon', 'vehicleLevel', 'nationName', 'killerID', 'vehicleState', 'vehicleStatePrefix', 'vehicleStateSuffix', 'isPrematureLeave', 'isKilledByTeamKiller')

    def setVehicle(self, item):
        if item is not None:
            self.isVehicleStatusDefined = not item.isObserver
            self.vehicleIcon = self._getVehicleIcon(item)
            self.vehicleLevel = item.level
            self.nationName = item.nationName
        else:
            self.isVehicleStatusDefined = False
        return

    def setRecord(self, result, reusable):
        killerID = result.get('killerID', 0)
        deathReason = result.get('deathReason', DEATH_REASON_ALIVE)
        self.killerID = killerID
        if reusable.personal.avatar.isPrematureLeave:
            self.isPrematureLeave = True
            self.vehicleState = i18n.makeString(BATTLE_RESULTS.COMMON_VEHICLESTATE_PREMATURELEAVE)
        elif deathReason > DEATH_REASON_ALIVE:
            if self.isVehicleStatusDefined and killerID:
                fillKillerInfoBlock(self, deathReason, killerID, reusable)
        else:
            self.vehicleState = i18n.makeString(BATTLE_RESULTS.COMMON_VEHICLESTATE_ALIVE)

    def _getVehicleIcon(self, item):
        return getNationLessName(item.name)


class EpicVehicleBlock(PersonalVehicleBlock):

    def _getVehicleIcon(self, item):
        return getIconShopPath(item.name, STORE_CONSTANTS.ICON_SIZE_LARGE)


class PersonalVehiclesBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        personal = reusable.personal
        for intCD, item in personal.getVehicleItemsIterator():
            component = self._createComponent()
            component.setVehicle(item)
            component.setRecord(result[intCD], reusable)
            self.addComponent(self.getNextComponentIndex(), component)

    def _createComponent(self):
        return PersonalVehicleBlock()


class EpicVehiclesBlock(PersonalVehiclesBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        component = PersonalVehicleBlock()
        component.vehicleIcon = RES_ICONS.MAPS_ICONS_LIBRARY_EPICVEHICLESALL
        self.addNextComponent(component)
        super(EpicVehiclesBlock, self).setRecord(result, reusable)

    def _createComponent(self):
        return EpicVehicleBlock()


class _DetailsBlock(base.StatsBlock):
    __slots__ = ('_isEmpty',)

    def __init__(self, meta=None, field='', *path):
        super(_DetailsBlock, self).__init__(meta, field, *path)
        self._isEmpty = True

    def isEmpty(self):
        return self._isEmpty


class DamageDetailsBlock(_DetailsBlock):
    __slots__ = ('piercings', 'damageDealtValues', 'damageDealtNames', '_isEmpty')

    def __init__(self, meta=None, field='', *path):
        super(DamageDetailsBlock, self).__init__(meta, field, *path)
        self.piercings = None
        self.damageDealtValues = None
        self.damageDealtNames = None
        return

    def setRecord(self, result, reusable):
        piercings = result.piercings
        damageDealt = result.damageDealt
        self.piercings = piercings
        self._isEmpty = piercings <= 0
        if damageDealt > 0:
            self._isEmpty = False
            self.damageDealtValues = [BigWorld.wg_getIntegralFormat(damageDealt), BigWorld.wg_getIntegralFormat(piercings)]
            self.damageDealtNames = [i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_DAMAGE_PART1, vals=style.getTooltipParamsStyle()), i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_DAMAGE_PART2)]


class ArmorUsingDetailsBlock(_DetailsBlock):
    __slots__ = ('usedArmorCount', 'armorValues', 'armorNames', '_isEmpty')

    def __init__(self, meta=None, field='', *path):
        super(ArmorUsingDetailsBlock, self).__init__(meta, field, *path)
        self.usedArmorCount = None
        self.armorValues = None
        self.armorNames = None
        return

    def setRecord(self, result, _):
        noDamage = result.noDamageDirectHitsReceived
        damageBlocked = result.damageBlockedByArmor
        self.usedArmorCount = noDamage
        if noDamage > 0 or damageBlocked > 0:
            self._isEmpty = False
            rickochets = result.rickochetsReceived
            self.armorValues = [BigWorld.wg_getIntegralFormat(rickochets), BigWorld.wg_getIntegralFormat(noDamage), BigWorld.wg_getIntegralFormat(damageBlocked)]
            self.armorNames = [i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_PART1), i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_PART2), i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ARMOR_PART3, vals=style.getTooltipParamsStyle())]


class AssistDetailsBlock(_DetailsBlock):
    __slots__ = ('damageAssisted', 'damageAssistedValues', 'damageAssistedNames', '_isEmpty')

    def __init__(self, meta=None, field='', *path):
        super(AssistDetailsBlock, self).__init__(meta, field, *path)
        self.damageAssisted = None
        self.damageAssistedValues = None
        self.damageAssistedNames = None
        return

    def setRecord(self, result, reusable):
        damageAssistedTrack = result.damageAssistedTrack
        damageAssistedRadio = result.damageAssistedRadio
        damageAssisted = damageAssistedTrack + damageAssistedRadio
        self.damageAssisted = damageAssisted
        if damageAssisted > 0:
            self._isEmpty = False
            self.damageAssistedValues = [BigWorld.wg_getIntegralFormat(damageAssistedRadio), BigWorld.wg_getIntegralFormat(damageAssistedTrack), BigWorld.wg_getIntegralFormat(damageAssisted)]
            tooltipStyle = style.getTooltipParamsStyle()
            self.damageAssistedNames = [i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_PART1, vals=tooltipStyle), i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_PART2, vals=tooltipStyle), i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_ASSIST_TOTAL, vals=tooltipStyle)]


class StunDetailsBlock(_DetailsBlock):
    __slots__ = ('stunNum', 'stunValues', 'stunNames', 'stunDuration', '_isEmpty')

    def __init__(self, meta=None, field='', *path):
        super(StunDetailsBlock, self).__init__(meta, field, *path)
        self.stunNum = None
        self.stunValues = None
        self.stunNames = None
        self.stunDuration = None
        return

    def setRecord(self, result, _):
        count = result.stunNum
        assisted = result.damageAssistedStun
        duration = result.stunDuration
        self.stunNum = count
        self.stunDuration = duration
        if count > 0 or assisted > 0 or duration > 0:
            self._isEmpty = False
            self.stunValues = [BigWorld.wg_getIntegralFormat(assisted), BigWorld.wg_getIntegralFormat(count), BigWorld.wg_getFractionalFormat(duration)]
            self.stunNames = [i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_STUN_PART1, vals=style.getTooltipParamsStyle()), i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_STUN_PART2), i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_STUN_PART3, vals=style.getTooltipParamsStyle(BATTLE_RESULTS.COMMON_TOOLTIP_PARAMS_VAL_SECONDS))]


class CritsDetailsBlock(_DetailsBlock):
    __slots__ = ('critsCount', 'criticalDevices', 'destroyedDevices', 'destroyedTankmen', '_isEmpty')

    def __init__(self, meta=None, field='', *path):
        super(CritsDetailsBlock, self).__init__(meta, field, *path)
        self.critsCount = None
        self.criticalDevices = None
        self.destroyedDevices = None
        self.destroyedTankmen = None
        return

    def setRecord(self, result, reusable):
        crits = result.critsInfo
        criticalDevices = []
        destroyedDevices = []
        destroyedTankmen = []
        for device in crits[CRIT_MASK_SUB_TYPES.CRITICAL_DEVICES]:
            self._isEmpty = False
            criticalDevices.append(style.makeCriticalModuleTooltipLabel(device))

        for device in crits[CRIT_MASK_SUB_TYPES.DESTROYED_DEVICES]:
            self._isEmpty = False
            destroyedDevices.append(style.makeDestroyedModuleTooltipLabel(device))

        for tankman in crits[CRIT_MASK_SUB_TYPES.DESTROYED_TANKMENS]:
            self._isEmpty = False
            destroyedTankmen.append(style.makeTankmenTooltipLabel(tankman))

        self.critsCount = BigWorld.wg_getIntegralFormat(crits['critsCount'])
        self.criticalDevices = style.makeMultiLineHtmlString(criticalDevices)
        self.destroyedDevices = style.makeMultiLineHtmlString(destroyedDevices)
        self.destroyedTankmen = style.makeMultiLineHtmlString(destroyedTankmen)


class TeamBaseDetailsBlock(base.StatsBlock):
    __slots__ = ('_showCapturePoints', '_showDefencePoints', 'captureTotalItems', 'defenceTotalItems', 'captureValues', 'captureNames', 'defenceValues', 'defenceNames', 'label', 'isEnemyBase')

    def __init__(self, meta=None, field='', *path):
        super(TeamBaseDetailsBlock, self).__init__(meta, field, *path)
        self._showCapturePoints = False
        self._showDefencePoints = False
        self.label = None
        self.captureTotalItems = None
        self.defenceTotalItems = None
        self.captureValues = None
        self.captureNames = None
        self.defenceValues = None
        self.defenceNames = None
        self.isEnemyBase = False
        return

    def setRecord(self, result, _):
        capturePoints = result.capturePoints
        defencePoints = result.droppedCapturePoints
        self.captureTotalItems = capturePoints
        self.defenceTotalItems = defencePoints
        if self._showCapturePoints and capturePoints > 0:
            self.captureValues = (BigWorld.wg_getIntegralFormat(capturePoints),)
            self.captureNames = (i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_CAPTURE_TOTALPOINTS),)
        if self._showDefencePoints and defencePoints > 0:
            self.defenceValues = (BigWorld.wg_getIntegralFormat(defencePoints),)
            self.defenceNames = (i18n.makeString(BATTLE_RESULTS.COMMON_TOOLTIP_DEFENCE_TOTALPOINTS),)


class EnemyTeamBaseDetailBlock(TeamBaseDetailsBlock):
    __slots__ = ('_showCapturePoints', 'label', 'isEnemyBase')

    def __init__(self, meta=None, field='', *path):
        super(EnemyTeamBaseDetailBlock, self).__init__(meta, field, *path)
        self._showCapturePoints = True
        self.label = text_styles.standard(i18n.makeString(BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_ENEMYBASE))
        self.isEnemyBase = True


class AllyTeamBaseDetailBlock(TeamBaseDetailsBlock):
    __slots__ = ('_showDefencePoints', 'label')

    def __init__(self, meta=None, field='', *path):
        super(AllyTeamBaseDetailBlock, self).__init__(meta, field, *path)
        self._showDefencePoints = True
        self.label = text_styles.standard(i18n.makeString(BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_ALLYBASE))
        self.isEnemyBase = False


class EnemyDetailsBlock(_DetailsBlock):
    __slots__ = ('vehicleIcon', 'vehicleName', 'vehicleIntCD', 'vehicleID', 'deathReason', 'spotted', 'piercings', 'damageDealt', 'killCount', '_isEmpty')

    def setRecord(self, result, reusable):
        if result.vehicle is not None:
            self._setVehicle(result.vehicle)
        if result.player is not None:
            self._setPlayerInfo(result.player)
        self.deathReason = result.deathReason
        self.spotted = result.spotted
        self.piercings = result.piercings
        self.damageDealt = result.damageDealt
        self.killCount = result.targetKills
        blocks = (DamageDetailsBlock(),
         ArmorUsingDetailsBlock(),
         AssistDetailsBlock(),
         CritsDetailsBlock(),
         StunDetailsBlock())
        self._isEmpty = self.spotted <= 0
        for block in blocks:
            block.setRecord(result, reusable)
            if self._isEmpty:
                self._isEmpty = block.isEmpty()
            self.addComponent(self.getNextComponentIndex(), block)

        return

    def _setVehicle(self, vehicle):
        self.vehicleIcon = getSmallIconPath(vehicle.name)
        self.vehicleName = vehicle.shortUserName

    def _setPlayerInfo(self, info):
        component = DetailsPlayerNameBlock()
        component.setPlayerInfo(info)
        self.addComponent(self.getNextComponentIndex(), component)

    def setDeathReason(self, reason):
        self.deathReason = reason


class TotalEfficiencyDetailsHeader(base.StatsBlock):
    __slots__ = ('kills', 'damageDealt', 'criticalDamages', 'damageBlockedByArmor', 'damageAssisted', 'damageAssistedStun', 'spotted', 'killsTooltip', 'damageDealtTooltip', 'criticalDamagesTooltip', 'damageBlockedTooltip', 'damageAssistedTooltip', 'spottedTooltip', 'damageAssistedStunTooltip', 'hasEfficencyStats')

    def __init__(self, meta=None, field='', *path):
        super(TotalEfficiencyDetailsHeader, self).__init__(meta, field, *path)
        self.kills = None
        self.damageDealt = None
        self.criticalDamages = None
        self.damageBlockedByArmor = None
        self.damageAssisted = None
        self.damageAssistedStun = None
        self.spotted = None
        self.killsTooltip = None
        self.damageDealtTooltip = None
        self.criticalDamagesTooltip = None
        self.damageBlockedTooltip = None
        self.damageAssistedTooltip = None
        self.damageAssistedStunTooltip = None
        self.spottedTooltip = None
        self.hasEfficencyStats = None
        return

    def setRecord(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        if info is None:
            from debug_utils import LOG_ERROR
            LOG_ERROR('ERROR: TotalEfficiencyDetailsHeader:setRecord: getPersonalVehiclesInfo returned NONE!')
            return
        else:
            value = info.kills
            self.kills = numbers.formatInt(value, _UNDEFINED_EFFICIENCY_VALUE)
            self.killsTooltip = self.__makeEfficiencyHeaderTooltip('summKill', value)
            value = info.damageDealt
            self.damageDealt = numbers.makeStringWithThousandSymbol(value)
            self.damageDealtTooltip = self.__makeEfficiencyHeaderTooltip('summDamage', value)
            value = info.critsCount
            self.criticalDamages = numbers.formatInt(value, _UNDEFINED_EFFICIENCY_VALUE)
            self.criticalDamagesTooltip = self.__makeEfficiencyHeaderTooltip('summCrits', value)
            value = info.damageBlockedByArmor
            self.damageBlockedByArmor = numbers.makeStringWithThousandSymbol(value)
            self.damageBlockedTooltip = self.__makeEfficiencyHeaderTooltip('summArmor', value)
            value = info.damageAssisted
            self.damageAssisted = numbers.makeStringWithThousandSymbol(value)
            self.damageAssistedTooltip = self.__makeEfficiencyHeaderTooltip('summAssist', value)
            value = info.damageAssistedStun
            self.damageAssistedStun = numbers.makeStringWithThousandSymbol(value)
            self.damageAssistedStunTooltip = self.__makeEfficiencyHeaderTooltip('summStun', value)
            value = info.spotted
            self.spotted = numbers.formatInt(value, _UNDEFINED_EFFICIENCY_VALUE)
            self.spottedTooltip = self.__makeEfficiencyHeaderTooltip('summSpotted', value)
            self.hasEfficencyStats = info.kills + info.damageDealt + info.critsCount + info.damageBlockedByArmor + info.damageAssisted + info.damageAssistedStun + info.spotted > 0
            return

    @classmethod
    def __makeEfficiencyHeaderTooltip(cls, key, value):
        if value > 0:
            header = TOOLTIPS.battleresults_efficiencyheader(key)
            body = BigWorld.wg_getIntegralFormat(value)
            return makeTooltip(header, body)
        else:
            return None


class TotalEfficiencyDetailsBlock(base.StatsBlock):
    __slots__ = ()

    def setRecord(self, result, reusable):
        blocks = []
        for bases, enemies in reusable.getPersonalDetailsIterator(result):
            components = []
            for info in bases:
                if info.capturePoints > 0 or info.droppedCapturePoints > 0:
                    components.append(style.GroupMiddleLabelBlock(BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_BASES))
                    component = EnemyTeamBaseDetailBlock()
                    component.setRecord(info, reusable)
                    components.append(component)
                    component = AllyTeamBaseDetailBlock()
                    component.setRecord(info, reusable)
                    components.append(component)

            block = base.StatsBlock(base.ListMeta())
            detailedBlocks = []
            for info in enemies:
                component = EnemyDetailsBlock()
                component.setRecord(info, reusable)
                if not component.isEmpty():
                    detailedBlocks.append(component)

            if detailedBlocks:
                block.addComponent(block.getNextComponentIndex(), style.GroupMiddleLabelBlock(BATTLE_RESULTS.COMMON_BATTLEEFFICIENCY_TECHNIQUE))
                for db in detailedBlocks:
                    block.addComponent(block.getNextComponentIndex(), db)

            for component in components:
                block.addComponent(block.getNextComponentIndex(), component)

            blocks.append(block)

        for block in blocks[-1:] + blocks[:-1]:
            self.addComponent(self.getNextComponentIndex(), block)


class TotalPersonalAchievementsBlock(shared.BiDiStatsBlock):
    __slots__ = ()

    def addComponent(self, index, component):
        super(TotalPersonalAchievementsBlock, self).addComponent(index, component)

    def setRecord(self, result, reusable):
        left, right = reusable.personal.getAchievements(result)
        self.left.setRecord(left, reusable)
        self.right.setRecord(right, reusable)


class SandboxNoIncomeAlert(base.StatsBlock):
    __slots__ = ('icon', 'text')

    def __init__(self, meta=None, field='', *path):
        super(SandboxNoIncomeAlert, self).__init__(meta, field, *path)
        self.icon = ''
        self.text = ''

    def setRecord(self, result, _):
        self.icon = RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON
        builder = text_styles.builder(delimiter='\n')
        builder.addStyledText(text_styles.middleTitle, BATTLE_RESULTS.COMMON_NOINCOME_ALERT_TITLE)
        builder.addStyledText(text_styles.standard, BATTLE_RESULTS.COMMON_NOINCOME_ALERT_TEXT)
        self.text = builder.render()


class PersonalAccountDBID(base.StatsItem):

    def _convert(self, value, reusable):
        return reusable.personal.avatar.accountDBID


def fillKillerInfoBlock(vehicleStateBlock, deathReason, killerID, reusable):
    reason = style.makeI18nDeathReason(deathReason)
    vehicleStateBlock.vehicleState = reason.i18nString
    vehicleStateBlock.vehicleStatePrefix = reason.prefix
    vehicleStateBlock.vehicleStateSuffix = reason.suffix
    pi = reusable.getPlayerInfoByVehicleID(killerID)
    playerKillerBlock = KillerPlayerNameBlock()
    playerKillerBlock.setPlayerInfo(pi)
    vi = reusable.vehicles.getVehicleInfo(killerID)
    if vi.isTeamKiller:
        playerKillerBlock.setTeamKillerInfo()
        vehicleStateBlock.isKilledByTeamKiller = True
    vehicleStateBlock.addComponent(vehicleStateBlock.getNextComponentIndex(), playerKillerBlock)
