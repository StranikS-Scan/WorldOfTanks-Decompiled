# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/slides.py
from typing import Tuple, List, Dict
from collections import namedtuple
import ResMgr
from gui.battle_control.arena_info.settings import SCREEN_MAP_IMAGE_RES_PATH
from helpers import i18n
from items import _xml
PATH = 'historical_battles/gui/loading_screen_slides.xml'

class SlideData(namedtuple('SlideData', 'title description background backgroundF1')):

    def getLoadingData(self):
        return {'title': self.title,
         'description': self.description,
         'background': self.background}

    def getBattleData(self):
        return {'title': self.title,
         'description': self.description,
         'background': self.backgroundF1}


class LoadingScreenSlidesCfg(object):
    _instance = None
    __slots__ = ('_loadingScreens',)

    def __init__(self):
        self._loadingScreens = {}

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = LoadingScreenSlidesCfg()
            cls._instance.loadFromXml(PATH)
        return cls._instance

    def getLoadingScreen(self, name):
        ls = self._loadingScreens.get(name)
        if ls:
            return ls
        dls = LoadingScreenSlides()
        dls.initDefault(name)
        return dls

    def loadFromXml(self, path):
        section = ResMgr.openSection(path)
        xmlCtx = (path, None)
        if section is None:
            _xml.raiseWrongXml(xmlCtx, path, 'can not open or read')
        self._loadingScreens = {}
        for subsection in section.values():
            lss = LoadingScreenSlides()
            lss.initFromXML(xmlCtx, subsection)
            self._loadingScreens[lss.spaceName] = lss

        ResMgr.purge(path)
        return


class LoadingScreenSlides(object):
    __slots__ = ('_spaceName', '_slides')

    def __init__(self):
        self._spaceName = ''
        self._slides = []

    def initDefault(self, spaceName):
        self._spaceName = spaceName
        slide = SlideData(spaceName, 'This arena has no slides in {}'.format(PATH), 'img://{}'.format(SCREEN_MAP_IMAGE_RES_PATH % spaceName), 'img://{}'.format(SCREEN_MAP_IMAGE_RES_PATH % spaceName))
        self._slides.append(slide)

    def initFromXML(self, xmlCtx, section):
        self._spaceName = _xml.readString(xmlCtx, section, 'spaceName')
        xmlCtx2 = (xmlCtx, self._spaceName)
        for slideSection in section['slides'].values():
            titleKey = _xml.readString(xmlCtx2, slideSection, 'title')
            descriptionKey = _xml.readString(xmlCtx2, slideSection, 'description')
            background = _xml.readString(xmlCtx2, slideSection, 'background')
            backgroundF1 = _xml.readString(xmlCtx2, slideSection, 'background_f1')
            self._slides.append(SlideData(i18n.makeString(titleKey), i18n.makeString(descriptionKey), background, backgroundF1))

    @property
    def spaceName(self):
        return self._spaceName

    @property
    def slides(self):
        return self._slides
