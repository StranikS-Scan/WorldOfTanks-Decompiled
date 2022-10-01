# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/vo_converters.py
from gui.Scaleform.daapi.view.lobby.cyberSport import PLAYER_GUI_STATUS
from gui.Scaleform.daapi.view.lobby.rally.vo_converters import makeSlotsVOs, MAX_PLAYER_COUNT_ALL, makeTotalLevelLabel, makeUnitStateLabel
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.prb_control import settings
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import i18n
from shared_utils import BitmaskHelper

class FILTER_STATE(BitmaskHelper):
    ALL = 0
    LIGHT_TANK = 1
    MEDIUM_TANK = 2
    HEAVY_TANK = 4
    SPG = 8
    AT_SPG = 16
    VEHICLE_TYPES = ((LIGHT_TANK, VEHICLE_CLASS_NAME.LIGHT_TANK),
     (MEDIUM_TANK, VEHICLE_CLASS_NAME.MEDIUM_TANK),
     (HEAVY_TANK, VEHICLE_CLASS_NAME.HEAVY_TANK),
     (AT_SPG, VEHICLE_CLASS_NAME.AT_SPG),
     (SPG, VEHICLE_CLASS_NAME.SPG))


def _convertVehClassNamesToState(vehClassNames):
    state = FILTER_STATE.ALL
    for bType, vType in FILTER_STATE.VEHICLE_TYPES:
        if vType in vehClassNames:
            state |= bType

    return state


def makeStrongholdsSlotsVOs(unitEntity, unitMgrID=None, maxPlayerCount=MAX_PLAYER_COUNT_ALL):
    isRosterSet, slots = makeSlotsVOs(unitEntity, unitMgrID, maxPlayerCount)
    isCommander = unitEntity.isCommander()
    fullData = unitEntity.getUnitFullData(unitMgrID=unitMgrID)
    isPlayersMatchingAvailable = unitEntity.isPlayersMatchingAvailable()
    slotFilters = unitEntity.getSlotFilters().items()
    vehTypesInSlotFilters = {slotId:_convertVehClassNamesToState(item.get('vehicle_types', [])) for slotId, item in slotFilters}
    vehiclesInSlotFilters = {slotId:item.get('vehicle_cds', []) for slotId, item in slotFilters}
    canSetupPlayersMatching = isPlayersMatchingAvailable and isCommander
    rosterSettings = unitEntity.getRosterSettings()
    legionariesMaxCount = rosterSettings.getLegionariesMaxCount()
    legionariesInRoster = fullData.stats.legionariesInRoster
    playersMatchingSlotsCount = fullData.stats.playersMatchingSlotsCount
    maxLegionariesNotReached = legionariesMaxCount > legionariesInRoster + playersMatchingSlotsCount
    slotsInPlayersMatching = unitEntity.getSlotsInPlayersMatching()
    unitInPlayersMatchingMode = unitEntity.inPlayersMatchingMode()
    for idx, slot in enumerate(slots):
        if slot['isLocked']:
            break
        vehTypesInSlot = vehTypesInSlotFilters.get(idx, 0)
        vehiclesInSlot = vehiclesInSlotFilters.get(idx, ())
        slot['isMatchingEnabled'] = canSetupPlayersMatching
        slot['isFiltersEnabled'] = maxLegionariesNotReached
        if slot['player'] is not None:
            slot['filterState'] = 0
            slot['vehicles'] = ()
            slot['isRemoveAvailable'] = unitEntity.getPermissions().canAssignToSlot(slot['player']['dbID'])
            continue
        slot['filterState'] = vehTypesInSlot
        slot['vehicles'] = vehiclesInSlot
        if idx in slotsInPlayersMatching or unitInPlayersMatchingMode:
            if isCommander:
                slotLabel = i18n.makeString(FORTIFICATIONS.SORTIE_MEMBER_SLOT_FOR_LEGIONARY)
            else:
                slotLabel = i18n.makeString(FORTIFICATIONS.SORTIE_MEMBER_SLOT_FOR_LEGIONARY_SEARCH)
            slot.update({'canBeTaken': False,
             'isLegionaries': True,
             'slotLabel': slotLabel,
             'playerStatus': PLAYER_GUI_STATUS.READY,
             'isFiltersEnabled': True})
        if slot['isLegionaries'] and slot['selectedVehicle'] and not slot['isFreezed'] and not slot['isCommanderState']:
            slot['selectedVehicle']['isReadyToFight'] = True

    return (isRosterSet, slots)


def makeSortieVO(unitEntity, isCommander, unitMgrID=None, canInvite=True, maxPlayerCount=MAX_PLAYER_COUNT_ALL):
    fullData = unitEntity.getUnitFullData(unitMgrID=unitMgrID)
    levelsValidation = unitEntity.validateLevels()
    canDoAction, restriction = levelsValidation.isValid, levelsValidation.restriction
    sumLevelsStr = makeTotalLevelLabel(fullData.stats, restriction)
    _, slots = makeStrongholdsSlotsVOs(unitEntity, unitMgrID, maxPlayerCount)
    if fullData.playerInfo.isInSlot:
        disableCanBeTakenButtonInSlots(slots)
    if fullData.flags.isLocked() or unitEntity.isStrongholdUnitFreezed() or unitEntity.inPlayersMatchingMode():
        setFreezedInSlots(slots)
        canAssignToSlot = False
    else:
        canAssignToSlot = canInvite
    return {'canInvite': canInvite,
     'isCommander': isCommander,
     'isFreezed': fullData.flags.isLocked(),
     'canAssignToSlot': canAssignToSlot,
     'hasRestrictions': fullData.unit.isRosterSet(ignored=settings.CREATOR_ROSTER_SLOT_INDEXES),
     'statusLbl': makeUnitStateLabel(fullData.flags),
     'statusValue': fullData.flags.isOpened(),
     'sumLevelsInt': fullData.stats.curTotalLevel,
     'sumLevels': sumLevelsStr,
     'sumLevelsError': canDoAction,
     'slots': slots,
     'description': unitEntity.getCensoredComment(unitMgrID=unitMgrID)}


def disableCanBeTakenButtonInSlots(slots):
    for player in slots:
        if player['player'] is None:
            player['canBeTaken'] = False

    return slots


def setFreezedInSlots(slots):
    for player in slots:
        if player['player'] is not None and player['selectedVehicle'] is not None:
            player['isFreezed'] = True
            player['isDragNDropFreezed'] = False
        player['canBeTaken'] = False

    return slots
