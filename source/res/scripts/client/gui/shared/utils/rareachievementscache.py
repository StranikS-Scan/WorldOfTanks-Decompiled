# Embedded file name: scripts/client/gui/shared/utils/RareAchievementsCache.py
from functools import partial
import ResMgr
import re
import Event
from debug_utils import *
from helpers import i18n, getClientLanguage
from account_helpers.rare_achievements import getRareAchievementImage, getRareAchievementImageBig, getRareAchievementText

class IMAGE_TYPE:
    IT_67X71 = 1
    IT_180X180 = 2


class IMAGE_PATH:
    IT_67X71 = 'gui/maps/icons/achievement/'
    IT_180X180 = 'gui/maps/icons/achievement/big/'


class _RaresCache(object):
    DEFAULT_TITLE = i18n.makeString('#tooltips:achievement/action/unavailable/title')
    DEFAULT_DESCR = i18n.makeString('#tooltips:achievement/action/unavailable/descr')
    RARE_ACHIEVEMENT_PREFIX = 'rare'
    RARE_ACHIEVEMENT_PATTERN = '^%s([0-9]+)' % RARE_ACHIEVEMENT_PREFIX
    RARE_ACHIEVEMENT_ICON_PATTERN = '^%s[0-9]+\\.png$' % RARE_ACHIEVEMENT_PREFIX

    def __init__(self):
        self.__cache = dict()
        self.__local = set()
        self.onTextReceived = Event.Event()
        self.onImageReceived = Event.Event()
        achieveIDPattern = re.compile(self.RARE_ACHIEVEMENT_PATTERN)
        iconPattern = re.compile(self.RARE_ACHIEVEMENT_ICON_PATTERN)
        rareIcons67x71 = ResMgr.openSection(IMAGE_PATH.IT_67X71)
        rareIcons180x180 = ResMgr.openSection(IMAGE_PATH.IT_180X180)
        listOfIcons = set()
        listOfIcons.update(filter(iconPattern.match, rareIcons67x71.keys()))
        listOfIcons.update(filter(iconPattern.match, rareIcons180x180.keys()))
        for icon in listOfIcons:
            rareName = achieveIDPattern.search(icon).group()
            rareID = self.__getRareAchievementID(rareName)
            self.__local.add(rareID)
            achieveData = self.__cache[rareID] = {'image': {}}
            try:
                achieveData['image'][IMAGE_TYPE.IT_67X71] = rareIcons67x71[icon].asBinary
            except:
                LOG_WARNING('Cannot load rare achievement local file', icon)
                LOG_CURRENT_EXCEPTION()

            try:
                achieveData['image'][IMAGE_TYPE.IT_180X180] = rareIcons180x180[icon].asBinary
            except:
                LOG_WARNING('Cannot load rare achievement local file', icon)

            achieveData['title'] = i18n.makeString('#achievements:%s' % rareName)
            achieveData['descr'] = i18n.makeString('#achievements:%s_descr' % rareName)
            heroInfoKey = '%s_heroInfo' % rareName
            heroInfoMsg = i18n.makeString('#achievements:%s' % heroInfoKey)
            if heroInfoMsg != heroInfoKey:
                achieveData['historyInfo'] = heroInfoMsg
            condKey = '%s_condition' % rareName
            condMsg = i18n.makeString('#achievements:%s' % condKey)
            if condMsg != condKey:
                achieveData['conditions'] = condMsg

    def request(self, listOfIds):
        LOG_DEBUG('Request action achievements data', listOfIds)
        if not len(listOfIds):
            return
        landId = getClientLanguage()
        for achieveId in listOfIds:
            if self.isLocallyLoaded(achieveId):
                LOG_DEBUG('Action achievements data loaded locally', achieveId)
                continue
            getRareAchievementText(landId, achieveId, self.__onTextReceived)
            getRareAchievementImage(achieveId, partial(self.__onImageReceived, IMAGE_TYPE.IT_67X71))
            getRareAchievementImageBig(achieveId, partial(self.__onImageReceived, IMAGE_TYPE.IT_180X180))

    def __onTextReceived(self, rareID, text):
        achieveData = self.__cache.setdefault(rareID, dict())
        title = text.get('title')
        descr = text.get('description')
        info = text.get('historyInfo')
        cond = text.get('conditions')

        def valueChanged(key, value):
            return value is not None and (key not in achieveData or achieveData[key] != value)

        descrChanged = valueChanged('descr', descr)
        titleChanged = valueChanged('title', title)
        infoChanged = valueChanged('historyInfo', info)
        condChanged = valueChanged('conditions', cond)
        isGenerateEvent = descrChanged or titleChanged or infoChanged or condChanged
        if descr is not None:
            achieveData['descr'] = descr
        if title is not None:
            achieveData['title'] = title
        if info is not None:
            achieveData['historyInfo'] = info
        if cond is not None:
            achieveData['conditions'] = cond
        if isGenerateEvent:
            LOG_DEBUG('Text received for achievement', text)
            self.onTextReceived(rareID, achieveData)
        return

    def __onImageReceived(self, imgType, imgID, imageData):
        achieveData = self.__cache.setdefault(imgID, dict())
        achieveImgData = achieveData.setdefault('image', {})
        if imageData is None:
            return
        else:
            isGenerateEvent = imgType not in achieveImgData or achieveImgData[imgType] != imageData
            achieveImgData[imgType] = imageData
            if isGenerateEvent:
                LOG_DEBUG('Image received for achievement', imgType, imgID, type(imageData))
                self.onImageReceived(imgType, imgID, imageData)
            return

    def isLocallyLoaded(self, achieveID):
        return achieveID in self.__local

    def getTitle(self, achieveID):
        return self.__cache.get(achieveID, dict()).get('title') or _RaresCache.DEFAULT_TITLE

    def getDescription(self, achieveID):
        return self.__cache.get(achieveID, dict()).get('descr') or _RaresCache.DEFAULT_DESCR

    def getImageData(self, imgType, achieveID):
        return self.__cache.get(achieveID, dict()).get('image', {}).get(imgType)

    def getHeroInfo(self, achieveID):
        return self.__cache.get(achieveID, dict()).get('historyInfo')

    def getConditions(self, achieveID):
        return self.__cache.get(achieveID, dict()).get('conditions')

    @classmethod
    def __getRareAchievementID(cls, rareName):
        return int(rareName.replace(cls.RARE_ACHIEVEMENT_PREFIX, ''))


g_rareAchievesCache = _RaresCache()
