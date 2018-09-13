# Embedded file name: scripts/client/gui/Scaleform/daapi/abstract.py
from debug_utils import LOG_DEBUG

class StatsStorageMeta(object):

    def as_setExperienceS(self, experience):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setExperience(experience)
        return

    def as_setTankmanIdS(self, id):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setTankmanId(id)
        return

    def as_setCreditsS(self, credits):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setCredits(credits)
        return

    def as_setGoldS(self, gold):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setGold(gold)
        return

    def as_setPremiumS(self, premium):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setPremium(premium)
        return

    def as_setVehicleS(self, vehicle):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setVehicle(vehicle)
        return

    def as_setPlayerSpeakingS(self, dbId, isSpeak, isSelf):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setPlayerSpeaking(dbId, isSpeak, isSelf)
        return

    def as_setAccountAttrsS(self, attrs):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setAccountAttrs(attrs)
        return

    def as_setDenunciationsCountS(self, denunciationsCount):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setDenunciationsCount(denunciationsCount)
        return

    def as_setNationsS(self, nations):
        if self.flashObject is None:
            LOG_DEBUG('flash object can`t be None!')
        else:
            self.flashObject.as_setNations(nations)
        return
