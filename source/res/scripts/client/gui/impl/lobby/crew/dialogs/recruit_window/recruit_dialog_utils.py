# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/dialogs/recruit_window/recruit_dialog_utils.py
from gui.impl.gen.resources import R
from gui.impl import backport
from gui.server_events import recruit_helper
from gui.shared.utils.functions import replaceHyphenToUnderscore
RECRUIT_BG_DYN = R.images.gui.maps.icons.tankmen.windows.recruits.recruit_dialog

def getTitle(name=None):
    if name:
        title = backport.text(R.strings.dialogs.recruitDialog.name.title(), name=name)
    else:
        title = backport.text(R.strings.dialogs.recruitDialog.title())
    return title


def getTitleFromTokenData(tokenData):
    name = tokenData.getFullUserNameByNation().strip()
    if tokenData.getSmallIcon() in (recruit_helper._TANKWOMAN_ICON, recruit_helper._TANKMAN_ICON):
        name = None
    return getTitle(name)


def getIconName(iconID):
    return iconID.split('.')[0]


def getIcon(iconName='', isFemale=False):
    specialID = R.images.gui.maps.icons.tankmen.icons.special.dyn(attr='{}'.format(replaceHyphenToUnderscore(iconName)))
    if specialID is not None and specialID.exists():
        return (specialID(), True)
    else:
        bigID = R.images.gui.maps.icons.tankmen.icons.big.dyn(attr='{}'.format(replaceHyphenToUnderscore(iconName)))
        if bigID is not None and bigID.exists():
            return (bigID(), False)
        icon = recruit_helper._TANKMAN_ICON if not isFemale else recruit_helper._TANKWOMAN_ICON
        return (R.images.gui.maps.icons.tankmen.icons.special.dyn(replaceHyphenToUnderscore(getIconName(icon)))(), True)


def getIconBackground(resurceID=None, dynIconName=None, dynPath=RECRUIT_BG_DYN):
    for event in recruit_helper.RecruitSourceID.EVENTS:
        if resurceID and event in resurceID or dynIconName and event in dynIconName:
            return dynPath.bg_recruitment_twitch()

    return dynPath.bg_recruitment_ny() if resurceID and resurceID[:2] == 'ny' else dynPath.bg_recruitment_regular()


def getSortedItems(unsortedItems, itemsOrderedList):
    sortedItems = []
    for name in itemsOrderedList:
        if name in unsortedItems:
            sortedItems.append(name)

    return sortedItems
