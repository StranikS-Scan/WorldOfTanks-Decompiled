# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/crew2/crew2_pdata_utils.py
from game_region_params import get as getGameParams
from nation_change.nation_change_helpers import activeInNationGroup

def getFreeDormitoryRooms(centerID, pdata):
    rawRooms = pdata['stats']['dormitories'] * getGameParams(centerID)['economics']['dormitory']['number_rooms']
    ncRooms = sum((1 for vehID in pdata['inventory'][1]['compDescr'] if not activeInNationGroup(pdata['inventory'][1]['extraSettings'][vehID])))
    return rawRooms + pdata['stats']['slots'] + ncRooms + len(pdata['inventory'][15]['recycleBin']) - len(pdata['inventory'][1]['rent']) - len(pdata['inventory'][15]['compDescr'])


def hasFreeDormitoryRooms(centerID, pdata):
    return getFreeDormitoryRooms(centerID, pdata) > 0
