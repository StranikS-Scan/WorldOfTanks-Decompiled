# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/profile/comp7_profile_helper.py
from gui.Scaleform.daapi.view.lobby.profile.ProfileSection import DropdownData
COMP7_SEASON_NUMBERS = (1, 2)
COMP7_ARCHIVE_NAMES = ('Griffin', 'Pegasus')
COMP7_ARCHIVE_DROPDOWN_KEY_PREFIX = 'comp7_archive_'
COMP7_SEASON_DROPDOWN_KEY_PREFIX = 'comp7_season_'

def isComp7Archive(battleType):
    return battleType.startswith(COMP7_ARCHIVE_DROPDOWN_KEY_PREFIX)


def isComp7Season(battleType):
    return battleType.startswith(COMP7_SEASON_DROPDOWN_KEY_PREFIX)


def getArchiveName(battleType):
    _, __, archiveName = battleType.rpartition(COMP7_ARCHIVE_DROPDOWN_KEY_PREFIX)
    return archiveName


def getSeasonName(battleType):
    _, __, seasonName = battleType.rpartition(COMP7_SEASON_DROPDOWN_KEY_PREFIX)
    return seasonName


def getDropdownKeyByArchiveName(archiveName):
    return '{}{}'.format(COMP7_ARCHIVE_DROPDOWN_KEY_PREFIX, archiveName)


def getDropdownKeyBySeason(season):
    return '{}{}'.format(COMP7_SEASON_DROPDOWN_KEY_PREFIX, season)


def getBattleHandlers():
    result = {}
    for archiveName in COMP7_ARCHIVE_NAMES:
        dropdownKey = getDropdownKeyByArchiveName(archiveName)
        result[dropdownKey] = DropdownData(False, 'getComp7Stats', {'archive': archiveName})

    for season in COMP7_SEASON_NUMBERS:
        dropdownKey = getDropdownKeyBySeason(season)
        result[dropdownKey] = DropdownData(False, 'getComp7Stats', {'season': season})

    return result
