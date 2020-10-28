# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/EventControlPoint.py
import logging
import BigWorld
import AnimationSequence
from Math import Vector2
from Math import Matrix
import ResMgr
from debug_utils import LOG_WARNING, LOG_DEBUG
import SoundGroups
from collector_animator import CollectorAnimator
from effect_controller import EffectController
from helpers import dependency
from helpers import newFakeModel
from helpers.EffectsList import effectsFromSection, EffectsListPlayer
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ECP_INDEXES, ECP_SWITCHES, ECP_HUD_INDEXES, ECP_HUD_TOGGLES
_ANOTHERWORLD_EFFECT_NAME = 'EventControlPointAnotherWorldEffect'
_ORIGINALWORLD_EFFECT_NAME = 'EventControlPointOriginalWorldEffect'
_logger = logging.getLogger(__name__)

class _EventControlPointSettingsCache(object):

    def __init__(self, settings):
        self.initSettings(settings)

    def initSettings(self, settings):
        self.flagModel = settings.readString('flagModelName', '')
        self.radiusModel = settings.readString('radiusModel', '')
        self.flagAnim = settings.readString('flagAnim', '')
        self.attachedSoundEventName = settings.readString('wwsound', '')
        self.ssm = settings.readString('eventControlPointSSM', '')
        self.ssmModel = settings.readString('eventControlPointSSMModel', '')
        self.ssmBoolParam = settings.readString('eventControlPointSSMBoolParam', '')


ENVIRONMENT_EFFECTS_CONFIG_FILE = 'scripts/dynamic_objects.xml'
_g_eventControlPointSettings = None

