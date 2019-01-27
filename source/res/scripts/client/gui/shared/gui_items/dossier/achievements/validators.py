# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/validators.py
from constants import IS_WEB
if IS_WEB:

    def questHasThisAchievementAsBonus(name, block):
        return False


    def alreadyAchieved(achievementClass, name, block, dossier):
        return False


    def requiresFortification():
        return False


    def requiresReferralProgram():
        return False


    def accountIsRoaming(dossier):
        return False


else:
    from helpers import dependency
    from skeletons.gui.lobby_context import ILobbyContext
    from skeletons.gui.server_events import IEventsCache

    def questHasThisAchievementAsBonus(name, block):
        eventsCache = dependency.instance(IEventsCache)
        for records in eventsCache.getQuestsDossierBonuses().itervalues():
            if (block, name) in records:
                return True

        return False


    def alreadyAchieved(achievementClass, name, block, dossier):
        return achievementClass.checkIsInDossier(block, name, dossier)


    def requiresFortification():
        lobbyContext = dependency.instance(ILobbyContext)
        return lobbyContext.getServerSettings() is not None and lobbyContext.getServerSettings().isStrongholdsEnabled()


    def requiresReferralProgram():
        lobbyContext = dependency.instance(ILobbyContext)
        return lobbyContext.getServerSettings() is not None and lobbyContext.getServerSettings().isReferralProgramEnabled()


    def accountIsRoaming(dossier):
        return dossier.isInRoaming()
