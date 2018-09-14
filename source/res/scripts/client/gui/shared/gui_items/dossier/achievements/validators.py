# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/validators.py
from gui.shared.fortifications import isFortificationEnabled

def questHasThisAchievementAsBonus(name, block):
    from gui.server_events import g_eventsCache
    for records in g_eventsCache.getQuestsDossierBonuses().itervalues():
        if (block, name) in records:
            return True

    return False


def alreadyAchieved(achievementClass, name, block, dossier):
    return achievementClass.checkIsInDossier(block, name, dossier)


def requiresFortification():
    return isFortificationEnabled()


def accountIsRoaming(dossier):
    return dossier.isInRoaming()
