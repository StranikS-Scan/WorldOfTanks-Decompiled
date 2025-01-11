# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/ny_common/ResourceCollectingConfig.py
from ny_common.settings import ResourceCollectingConsts
from typing import Optional, List, Dict, Union

class ResourceCollectingConfig(object):

    def __init__(self, config):
        self._config = config

    def getCollectingsDescriptors(self):
        return map(CollectingDescriptor, self._config.get(ResourceCollectingConsts.COLLECTINGS))

    def getCollectingDescriptorByIndex(self, idx):
        collectings = self._config.get(ResourceCollectingConsts.COLLECTINGS)
        return collectings and (CollectingDescriptor(collectings[idx]) if 0 <= idx < len(collectings) else None)

    def getNextCollectingDescriptor(self, activeIndex):
        collectings = self._config.get(ResourceCollectingConsts.COLLECTINGS)
        if collectings is None or len(collectings) == 0:
            return
        else:
            return CollectingDescriptor(collectings[0]) if activeIndex is None else CollectingDescriptor(collectings[activeIndex + 1 if len(collectings) > activeIndex + 1 else 0])

    def getFriendResources(self):
        return self._config.get(ResourceCollectingConsts.FRIEND_RESOURCES, {})

    def getCollectingNotifyTimeout(self):
        return self._config.get(ResourceCollectingConsts.NOTIFY_TIMEOUT, 0)

    def getNoFriendsNotifyTimeout(self):
        return self._config.get(ResourceCollectingConsts.NOTIFY_NO_FRIENDS_TIMEOUT, 0)


class CollectingDescriptor(object):

    def __init__(self, config):
        self._config = config

    def getID(self):
        return self._config.get(ResourceCollectingConsts.COLLECTING_ID)

    @staticmethod
    def getSkippedDaysAmount(lastCollectingDay, currentDay):
        dayDelta = currentDay - lastCollectingDay
        if dayDelta < 0:
            return dayDelta
        return dayDelta - 1 if dayDelta > 0 else 0

    def getResources(self, skippedDays):
        resourcesCollecting = self._config.get(ResourceCollectingConsts.RESOURCES_COLLECTING, [])
        return {} if skippedDays < 0 or len(resourcesCollecting) == 0 else resourcesCollecting[skippedDays if skippedDays < len(resourcesCollecting) else -1]

    def getCollectingCooldown(self):
        return self._config.get(ResourceCollectingConsts.COOLDOWN, None)
