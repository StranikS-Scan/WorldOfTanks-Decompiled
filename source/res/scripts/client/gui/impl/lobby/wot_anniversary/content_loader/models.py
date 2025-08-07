# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wot_anniversary/content_loader/models.py
import typing
from enum import unique, Enum
if typing.TYPE_CHECKING:
    from ResMgr import DataSection

@unique
class BackgroundID(str, Enum):
    FIRST_PAGE = 'first_page'
    SECOND_PAGE = 'second_page'


VIDEOS_CONTENT_NAME = 'videos'

class BaseContent(object):

    def isContentLoaded(self):
        raise NotImplementedError


class BackgroundContent(BaseContent):

    def __init__(self, small, medium, large, extraLarge):
        self.small = small
        self.medium = medium
        self.large = large
        self.extraLarge = extraLarge

    def isContentLoaded(self):
        return all([self.small,
         self.medium,
         self.large,
         self.extraLarge])

    def __repr__(self):
        return '<BackgroundContent(small={}, large={})>'.format(self.small, self.large)


class DayContent(BaseContent):

    def __init__(self, image, imageLarge, localizations, video):
        self.image = image
        self.imageLarge = imageLarge
        self.localizations = localizations
        self.video = video

    def isContentLoaded(self):
        return all([self.image,
         self.imageLarge,
         self.localizations,
         self.video])

    def __repr__(self):
        return '<DayContent(image={}, imageLarge={}, localizations={}, video={})>'.format(self.image, self.imageLarge, self.localizations, self.video)


class VideosContent(BaseContent):

    def __init__(self, conversionOneEnv, conversionTwoEnvs, conversionThreeEnvs, turnPage):
        self.conversionOneEnv = conversionOneEnv
        self.conversionTwoEnvs = conversionTwoEnvs
        self.conversionThreeEnvs = conversionThreeEnvs
        self.turnPage = turnPage

    def isContentLoaded(self):
        return all([self.conversionOneEnv,
         self.conversionTwoEnvs,
         self.conversionThreeEnvs,
         self.turnPage])

    def __repr__(self):
        return '<VideosContent(conversionOneEnv={}, conversionTwoEnvs={}, conversionThreeEnvs={}, turnPage={})>'.format(self.conversionOneEnv, self.conversionTwoEnvs, self.conversionThreeEnvs, self.turnPage)
