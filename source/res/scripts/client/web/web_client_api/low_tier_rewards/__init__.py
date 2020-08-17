# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/low_tier_rewards/__init__.py
from helpers import dependency
from skeletons.gui.game_control import ILowTierMMController
from skeletons.gui.shared import IItemsCache
from web.web_client_api import w2capi, W2CSchema, w2c
from dossiers2.ui.achievements import MARK_ON_GUN_RECORD

@w2capi(name='low_tier', key='action')
class LowTierRewardsWebApi(W2CSchema):
    itemsCache = dependency.descriptor(IItemsCache)
    __eventController = dependency.descriptor(ILowTierMMController)

    @w2c(W2CSchema, name='is_MM_enabled')
    def isMMEnabled(self, cmd):
        return {'action': self.__eventController.isEnabled()}

    @w2c(W2CSchema, name='get_MM_end')
    def getMMEnd(self, cmd):
        return {'action': self.__eventController.getDateFinish()}

    @w2c(W2CSchema, 'get_stats')
    def getStats(self, command):
        try:
            dossier = self.itemsCache.items.getAccountDossier()
        except Exception:
            battlesCount = None
            damageDealtAvg = None
            threeMarks = None
            damageAssistedAvg = None
            spottedCountAvg = None
            hitsRatio = None
            capturePoints = None
            drCapturePoints = None
            achievementsCount = None
            shotsCount = None
            fragsCount = None
            treesCutCount = None
        else:
            battlesCount = dossier.getRandomStats().getBattlesCount
            damageDealtAvg = dossier.getRandomStats().getAvgDamage
            threeMarks = self.getThreeMarksOnGun
            damageAssistedAvg = dossier.getRandomStats().getDamageAssistedEfficiency
            spottedCountAvg = dossier.getRandomStats().getAvgEnemiesSpotted
            hitsRatio = self.getHitsRatio
            capturePoints = dossier.getRandomStats().getCapturePoints
            drCapturePoints = dossier.getRandomStats().getDroppedCapturePoints
            achievementsCount = self.getAchievementCount
            shotsCount = dossier.getRandomStats().getShotsCount
            fragsCount = dossier.getRandomStats().getFragsCount
            treesCutCount = dossier.getGlobalStats().getTreesCut

        data = {'battles_count': self.__tryGetParam(battlesCount),
         'accumulative': {'damage_dealt_avg': self.__tryGetParam(damageDealtAvg),
                          'three_marks_on_gun_tanks_count': self.__tryGetParam(threeMarks),
                          'damage_assisted_avg': self.__tryGetParam(damageAssistedAvg),
                          'spotted_count_avg': self.__tryGetParam(spottedCountAvg),
                          'hits_ratio': self.__tryGetParam(hitsRatio),
                          'capture_points': self.__tryGetParam(capturePoints),
                          'dropped_capture_points': self.__tryGetParam(drCapturePoints),
                          'achievements_count': self.__tryGetParam(achievementsCount)},
         'peak': {'shots_count': self.__tryGetParam(shotsCount),
                  'frags_count': self.__tryGetParam(fragsCount),
                  'trees_cut_count': self.__tryGetParam(treesCutCount)}}
        return data

    def getThreeMarksOnGun(self):
        vehicles = self.itemsCache.items.getAccountDossier().getRandomStats().getVehicles()
        threeMarksOnGunCount = 0
        for intCD in vehicles:
            vehDossier = self.itemsCache.items.getVehicleDossier(intCD)
            vehStats = vehDossier.getTotalStats()
            marksOnGun = vehStats.getAchievement(MARK_ON_GUN_RECORD)
            if marksOnGun.getValue() > 2:
                threeMarksOnGunCount += 1

        return threeMarksOnGunCount

    def getAchievementCount(self):
        achievements = self.itemsCache.items.getAccountDossier().getTotalStats().getAchievements(isInDossier=True)
        achivementsCount = 0
        for achievement in achievements:
            achivementsCount += len(achievement)

        return achivementsCount

    def getHitsRatio(self):
        hitsRatio = self.itemsCache.items.getAccountDossier().getRandomStats().getHitsEfficiency()
        hitsRatioPercent = hitsRatio * 100
        return hitsRatioPercent

    @staticmethod
    def __tryGetParam(func):
        if func is None:
            return
        else:
            try:
                param = func()
            except Exception:
                param = None

            return param
