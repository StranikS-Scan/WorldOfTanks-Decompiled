# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ny/ny_collections.py
from gui import makeHtmlString
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.ny.ny_helper_view import NYHelperView
from gui.Scaleform.daapi.view.meta.NYCollectionsMeta import NYCollectionsMeta
from gui.Scaleform.genConsts.NY_CONSTANTS import NY_CONSTANTS
from gui.Scaleform.locale.NY import NY
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from helpers import dependency
from items.new_year_types import NATIONAL_SETTINGS_IDS_BY_NAME, NATIONAL_SETTINGS, g_cache
from new_year.new_year_sounds import NYSoundEvents
from skeletons.new_year import INewYearUIManager
_DEF_DATA = {'backBtnDescrLabel': NY.COLLECTIONSGROUP_BACKBTN_TO_NYCOLLECTIONSGROUPS}

class NYCollections(NYHelperView, NYCollectionsMeta):
    _newYearUIManager = dependency.descriptor(INewYearUIManager)

    def __init__(self, ctx=None):
        self.__selectedSetting = None
        self.__navigation = dict.fromkeys(NATIONAL_SETTINGS, 0)
        self.__settingData = (0, 0, tuple())
        ctx = ctx or {}
        self.__updateSelectedSetting(ctx['settings'] if 'settings' in ctx else NY_CONSTANTS.NY_SETTINGS_TYPE_SOVIET)
        super(NYCollections, self).__init__()
        return

    def onWindowClose(self):
        self.__doClose()

    def onClose(self):
        NYSoundEvents.playSound(NYSoundEvents.ON_CLOSE_COLLECTION_GROUPS)
        self._switchToNYMain(previewAlias=VIEW_ALIAS.LOBBY_NY_COLLECTIONS)

    def onBackClick(self):
        self._switchToGroups(previewAlias=VIEW_ALIAS.LOBBY_NY_COLLECTIONS)

    def onChange(self, setting, level):
        if self.__selectedSetting != setting:
            self.__updateSelectedSetting(setting)
            self.__updateDataByLevel(self.__navigation[self.__selectedSetting] + 1)
        elif self.__navigation[self.__selectedSetting] != level:
            self.__navigation[self.__selectedSetting] = level
            self.__updateDataByLevel(self.__navigation[self.__selectedSetting] + 1)
            self._newYearUIManager.setSelectedCollectionLevels(self.__navigation)

    def _populate(self):
        super(NYCollections, self)._populate()
        levelSettings = self._newYearUIManager.getSelectedCollectionLevels()
        if levelSettings:
            self.__navigation = levelSettings
        else:
            for toyId in self._newYearController.receivedToysCollection:
                toy = g_cache.toys[toyId]
                self.__navigation[toy.setting] = max(toy.rank - 1, self.__navigation[toy.setting])

            self._newYearUIManager.setSelectedCollectionLevels(self.__navigation)
        data = _DEF_DATA
        data['selectedSettings'] = self.__selectedSetting
        data['selectedLevel'] = [ {'nation': nation,
         'selectedLevel': level} for nation, level in self.__navigation.iteritems() ]
        data['nationOrder'] = sorted(NATIONAL_SETTINGS, key=lambda s: self._newYearController.getSettingIndexInNationsOrder(s))
        self.as_setDataS(data)
        self._newYearController.onToyCollectionChanged += self.__onToyCollectionChanged
        self.__updateDataByLevel(self.__navigation[self.__selectedSetting] + 1)
        NYSoundEvents.setBoxSwitch(self.__selectedSetting)

    def _dispose(self):
        self._newYearController.onToyCollectionChanged -= self.__onToyCollectionChanged
        super(NYCollections, self)._dispose()

    def __updateSelectedSetting(self, setting):
        self.__selectedSetting = setting
        receivedCount = 0
        totalCount = 0
        alreadyReceived = self._newYearController.receivedToysCollection
        toys = self._newYearController.toysDescrs
        toysBySetting = []
        for toy in toys.values():
            if toy.setting == setting:
                totalCount += 1
                received = toy.id in alreadyReceived
                if received:
                    receivedCount += 1
                toysBySetting.append(toy)

        self.__settingData = (receivedCount, totalCount, toysBySetting)

    def __onToyCollectionChanged(self, _):
        self.__updateSelectedSetting(self.__selectedSetting)
        self.__updateDataByLevel(self.__navigation[self.__selectedSetting] + 1)

    def __updateDataByLevel(self, rank):
        outcome = []
        alreadyReceived = self._newYearController.receivedToysCollection
        receivedCount, totalCount, toysBySetting = self.__settingData
        bonuses = self._newYearController.getBonusesForSetting(NATIONAL_SETTINGS_IDS_BY_NAME[self.__selectedSetting])
        bonus = int(bonuses[0] * 100.0) if bonuses else 0
        for toy in toysBySetting:
            if toy.rank == rank:
                outcome.append({'id': toy.id,
                 'icon': toy.icon,
                 'isReceived': toy.id in alreadyReceived})

        progress = _ms(NY.COLLECTIONS_STATUS, value=text_styles.stats(str(receivedCount)), max=totalCount)
        bonusCount = makeHtmlString('html_templates:newYear/collectionBonus', 'big', {'bonus': bonus})
        levelData = {'progress': progress,
         'setting': self.__selectedSetting,
         'title': _ms(NY.COLLECTIONS_TITLE, setting=_ms(NY.collections_title(self.__selectedSetting))),
         'subTitle': NY.collections_level(rank),
         'toys': outcome,
         'bonusCount': bonusCount,
         'isCollected': totalCount == receivedCount}
        self.as_setLevelDataS(levelData)

    def __doClose(self):
        self.destroy()
