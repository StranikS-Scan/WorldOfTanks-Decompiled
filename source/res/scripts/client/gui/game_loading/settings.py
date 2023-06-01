# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/settings.py
import typing
from gui.game_loading import loggers
from gui.game_loading.resources.cdn.consts import SequenceOrders
from gui.game_loading.resources.cdn.models import LocalSlideModel, LocalSequenceModel, CdnCacheDefaultsModel
from gui.game_loading.resources.consts import ImageVfxs, MilestonesTypes, LoadingTypes, Milestones, InfoStyles
from gui.game_loading.resources.models import StatusTextModel, LogoModel
from gui.game_loading.state_machine.models import ImageViewSettingsModel
from gui.game_loading.state_machine.const import DEFAULT_SLIDE_DURATION, DEFAULT_LOGIN_NEXT_SLIDE_DURATION, DEFAULT_LOGIN_STATUS_MIN_SHOW_TIME_SEC, DEFAULT_SLIDE_TRANSITION_DURATION, ContentState
from gui.game_loading.state_machine.models import LoadingMilestoneModel, ProgressSettingsModel
from helpers import getClientLanguage
from helpers.i18n import makeString
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from ResMgr import DataSection
_logger = loggers.getLoaderSettingsLogger()
DEFAULT_TAG = 'default'