class EventControlPoint(BigWorld.Entity):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _COLOR = 4294967295L
    _OVER_TERRAIN_HEIGHT = 0.5

    def __init__(self):
        global _g_eventControlPointSettings
        self.minimapSymbol = None
        if _g_eventControlPointSettings is None:
            settingsData = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE + '/eventControlPoint')
            _g_eventControlPointSettings = _EventControlPointSettingsCache(settingsData)
        self._g_eventControlPointSettings = None
        self.__terrainSelectedArea = None
        self.__animator = None
        self.__model = None
        self.__minimapID = None
        self.__anotherWorldEffect = None
        self.__ssm = None
        self.__ssmModel = None
        self.__fakemodel = None
        self.__arenaECPComponent = None
        self._collectorAnimator = None
        self._disappearEffect = None
        return

    def prerequisites(self):
        loader = AnimationSequence.Loader(_g_eventControlPointSettings.ssm, self.spaceID)
        loaderModel = AnimationSequence.Loader(_g_eventControlPointSettings.ssmModel, self.spaceID)
        rv = [_g_eventControlPointSettings.flagModel,
         _g_eventControlPointSettings.radiusModel,
         loader,
         loaderModel]
        mProv = Matrix()
        mProv.translation = self.position
        self.__eventControlPointSoundObject = SoundGroups.g_instance.WWgetSoundObject('eventControlPoint' + str(self), mProv)
        self.__eventControlPointSoundObject.play(_g_eventControlPointSettings.attachedSoundEventName)
        return rv

    def onEnterWorld(self, prereqs):
        self.__model = prereqs[_g_eventControlPointSettings.flagModel]
        if self.__ssm is None:
            self.__ssm = prereqs[_g_eventControlPointSettings.ssm]
            if self.__ssm:
                if self.__fakemodel is None:
                    self.__fakemodel = newFakeModel()
                    self.__fakemodel.position = self.position
                    BigWorld.player().addModel(self.__fakemodel)
                self.__ssm.bindTo(AnimationSequence.ModelWrapperContainer(self.__fakemodel, self.spaceID))
                self.__ssm.start()
        if self.__ssmModel is None:
            self.__ssmModel = prereqs[_g_eventControlPointSettings.ssmModel]
            if self.__ssmModel:
                if self.__fakemodel is None:
                    self.__fakemodel = newFakeModel()
                    self.__fakemodel.position = self.position
                    BigWorld.player().addModel(self.__fakemodel)
                self.__ssmModel.bindTo(AnimationSequence.ModelWrapperContainer(self.__fakemodel, self.spaceID))
                self.__ssmModel.start()
        currentState = self.__getArenaECPComponent().ecpStateByID(self.id)
        if currentState:
            self._restoreState(currentState)
        return

    def onChangeState(self, state, switch, value):
        if self.filterByPlayerID >= 0 and BigWorld.player().vehicle.id != self.filterByPlayerID:
            return
        methodName = '_' + ECP_INDEXES[state].name()
        if hasattr(self, methodName):
            getattr(self, methodName)(ECP_SWITCHES[switch] == ECP_SWITCHES.on, value)
        else:
            LOG_DEBUG('There is no attr with name ', methodName)

    def _light(self, switch, value):
        if self.__ssm:
            self.__ssm.setBoolParam(_g_eventControlPointSettings.ssmBoolParam, switch)
        else:
            if not self.__anotherWorldEffect:
                self.__anotherWorldEffect = _AnotherWorldEffectPlayer(self.position)
            effectName = _ANOTHERWORLD_EFFECT_NAME if switch else _ORIGINALWORLD_EFFECT_NAME
            self.__anotherWorldEffect.play(effectName)

    def _circle(self, switch, value):
        if self.__ssmModel and value:
            self.__ssmModel.setBoolParam(value, switch)
            return
        else:
            if switch:
                self.model = self.__model
                self.model.position = self.position
                if _g_eventControlPointSettings.flagAnim is not None:
                    try:
                        clipResource = self.model.deprecatedGetAnimationClipResource(_g_eventControlPointSettings.flagAnim)
                        if clipResource:
                            spaceID = BigWorld.player().spaceID
                            loader = AnimationSequence.Loader(clipResource, spaceID)
                            self.__animator = loader.loadSync()
                            self.__animator.bindTo(AnimationSequence.ModelWrapperContainer(self.model, spaceID))
                            self.__animator.start()
                    except Exception:
                        LOG_WARNING('Unable to start "%s" animation action for model "%s"' % (_g_eventControlPointSettings.flagAnim, _g_eventControlPointSettings.flagModel))

                self.__terrainSelectedArea = BigWorld.PyTerrainSelectedArea()
                self.__terrainSelectedArea.setup(_g_eventControlPointSettings.radiusModel, Vector2(self.radius * 2.0, self.radius * 2.0), self._OVER_TERRAIN_HEIGHT, self._COLOR)
                self.model.root.attach(self.__terrainSelectedArea)
            else:
                self.model = None
            return

    def _minimap(self, switch, value):
        setattr(self, 'minimapSymbol', value)
        self.__getArenaECPComponent().toggleHUDElement(self, ECP_HUD_INDEXES.minimap, ECP_HUD_TOGGLES[int(switch)])

    def _marker(self, switch, value):
        setattr(self, 'markerSymbol', value)
        self.__getArenaECPComponent().toggleHUDElement(self, ECP_HUD_INDEXES.marker, ECP_HUD_TOGGLES[int(switch)])

    def _soulCollector(self, switch, value):
        if switch:
            self._collectorAnimator = CollectorAnimator(self)
            self._collectorAnimator.start()
        else:
            if self._collectorAnimator:
                self._collectorAnimator.stop()
                self._collectorAnimator = None
            if self.__fakemodel is None:
                self.__fakemodel = newFakeModel()
                self.__fakemodel.position = self.position
                BigWorld.player().addModel(self.__fakemodel)
            self._disappearEffect = EffectController('volot_disappear')
            self._disappearEffect.playSequence(self.__fakemodel)
        return

    def _restoreState(self, state):
        for i, switch in enumerate(state[0]):
            if switch == ECP_SWITCHES.on:
                self.onChangeState(i, ECP_SWITCHES.on.index(), state[1][i])

    def onLeaveWorld(self):
        if self.__anotherWorldEffect:
            self.__anotherWorldEffect.cleanup()
        self.__eventControlPointSoundObject.stopAll()
        self.__eventControlPointSoundObject = None
        if self._collectorAnimator:
            self._collectorAnimator.stop()
            self._collectorAnimator = None
        if self._disappearEffect:
            self._disappearEffect.reset()
        self.__animator = None
        if self.__fakemodel and self.__fakemodel.inWorld:
            BigWorld.player().delModel(self.__fakemodel)
            self.__fakemodel = None
        self.__ssm = None
        self.__ssmModel = None
        return

    def isActiveForPlayerTeam(self):
        return self.team == 0 or self.team == BigWorld.player().team

    def __getArenaECPComponent(self):
        if self.__arenaECPComponent:
            return self.__arenaECPComponent
        cs = BigWorld.player().arena.componentSystem
        self.__arenaECPComponent = getattr(cs, 'ecp')
        return self.__arenaECPComponent


class _AnotherWorldEffectPlayer(object):

    def __init__(self, position):
        self.__effectsPlayer = None
        self.__effect = None
        self.__model = newFakeModel()
        self.__model.position = position
        BigWorld.player().addModel(self.__model)
        return

    def play(self, effectName):
        effectsSection = ResMgr.openSection(ENVIRONMENT_EFFECTS_CONFIG_FILE + '/' + effectName)
        self.__effect = effectsFromSection(effectsSection)
        self.__play()

    def __play(self):
        if self.__effectsPlayer:
            self.__effectsPlayer.stop()
        self.__effectsPlayer = EffectsListPlayer(self.__effect.effectsList, self.__effect.keyPoints, debugParent=self)
        self.__effectsPlayer.play(self.__model, None, self.__onFinished)
        return

    def __onFinished(self):
        self.__play()

    def cleanup(self):
        if self.__effectsPlayer:
            self.__effectsPlayer.stop()
            self.__effectsPlayer = None
        if self.__model and self.__model.inWorld is True:
            BigWorld.player().delModel(self.__model)
            self.__model = None
        return