class GameLoadingSettings(object):
    __slots__ = ('_settings', '_ageRatingPath', '_lang')

    def __init__(self, settings):
        self._settings = settings
        self._ageRatingPath = None
        self._lang = getClientLanguage()
        return

    def getLogos(self):
        logoListSection = self._settings['logoList']
        if logoListSection is None:
            return []
        else:
            logos = []
            infoStyleValues = InfoStyles.values()
            for logoData in logoListSection.values():
                info = ''
                style = InfoStyles.DEFAULT
                infoDatas = logoData['info']
                if infoDatas is not None:
                    infoData = None
                    if infoDatas.has_key(self._lang):
                        infoData = infoDatas[self._lang]
                    elif infoDatas.has_key(DEFAULT_TAG):
                        infoData = infoDatas[DEFAULT_TAG]
                    if infoData is not None:
                        info = infoData.readString('text')
                        styleValue = infoData.readString('style')
                        if styleValue:
                            if styleValue not in infoStyleValues:
                                _logger.warning('Not supported info style: %s not in %s.', styleValue, infoStyleValues)
                            else:
                                style = InfoStyles(styleValue)
                logos.append(LogoModel(logoType=logoData.readInt('type', 0), minShowTimeSec=logoData.readFloat('duration', 0), showCopyright=logoData.readBool('showCopyright', False), showVersion=logoData.readBool('showVersion', False), transition=int(logoData.readFloat('transitionDuration', 0) * 1000), info=makeString(info) or '', infoStyle=style))

            return logos

    def getLoginNextSlideDuration(self):
        return self._settings.readFloat('loginNextSlideDuration', DEFAULT_LOGIN_NEXT_SLIDE_DURATION)

    def getCdnCacheDefaults(self):
        slideDuration = self._settings.readFloat('slideDuration', DEFAULT_SLIDE_DURATION)
        slideTransitionDuration = int(self._settings.readFloat('slideTransitionDuration', DEFAULT_SLIDE_TRANSITION_DURATION) * 1000)
        defaultSlideListSection = self._settings['defaultSlideList']
        defaultSlideList = [] if defaultSlideListSection is None else defaultSlideListSection.values()
        slides, vfxValues = [], ImageVfxs.values()
        for slideSection in defaultSlideList:
            image = slideSection.readString('image')
            if not image:
                _logger.error('Empty image section, slide will be skipped.')
                continue
            vfx = None
            vfxValue = slideSection.readString('vfx') or None
            if vfxValue is not None:
                if vfxValue not in vfxValues:
                    _logger.warning('Not supported vfx value: %s not in %s.', vfxValue, vfxValues)
                    vfx = None
                else:
                    vfx = ImageVfxs(vfxValue)
            slide = LocalSlideModel(imageRelativePath=image, localizationText=makeString(slideSection.readString('title') or ''), descriptionText=makeString(slideSection.readString('description') or ''), vfx=vfx, minShowTimeSec=slideDuration, transition=slideTransitionDuration)
            slides.append(slide)

        if not slides:
            _logger.error('Default sequence id empty.')
        sequence = LocalSequenceModel(name='__static__', order=SequenceOrders.RANDOM, slides=slides)
        return CdnCacheDefaultsModel(sequence=sequence, minShowTimeSec=slideDuration, transition=slideTransitionDuration)

    def getStatusTexts(self):
        statusTextDuration = self._settings.readFloat('statusTextDuration', DEFAULT_SLIDE_DURATION)
        statusTextListSection = self._settings['statusTextList']
        if statusTextListSection is None:
            return []
        else:
            return [ StatusTextModel(text=makeString(text.asString), minShowTimeSec=statusTextDuration) for text in statusTextListSection.values() ]

    def getProgressSettingsByType(self, loadingType):
        loadingTypeSection = self._getLoadingTypeSection(loadingType)
        if loadingTypeSection is None:
            raise SoftException('Wrong progress settings.')
        settingsSection = loadingTypeSection['settings']
        if settingsSection is None:
            raise SoftException('No "settings" section for progress.')
        return ProgressSettingsModel(startPercent=settingsSection.readInt('startPercent', 0), limitPercent=settingsSection.readInt('limitPercent', 100), ticksInProgress=settingsSection.readInt('ticksInProgress', 1000), minTickTimeSec=settingsSection.readFloat('minTickTimeSec', 0))

    def getProgressMilestones(self, loadingType):
        loadingTypeSection = self._getLoadingTypeSection(loadingType)
        if loadingTypeSection is None:
            raise SoftException('Wrong progress settings.')
        milestoneSection = loadingTypeSection['milestones']
        if milestoneSection is None:
            return {}
        else:
            milestonesForTypes = {}
            for rawMilestonesType, rawMilestones in milestoneSection.items():
                milestonesType = rawMilestonesType
                milestonesTypes = MilestonesTypes.values()
                if milestonesType not in milestonesTypes:
                    _logger.error('Unknown milestonesType: %s, Available: %s', milestonesType, milestonesTypes)
                    continue
                milestonesForType = milestonesForTypes.setdefault(MilestonesTypes(milestonesType), {})
                for milestoneSection in rawMilestones.values():
                    milestoneName = milestoneSection.readString('name')
                    milestones = Milestones.values()
                    if milestoneName not in milestones:
                        _logger.error('Unknown milestone: %s, Available: %s', milestoneName, milestones)
                        continue
                    status = StatusTextModel(text=makeString(milestoneSection.readString('text')), minShowTimeSec=DEFAULT_LOGIN_STATUS_MIN_SHOW_TIME_SEC)
                    milestoneName = Milestones(milestoneName)
                    milestonesForType[milestoneName] = LoadingMilestoneModel(name=milestoneName, percent=milestoneSection.readInt('percent'), forceApply=milestoneSection.readBool('forceApply'), status=status)

            defaultMilestones = milestonesForTypes.get(MilestonesTypes.CONNECTION)
            if defaultMilestones is None:
                raise SoftException('Default milestones type should be in settings.')
            if not defaultMilestones:
                raise SoftException('At list one milestone should be in settings.')
            return milestonesForTypes

    def getClientLoadingStateViewSettings(self):
        return self._getStateViewSettings('clientLoading')

    def getLoginStateViewSettings(self):
        return self._getStateViewSettings('login')

    def getPlayerLoadingStateViewSettings(self):
        return self._getStateViewSettings('playerLoading')

    def _getStateViewSettings(self, state):
        statesSection = self._settings['states']
        if statesSection is None:
            _logger.warning('No states section can be found')
            return ImageViewSettingsModel()
        else:
            stateSection = statesSection[state]
            showVfx = False
            contentState = ContentState.INVISIBLE
            ageRatingPath = self._getAgeRatingPath()
            info = ''
            if stateSection is not None:
                showVfx = stateSection.readBool('showVfx', False)
                contentStateValue = stateSection.readInt('contentState', ContentState.INVISIBLE.value)
                info = makeString(stateSection.readString('info') or '')
                if contentStateValue not in ContentState.values():
                    _logger.warning('Not supported contentState value for %s state: %s not in %s.', state, contentStateValue, ContentState.values())
                else:
                    contentState = ContentState(contentStateValue)
            else:
                _logger.warning('No section can be found for %s view state', state)
            return ImageViewSettingsModel(showVfx=showVfx, contentState=contentState, ageRatingPath=ageRatingPath, info=info)

    def _getAgeRatingPath(self):
        if self._ageRatingPath is None:
            self._ageRatingPath = ''
            ageRatingPathData = self._settings['ageRatingPath']
            if ageRatingPathData is not None:
                if ageRatingPathData.has_key(self._lang):
                    self._ageRatingPath = ageRatingPathData.readString(self._lang)
                elif ageRatingPathData.has_key(DEFAULT_TAG):
                    self._ageRatingPath = ageRatingPathData.readString(DEFAULT_TAG)
        return self._ageRatingPath

    def _getLoadingTypeSection(self, loadingType):
        progressSettingsSection = self._settings['progressSettings']
        if progressSettingsSection is None:
            _logger.error('No progressSettings section.')
            return
        elif loadingType not in LoadingTypes.values():
            _logger.error('Wrong loading type %s', loadingType)
            return
        loadingTypeSection = progressSettingsSection[loadingType]
        if loadingTypeSection is None:
            _logger.error('No loading type %s section.', loadingTypeSection)
            return
        else:
            return loadingTypeSection
