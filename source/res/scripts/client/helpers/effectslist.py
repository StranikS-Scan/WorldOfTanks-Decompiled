# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/EffectsList.py
import logging
import random
import string
from collections import namedtuple
from functools import partial
import AnimationSequence
import BigWorld
import Math
import DecalMap
import SoundGroups
import helpers
import material_kinds
from PixieBG import PixieBG
from ReplayEvents import g_replayEvents
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException
from vehicle_systems.tankStructure import TankSoundObjectsIndexes
_logger = logging.getLogger(__name__)
COLOR_WHITE = 4294967295L
_ALLOW_DYNAMIC_LIGHTS = True
KeyPoint = namedtuple('KeyPoint', ('name', 'time'))
EffectsTimeLine = namedtuple('EffectsTimeLine', ('keyPoints', 'effectsList'))
EffectsTimeLinePrereqs = namedtuple('EffectsTimeLinePrereqs', ('keyPoints', 'effectsList', 'prereqs'))

class SpecialKeyPointNames(object):
    START = 'start'
    END = 'end'
    STATIC = 'static'


__START_KEY_POINT = KeyPoint(SpecialKeyPointNames.START, 0.0)
SoundStartParam = namedtuple('SoundStartParam', ('name', 'value'))

def _isPyModel(model):
    return model is not None and model.__class__.__name__ == 'Model'


def reload():
    import __builtin__
    from sys import modules
    __builtin__.reload(modules[reload.__module__])


class EffectsList(object):
    __slots__ = ('__effectDescList', 'relatedEffects')

    def __init__(self, section):
        super(EffectsList, self).__init__()
        self.__effectDescList = []
        self.relatedEffects = {}
        for s in section.items():
            effDesc = _createEffectDesc(s[0], s[1])
            if effDesc is not None:
                self.__effectDescList.append(effDesc)

        return

    def prerequisites(self):
        out = []
        for effDesc in self.__effectDescList:
            out += effDesc.prerequisites()

        for relatedEffect in self.relatedEffects.itervalues():
            out += relatedEffect.effectsList.prerequisites()

        return out

    def attachTo(self, model, data, key, **args):
        if not data.has_key('_EffectsList_effects'):
            data['_EffectsList_effects'] = []
        for eff in self.__effectDescList:
            if eff.startKey == key:
                if args.has_key('keyPoints'):
                    startTime = endTime = 0
                    for keyPoint in args['keyPoints']:
                        if keyPoint.name == eff.startKey:
                            startTime = keyPoint.time
                        endTime = keyPoint.time
                        if keyPoint.name == eff.endKey:
                            break

                    eff.duration = endTime - startTime
                eff.create(model, data['_EffectsList_effects'], args)

    def reattachTo(self, model, data):
        effects = data.get('_EffectsList_effects', ())
        for elem in effects:
            elem['typeDesc'].reattach(elem, model)

    def detachFrom(self, data, key, reason=1):
        effects = data['_EffectsList_effects']
        for elem in effects[:]:
            if elem['typeDesc'].endKey == key:
                if elem['typeDesc'].delete(elem, reason):
                    effects.remove(elem)

    def detachAllFrom(self, data, keepPosteffects=False):
        effects = data.get('_EffectsList_effects', None)
        if effects is None:
            return
        elif keepPosteffects:
            for elem in effects[:]:
                if elem['typeDesc'].delete(elem, 2):
                    effects.remove(elem)

            return
        else:
            for elem in effects[:]:
                elem['typeDesc'].delete(elem, 0)
                effects.remove(elem)

            del data['_EffectsList_effects']
            return


class EffectsListPlayer(object):
    effectsList = property(lambda self: self.__effectsList)
    isPlaying = property(lambda self: self.__isStarted)
    activeEffects = set()
    clearInProgress = False

    @staticmethod
    def clear():
        import BattleReplay
        replayCtrl = BattleReplay.g_replayCtrl
        if not replayCtrl.isPlaying:
            return
        else:
            warpDelta = replayCtrl.warpTime - replayCtrl.currentTime
            EffectsListPlayer.clearInProgress = True
            for effect in EffectsListPlayer.activeEffects:
                if effect.__waitForKeyOff and warpDelta > 0.0:
                    continue
                effectCurTime = 0
                if effect.__curKeyPoint is not None:
                    effectCurTime = effect.__curKeyPoint.time
                else:
                    effectCurTime = 0.0
                if warpDelta <= 0.0 or effect.__keyPoints[-1].time - effectCurTime < warpDelta:
                    if effect.__callbackFunc is not None:
                        effect.__callbackFunc()
                    effect.stop()

            EffectsListPlayer.clearInProgress = False
            return

    def __init__(self, effectsList, keyPoints, **args):
        self.__keyPoints = keyPoints
        self.__effectsList = effectsList
        self.__args = args
        self.__args['keyPoints'] = self.__keyPoints
        self.__curKeyPoint = None
        self.__callbackFunc = None
        self.__callbackID = None
        self.__keyPointIdx = -1
        self.__isStarted = False
        self.__waitForKeyOff = False
        self.__data = dict()
        return

    def play(self, model, startKeyPoint=None, callbackFunc=None, waitForKeyOff=False):
        needPlay, newKey = self.__isNeedToPlay(waitForKeyOff)
        if not needPlay:
            return
        else:
            if newKey is not None:
                startKeyPoint = newKey
            if self.__isStarted:
                _logger.error('player already started. To restart it you must before call stop().')
                return
            import BattleReplay
            if BattleReplay.g_replayCtrl.isPlaying:
                EffectsListPlayer.activeEffects.add(self)
            self.__isStarted = True
            self.__callbackID = None
            self.__model = model
            self.__callbackFunc = callbackFunc
            self.__waitForKeyOff = waitForKeyOff
            self.__keyPointIdx = self.__getKeyPointIdx(startKeyPoint) if startKeyPoint is not None else 0
            self.__keyPointIdx -= 1
            self.__effectsList.attachTo(self.__model, self.__data, None, **self.__args)
            firstTimePoint = self.__keyPoints[self.__keyPointIdx + 1].time
            if self.__keyPointIdx < 0 and startKeyPoint is None and firstTimePoint > 0.0:
                self.__callbackID = BigWorld.callback(firstTimePoint, self.__playKeyPoint)
            else:
                self.__playKeyPoint(waitForKeyOff)
            return

    def keyOff(self, waitForNextKeyOff=False):
        if self.__isStarted:
            self.__playKeyPoint(waitForNextKeyOff)

    def reattachTo(self, model):
        self.__effectsList.reattachTo(model, self.__data)
        self.__model = model

    def __isNeedToPlay(self, waitForKeyOff):
        if helpers.gEffectsDisabled():
            return (False, None)
        import BattleReplay
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            entity_id = -1
            if 'entity_id' in self.__args:
                entity_id = self.__args['entity_id']
            need_play = True
            if entity_id > -1:
                need_play = replayCtrl.isNeedToPlay(entity_id)
            if need_play:
                if replayCtrl.isTimeWarpInProgress:
                    if not waitForKeyOff:
                        warpDelta = replayCtrl.warpTime - replayCtrl.currentTime
                        if self.__keyPoints[-1].time / 2 < warpDelta:
                            return (False, None)
                else:
                    return (True, None)
            for key in self.__keyPoints:
                if key.name == SpecialKeyPointNames.STATIC:
                    return (True, SpecialKeyPointNames.STATIC)

            return (False, None)
        else:
            return (True, None)

    def stop(self, keepPosteffects=False, forceCallback=False):
        if self.__isStarted:
            if forceCallback and self.__callbackFunc is not None:
                self.__callbackFunc()
        if g_replayEvents.isPlaying and not EffectsListPlayer.clearInProgress:
            EffectsListPlayer.activeEffects.discard(self)
        self.__isStarted = False
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        if self.__effectsList is not None:
            self.__effectsList.detachAllFrom(self.__data, keepPosteffects)
        self.__model = None
        self.__data = dict()
        self.__curKeyPoint = None
        self.__callbackFunc = None
        return

    def __getKeyPointIdx(self, name):
        for i, keyPoint in enumerate(self.__keyPoints):
            if keyPoint.name == name:
                return i

    def __playKeyPoint(self, waitForKeyOff=False):
        self.__callbackID = None
        try:
            self.__keyPointIdx += 1
            if self.__keyPointIdx + 1 >= len(self.__keyPoints):
                if self.__callbackFunc:
                    self.__callbackFunc()
                self.stop()
                return
            self.__curKeyPoint = self.__keyPoints[self.__keyPointIdx]
            nextKeyPoint = self.__keyPoints[self.__keyPointIdx + 1]
            self.__effectsList.detachFrom(self.__data, self.__curKeyPoint.name)
            self.__effectsList.attachTo(self.__model, self.__data, self.__curKeyPoint.name, **self.__args)
            deltaTime = nextKeyPoint.time - self.__curKeyPoint.time
            if deltaTime == 0.0:
                self.__playKeyPoint(waitForKeyOff)
            elif not waitForKeyOff:
                self.__callbackID = BigWorld.callback(deltaTime, self.__playKeyPoint)
        except Exception:
            _logger.exception('Play key point exception')

        return


class _EffectDesc(object):
    __slots__ = ('startKey', 'endKey', '_nodeName', 'duration')

    def __init__(self, dataSection):
        self.startKey = intern(dataSection.readString('startKey'))
        if not self.startKey:
            _raiseWrongConfig('startKey', self.TYPE)
        self.endKey = dataSection.readString('endKey')
        nodeName = dataSection.readString('position')
        if nodeName:
            self._nodeName = [ intern(name) for name in string.split(nodeName, '/') ]
        else:
            self._nodeName = []

    def prerequisites(self):
        return []

    def reattach(self, elem, model):
        pass

    def create(self, model, effects, args):
        pass

    def delete(self, elem, reason):
        return True


class _PixieEffectDesc(_EffectDesc):
    __slots__ = ('_files', '_havokFiles', '_force', '_surfaceMatKinds', '_orientByClosestSurfaceNormal', '_alwaysUpdate', '__prototypePixies')
    TYPE = '_PixieEffectDesc'

    def __init__(self, dataSection):
        super(_PixieEffectDesc, self).__init__(dataSection)
        self._files = [ f for f in dataSection.readStrings('file') if f ]
        if not self._files:
            _raiseWrongConfig('file', self.TYPE)
        self._force = 0
        key = 'force'
        if dataSection.has_key(key):
            self._force = dataSection.readInt(key, 0)
            if self._force < 0:
                _raiseWrongConfig(key, self.TYPE)
        if dataSection.has_key('surfaceMatKind'):
            matKindNames = dataSection.readString('surfaceMatKind', '').split(' ')
            self._surfaceMatKinds = []
            for matKindName in matKindNames:
                self._surfaceMatKinds += material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES.get(matKindName, [])

        else:
            self._surfaceMatKinds = None
        self._orientByClosestSurfaceNormal = dataSection.readBool('orientBySurfaceNormal', False)
        self._alwaysUpdate = dataSection.readBool('alwaysUpdateModel', False)
        self.__prototypePixies = {}
        return

    def prerequisites(self):
        return self._files

    def reattach(self, elem, model):
        nodePos = self._nodeName
        elem['model'] = model
        if elem['newPos'] is not None:
            nodePos = string.split(elem['newPos'][0], '/') if elem['newPos'][0] else []
        if elem['pixie'].pixie is not None and elem['node'] is not None:
            elem['node'].detach(elem['pixie'].pixie)
            elem['node'] = _findTargetNode(model, nodePos, elem['newPos'][1] if elem['newPos'] else None, self._orientByClosestSurfaceNormal, elem['surfaceNormal'])
            elem['node'].attach(elem['pixie'].pixie)
        else:
            elem['node'] = _findTargetNode(model, nodePos, None, self._orientByClosestSurfaceNormal, elem['surfaceNormal'])
        return

    def create(self, model, effects, args):
        elem = {}
        node = args.get('node', None)
        if node is None:
            elem['newPos'] = args.get('position', None)
            nodePos = self._nodeName
            if elem['newPos'] is not None:
                nodePos = string.split(elem['newPos'][0], '/') if elem['newPos'][0] else []
            scale = args.get('scale')
            if scale is not None:
                elem['scale'] = scale
            elem['surfaceNormal'] = args.get('surfaceNormal', None)
            surfaceMatKind = args.get('surfaceMatKind', None)
            if surfaceMatKind is not None and self._surfaceMatKinds is not None:
                if surfaceMatKind not in self._surfaceMatKinds:
                    return
            elem['node'] = _findTargetNode(model, nodePos, elem['newPos'][1] if elem['newPos'] else None, self._orientByClosestSurfaceNormal, elem['surfaceNormal'])
        else:
            elem['node'] = node
        elem['model'] = model
        elem['typeDesc'] = self
        elem['pixie'] = None
        eFile = random.choice(self._files)
        prototypePixie = self.__prototypePixies.get(eFile)
        modifiers = {}
        if args.get('havokSpawnedDestructibles', False):
            modifiers['doHavokDebrisSpawned'] = True
        tintColor = args.get('tintColor', COLOR_WHITE)
        if tintColor != COLOR_WHITE:
            modifiers['tintColor'] = tintColor
        if not modifiers:
            modifiers = None
        if prototypePixie is not None:
            elem['pixie'] = PixieBG(eFile, None, prototypePixie.clone(), None, modifiers)
            self._callbackCreate(elem)
        else:
            elem['file'] = eFile
            elem['pixie'] = PixieBG(eFile, self._callbackAfterLoading, None, elem, modifiers)
        effects.append(elem)
        return

    def delete(self, elem, reason):
        pixieDef = elem.get('pixie', None)
        if pixieDef is not None:
            if pixieDef.pixie is not None:
                elem['node'].detach(elem['pixie'].pixie)
            pixieDef.destroy()
        elem['pixie'] = None
        elem['node'] = None
        return True

    def _callbackAfterLoading(self, pixieBG, elem):
        if elem is not None:
            self.__prototypePixies[elem['file']] = pixieBG.pixie.clone()
            self._callbackCreate(elem)
        return

    def _callbackCreate(self, elem):
        scale = elem.get('scale')
        pixie = elem['pixie']
        node = elem['node']
        if pixie is not None and node is not None:
            if scale is not None:
                pixie.scale(scale)
            pixie.force(self._force)
            node.attach(pixie.pixie)
        return


class _AnimationEffectDesc(_EffectDesc):
    __slots__ = ('_name',)
    TYPE = '_AnimationEffectDesc'

    def __init__(self, dataSection):
        super(_AnimationEffectDesc, self).__init__(dataSection)
        self._name = dataSection.readString('name')
        if not self._name:
            _raiseWrongConfig('name', self.TYPE)

    def create(self, model, effects, args):
        targetModel = _findTargetModel(model, self._nodeName)
        animator = None
        if _isPyModel(targetModel):
            clipResource = targetModel.deprecatedGetAnimationClipResource(self._name)
            spaceID = BigWorld.player().spaceID
            loader = AnimationSequence.Loader(clipResource, spaceID)
            animator = loader.loadSync()
            animator.bindTo(AnimationSequence.ModelWrapperContainer(model, spaceID))
            animator.start()
        else:
            SoftException('EffectsList trying to play old animation <%s> on compoud model <%s>.' % (self._name, self.TYPE))
        effects.append({'typeDesc': self,
         'animator': animator})
        return

    def delete(self, elem, reason):
        if elem['animator'] is None:
            return True
        elif reason == 2:
            if self.endKey:
                elem['animator'].stop()
                return True
            return False
        else:
            elem['animator'].stop()
            return True
            return


class _VisibilityEffectDesc(_EffectDesc):
    __slots__ = ('_hasInitial', '_initial')
    TYPE = '_VisibilityEffectDesc'

    def __init__(self, dataSection):
        super(_VisibilityEffectDesc, self).__init__(dataSection)
        self._hasInitial = False
        self._initial = False
        key = 'initial'
        if dataSection.has_key(key):
            self._initial = dataSection.readBool(key, False)
            self._hasInitial = True

    def create(self, model, effects, args):
        targetModel = _findTargetModel(model, self._nodeName)
        if self._hasInitial:
            targetModel.visible = self._initial
        else:
            targetModel.visible = not targetModel.visible
        effects.append({'typeDesc': self,
         'model': targetModel})

    def delete(self, elem, reason):
        if self._hasInitial:
            elem['model'].visible = not self._initial
        else:
            elem['model'].visible = not elem['model'].visible
        return True


class _ModelEffectDesc(_EffectDesc):
    __slots__ = ('_modelName', '_animation')
    TYPE = '_ModelEffectDesc'

    def __init__(self, dataSection):
        super(_ModelEffectDesc, self).__init__(dataSection)
        self._modelName = dataSection.readString('name')
        if not self._modelName:
            _raiseWrongConfig('name', self.TYPE)
        self._animation = None
        key = 'animation'
        if dataSection.has_key(key):
            self._animation = dataSection.readString(key)
        return

    def prerequisites(self):
        return [self._modelName]

    def reattach(self, elem, model):
        elem['node'].detach(elem['attachment'])
        nodeName = self._nodeName
        if elem['newPos'] is not None:
            nodeName = string.split(elem['newPos'][0], '/') if elem['newPos'][0] else []
        targetNode = _findTargetNode(model, nodeName, elem['newPos'][1] if elem['newPos'] else None)
        targetNode.attach(model)
        return

    def create(self, model, effects, args):
        currentModel = BigWorld.Model(self._modelName)
        newPos = args.get('position', None)
        nodeName = self._nodeName
        if newPos is not None:
            nodeName = string.split(newPos[0], '/') if newPos[0] else []
        targetNode = _findTargetNode(model, nodeName, newPos[1] if newPos else None)
        targetNode.attach(currentModel)
        animator = None
        if self._animation:
            clipResource = model.deprecatedGetAnimationClipResource(self._animation)
            spaceID = BigWorld.player().spaceID
            loader = AnimationSequence.Loader(clipResource, spaceID)
            animator = loader.loadSync()
            animator.bindTo(AnimationSequence.ModelWrapperContainer(model, spaceID))
            animator.start()
        elem = {'typeDesc': self,
         'model': model,
         'animator': animator,
         'attachment': currentModel,
         'newPos': newPos,
         'node': targetNode}
        effects.append(elem)
        return currentModel

    def delete(self, elem, reason):
        elem['node'].detach(elem['attachment'])
        return True


class _BaseSoundEvent(_EffectDesc):
    __slots__ = ('_soundName', '_parameters')

    def __init__(self, dataSection):
        super(_BaseSoundEvent, self).__init__(dataSection)
        self._parameters = None
        return

    def reattach(self, elem, model):
        sound = elem.get('sound')
        if sound is not None:
            elem['node'] = node = _findTargetNodeSafe(model, self._nodeName)
            sound.matrixProvider = node.actualNode
        else:
            elem['node'] = None
        return

    def delete(self, elem, reason):
        soundObject = elem.get('sound', None)
        if soundObject is not None:
            if reason != 0:
                soundObject.stopAll()
            elem['sound'] = None
        if elem.has_key('node'):
            elem['node'] = None
        return True

    def prerequisites(self):
        return []

    def _isPlayer(self, args):
        entityID = None
        if args.has_key('entity'):
            entityID = args['entity'].id
            isPlayerVehicle = BigWorld.player().playerVehicleID == entityID
        else:
            isPlayerVehicle = args.get('isPlayerVehicle', False)
        return (isPlayerVehicle, entityID)

    def _getName(self, args):
        isPlayer, pID = self._isPlayer(args)
        return (self._soundName[0 if isPlayer else 1], pID)

    def _register(self, effects, node, sound):
        elem = {'typeDesc': self}
        elem['node'] = node
        elem['sound'] = sound
        effects.append(elem)


class _ShotSoundEffectDesc(_BaseSoundEvent):
    __slots__ = ('_soundName',)
    TYPE = '_ShotSoundEffectDesc'

    def __init__(self, dataSection):
        super(_ShotSoundEffectDesc, self).__init__(dataSection)
        self._soundName = ((dataSection.readString('wwsoundPC', ''),), (dataSection.readString('wwsoundNPC', ''),))

    def create(self, model, effects, args):
        vehicle = args.get('entity', None)
        if vehicle is not None and vehicle.isAlive() and vehicle.isStarted:
            soundObject = vehicle.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.GUN)
            if soundObject is not None:
                isPlayer, _ = self._isPlayer(args)
                soundName = self._soundName[0 if isPlayer else 1]
                distance = (BigWorld.camera().position - vehicle.position).length
                for sndName in soundName:
                    soundObject.play(sndName)

                soundObject.setRTPC('RTPC_ext_control_reflections_priority', distance)
        return


class _NodeSoundEffectDesc(_BaseSoundEvent):
    TYPE = '_NodeSoundEffectDesc'
    effectUniqId = 0
    __slots__ = ('_soundName', 'effectUniqId')

    def __init__(self, dataSection):
        super(_NodeSoundEffectDesc, self).__init__(dataSection)
        self._soundName = ((dataSection.readString('wwsoundPC', ''),), (dataSection.readString('wwsoundNPC', ''),))

    @classmethod
    def nextUniqueID(cls):
        uniqueID = cls.effectUniqId
        cls.effectUniqId += 1
        return uniqueID

    def create(self, model, effects, args):
        soundName, _ = self._getName(args)
        if len(soundName) < 1:
            return
        else:
            isPresent = True
            vehicle = args.get('entity', None)
            if vehicle is not None:
                isPresent = vehicle.isAlive() and vehicle.isStarted
            if isPresent:
                nodeDesc = args.get('position', None)
                nodeName = self._nodeName
                nodeLocalPos = None
                if nodeDesc is not None:
                    nodeName = string.split(nodeDesc[0], '/') if nodeDesc[0] else []
                    nodeLocalPos = nodeDesc[1]
                node = _findTargetNode(model, nodeName, nodeLocalPos)
                hitPoint = args.get('hitPoint', None)
                if hitPoint is None:
                    if nodeLocalPos is not None:
                        local = nodeLocalPos.translation
                    else:
                        local = (0.0, 0.0, 0.0)
                else:
                    local = hitPoint - node.actualNode.position
                objectName = soundName[0] + str(self.nextUniqueID())
                soundObject = SoundGroups.g_instance.WWgetSoundObject(objectName, node.actualNode, local)
                if soundObject is not None:
                    damageFactor = args.get('damageFactor', None)
                    if damageFactor is not None:
                        damage_size = 'SWITCH_ext_damage_size_medium'
                        factor = args.get('damageFactor', 0.0)
                        if factor < 4335.0 / 100.0:
                            damage_size = 'SWITCH_ext_damage_size_small'
                        elif factor > 8925.0 / 100.0:
                            damage_size = 'SWITCH_ext_damage_size_large'
                        _logger.debug('Sound Name = %s Damage Size = %s', soundName[0], damage_size)
                        soundObject.setSwitch('SWITCH_ext_damage_size', damage_size)
                    startParams = args.get('soundParams', ())
                    for soundStartParam in startParams:
                        soundObject.setRTPC(soundStartParam.name, soundStartParam.value)

                    if self._parameters is not None:
                        for soundStartParam in self._parameters:
                            soundObject.setRTPC(soundStartParam.name, soundStartParam.value)

                    for sndName in soundName:
                        if sndName:
                            soundObject.play(sndName)

                    self._register(effects, node, soundObject)
                    return soundObject
            else:
                return
            return


class _TracerSoundEffectDesc(_NodeSoundEffectDesc):
    __slots__ = ('_parameters',)
    TYPE = '_TracerSoundEffectDesc'
    shellTypesMap = {'AP': 0,
     'HE': 1,
     'HC': 2,
     'APCR': 3}

    def __init__(self, dataSection):
        super(_TracerSoundEffectDesc, self).__init__(dataSection)
        shellType = dataSection.readString('type', '').split()[0]
        shellType = _TracerSoundEffectDesc.shellTypesMap.get(shellType, 0)
        self._parameters = [SoundStartParam('psb_shell_type', shellType)]

    def _getName(self, args):
        isPlayer, id = self._isPlayer(args)
        return (self._soundName[0 if isPlayer else 1], id)

    def delete(self, elem, reason):
        if reason != 0:
            soundObject = elem.get('sound', None)
            if soundObject is not None:
                soundObject.play('psb_npc_stop')
        super(_TracerSoundEffectDesc, self).delete(elem, 0)
        return

    def _isPlayer(self, args):
        attackerID = args.get('attackerID', None)
        avatar = BigWorld.player()
        return (attackerID == BigWorld.player().playerVehicleID, attackerID) if not avatar.isVehicleAlive and attackerID is not None else super(_TracerSoundEffectDesc, self)._isPlayer(args)


class _CollisionSoundEffectDesc(_NodeSoundEffectDesc):
    __slots__ = ('_soundName', '_parameters')
    TYPE = '_CollisionSoundEffectDesc'

    def __init__(self, dataSection):
        super(_CollisionSoundEffectDesc, self).__init__(dataSection)
        self._parameters = None
        pcSounds, npcSounds = dataSection.readString('wwsoundPC', ''), dataSection.readString('wwsoundNPC', '')
        if pcSounds == '' and npcSounds == '':
            pcSounds = npcSounds = dataSection.readString('wwsound', '')
        pcSounds = self.__parceNames(pcSounds)
        npcSounds = self.__parceNames(npcSounds)
        self._soundName = (pcSounds, npcSounds)
        return

    def __parceNames(self, events):
        if events == '':
            return None
        else:
            events = events.split(';')
            resultEvents = ([], [])
            lineNum = 0
            for eventLists in events:
                for evntName in eventLists.split(','):
                    resultEvents[lineNum].append(evntName.split()[0])

                lineNum += 1

            return resultEvents

    def _getName(self, args):
        isPlayer, pID = self._isPlayer(args)
        isTracks = args.get('isTracks', False)
        sounds = self._soundName[0 if isPlayer else 1]
        return (sounds[1 if isTracks else 0], pID) if sounds is not None else ('', pID)

    def create(self, model, effects, args):
        damageFactor = args.get('damageFactor', None)
        if damageFactor < 1.0:
            args['damageFactor'] = None
            damageFactor = None
        impulse = args.get('impulse', None)
        if impulse is not None:
            impulseParam = SoundStartParam('RTPC_ext_collision_impulse_object', impulse)
            soundParams = args.get('soundParams', [])
            soundParams.append(impulseParam)
            args['soundParams'] = soundParams
        object = _NodeSoundEffectDesc.create(self, model, effects, args)
        isPlayer, _ = self._isPlayer(args)
        if damageFactor is not None and object is not None and isPlayer:
            object.play('collision_static_object_damage')
        return


class _DestructionSoundEffectDesc(_BaseSoundEvent):
    TYPE = '_DestructionSoundEffectDesc'
    __slots__ = ('_soundName', '_parameters')
    _timeStamp = 0.0
    _effectCount = 0
    _DELTA_TIME_MAX = 1
    _MAX_EFFECT_COUNT = 10
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, dataSection):
        super(_DestructionSoundEffectDesc, self).__init__(dataSection)
        self._soundName = dataSection.readString('wwsound', '')
        self.__readParameters(dataSection)

    def create(self, model, list, args):
        soundName = self._soundName
        if soundName == '':
            return
        else:
            isEventBattle = self.guiSessionProvider.arenaVisitor.gui.isEventBattle()
            if isEventBattle:
                prevCallDelta = BigWorld.time() - _DestructionSoundEffectDesc._timeStamp
                _DestructionSoundEffectDesc._timeStamp = BigWorld.time()
                if prevCallDelta < _DestructionSoundEffectDesc._DELTA_TIME_MAX:
                    if _DestructionSoundEffectDesc._effectCount > _DestructionSoundEffectDesc._MAX_EFFECT_COUNT:
                        return
                    _DestructionSoundEffectDesc._effectCount += 1
                else:
                    _DestructionSoundEffectDesc._effectCount = 0
            node = _findTargetNodeSafe(model, self._nodeName)
            objectName = soundName
            sound = SoundGroups.g_instance.WWgetSoundObject(objectName, node.actualNode)
            if sound is None:
                return
            for soundStartParam in self._parameters:
                sound.setRTPC(soundStartParam.name, soundStartParam.value)

            sound.play(soundName)
            self._register(list, node, sound)
            return sound

    def __readParameters(self, dataSection):
        self._parameters = []
        section = dataSection['params']
        if section is None:
            return
        else:
            for param in section.items():
                name = 'RTPC_ext_objects_' + param[0].strip()
                value = param[1].asFloat
                if value > 0.0:
                    self._parameters.append(SoundStartParam(name, value))

            return


ImpactNames = namedtuple('ImpactNames', ('impactNPC_PC', 'impactPC_NPC', 'impactNPC_NPC', 'impactFNPC_PC'))

class _SoundEffectDesc(_EffectDesc):
    __slots__ = ('_soundName', '_soundNames', '_switch_impact_surface', '_switch_shell_type', '_dynamic', '_stopSyncVisual', '_impactNames')
    TYPE = '_SoundEffectDesc'
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, dataSection):
        super(_SoundEffectDesc, self).__init__(dataSection)
        self._soundName = None
        self._soundNames = None
        self._switch_impact_surface = None
        self._switch_shell_type = None
        self._stopSyncVisual = False
        if dataSection.has_key('wwsoundPC') and dataSection.has_key('wwsoundNPC'):
            self._soundNames = (intern(dataSection.readString('wwsoundPC')), intern(dataSection.readString('wwsoundNPC')))
        else:
            self._soundName = intern(dataSection.readString('wwsound'))
        self._impactNames = ImpactNames(intern(dataSection.readString('impactNPC_PC', '')), intern(dataSection.readString('impactPC_NPC', '')), intern(dataSection.readString('impactNPC_NPC', '')), intern(dataSection.readString('impactFNPC_PC', '')))
        if dataSection.has_key('SWITCH_ext_impact_surface'):
            self._switch_impact_surface = intern(dataSection.readString('SWITCH_ext_impact_surface'))
        if dataSection.has_key('SWITCH_ext_shell_type'):
            self._switch_shell_type = intern(dataSection.readString('SWITCH_ext_shell_type'))
        if not self._soundName and not self._soundNames and not self._impactNames:
            _raiseWrongConfig('wwsound or wwsoundNPC/wwsoundPC or impact tags', dataSection)
        self._stopSyncVisual = dataSection.readBool('stopSyncVisual', False)
        return

    def reattach(self, elem, model):
        sound = elem.get('sound')
        if sound is not None:
            elem['node'] = node = _findTargetNodeSafe(model, self._nodeName)
            sound.matrixProvider = node.actualNode
        else:
            elem['node'] = None
        return

    def create(self, model, effects, args):
        soundName = 'EMPTY_EVENT'
        entityID = args.get('entity_id', None)
        playerID = BigWorld.player().playerVehicleID
        observedVehicleID = BigWorld.player().observedVehicleID
        attachedVehicle = BigWorld.player().getVehicleAttached()
        attackerID = args.get('attackerID')
        if entityID is not None:
            isPlayerVehicle = playerID == entityID or not BigWorld.entity(playerID).isAlive() and entityID == observedVehicleID
        else:
            isPlayerVehicle = args.get('isPlayerVehicle')
            if isPlayerVehicle is None:
                if args.has_key('entity') and hasattr(args['entity'], 'isPlayerVehicle'):
                    isPlayerVehicle = args['entity'].isPlayerVehicle
                else:
                    isPlayerVehicle = False
        if attackerID is None or attachedVehicle is None:
            fromPC = False
        else:
            fromPC = attackerID == playerID or not BigWorld.entity(playerID).isAlive() and attachedVehicle.id == attackerID
        if not fromPC:
            soundName = self._soundNames[0 if isPlayerVehicle else 1] if self._soundNames is not None else self._soundName
        if entityID is not None:
            if soundName.startswith('expl_') and playerID != entityID:
                soundName = self._soundNames[1] if self._soundNames is not None else self._soundName
        elem = {'typeDesc': self}
        elem['node'] = node = _findTargetNodeSafe(model, self._nodeName)
        pos = Math.Matrix(node.actualNode).translation
        startParams = args.get('soundParams', ())
        if self._stopSyncVisual:
            objectName = soundName + '_NODE_' + str(entityID) + '_' + str(self._nodeName)
            elem['sound'] = SoundGroups.g_instance.WWgetSoundObject(objectName, node.actualNode)
            if SoundGroups.DEBUG_TRACE_EFFECTLIST is True:
                _logger.debug('SOUND: EffectList dynamic, %s, %s, %s, %s, %s', soundName, args, node.actualNode, self._nodeName, elem['sound'])
            if SoundGroups.DEBUG_TRACE_STACK is True:
                import traceback
                traceback.print_stack()
            for soundStartParam in startParams:
                elem['sound'].setRTPC(soundStartParam.name, soundStartParam.value)

            elem['sound'].play(soundName)
        elif self._switch_shell_type:
            if self._impactNames is None:
                raise SoftException('impact tags are invalid <%s> <%s> <%s> <%s>' % (self._soundName,
                 self._soundNames,
                 self._switch_impact_surface,
                 self._switch_shell_type))
            m = Math.Matrix(node.actualNode)
            hitdir = args.get('hitdir')
            if hitdir is not None:
                m.translation -= hitdir
            if fromPC:
                soundName = self._impactNames.impactPC_NPC
            elif isPlayerVehicle:
                isCustomAllyDamageEffect = self.__sessionProvider.arenaVisitor.hasCustomAllyDamageEffect()
                isAlly = self.__sessionProvider.getArenaDP().isAlly(attackerID)
                soundName = self._impactNames.impactNPC_PC
                if isCustomAllyDamageEffect and isAlly:
                    soundName = self._impactNames.impactFNPC_PC or self._impactNames.impactNPC_PC
                if not BigWorld.entity(playerID).isAlive():
                    if self.__sessionProvider is not None:
                        spectator = self.__sessionProvider.dynamic.spectator
                        if spectator is not None and spectator.spectatorViewMode in (EPIC_CONSTS.SPECTATOR_MODE_FREECAM, EPIC_CONSTS.SPECTATOR_MODE_FOLLOW):
                            soundName = self._impactNames.impactNPC_NPC
            else:
                soundName = self._impactNames.impactNPC_NPC
            if hitdir is not None:
                t = m.applyToOrigin()
                m.setRotateY(hitdir.yaw)
                m.translation = t
            sound = SoundGroups.g_instance.WWgetSoundObject(soundName + '_MODEL_' + str(id(model)), None, m.translation)
            if SoundGroups.DEBUG_TRACE_EFFECTLIST is True:
                _logger.debug('SOUND: EffectList impacts, %s, %s, %s, %s', soundName, args, str(id(model)), sound)
            if SoundGroups.DEBUG_TRACE_STACK is True:
                import traceback
                traceback.print_stack()
            if sound is not None:
                if self._switch_impact_surface:
                    sound.setSwitch('SWITCH_ext_impact_surface', self._switch_impact_surface)
                sound.setSwitch('SWITCH_ext_shell_type', self._switch_shell_type)
                damage_size = 'SWITCH_ext_damage_size_medium'
                if args.has_key('damageFactor'):
                    factor = args.get('damageFactor', 0.0)
                    if factor < 4335.0 / 100.0:
                        damage_size = 'SWITCH_ext_damage_size_small'
                    elif factor > 8925.0 / 100.0:
                        damage_size = 'SWITCH_ext_damage_size_large'
                sound.setSwitch('SWITCH_ext_damage_size', damage_size)
                self.__setFriendlyFireRTPC(attackerID, sound, soundName)
                sound.play(soundName)
                for soundStartParam in startParams:
                    sound.setRTPC(soundStartParam.name, soundStartParam.value)

        elif startParams:
            sound = SoundGroups.g_instance.WWgetSoundObject(soundName + '_POS_' + str(id(pos)), None, pos)
            if SoundGroups.DEBUG_TRACE_EFFECTLIST is True:
                _logger.debug('SOUND: EffectList WWgetSoundPos, %s, %s, %s, %s', soundName, args, sound, pos)
            if SoundGroups.DEBUG_TRACE_STACK is True:
                import traceback
                traceback.print_stack()
            if sound is not None:
                sound.play(soundName)
                for soundStartParam in startParams:
                    sound.setRTPC(soundStartParam.name, soundStartParam.value)

        else:
            idd = SoundGroups.g_instance.playSoundPos(soundName, pos)
            if SoundGroups.DEBUG_TRACE_EFFECTLIST is True:
                _logger.debug('SOUND: EffectList playSoundPos, %s, %s, %s, %s', soundName, args, idd, pos)
            if SoundGroups.DEBUG_TRACE_STACK is True:
                import traceback
                traceback.print_stack()
            if idd == 0:
                _logger.error('Failed to start sound effect, event ' + soundName)
        effects.append(elem)
        return

    def delete(self, elem, reason):
        if elem.has_key('sound') and elem['sound'] is not None:
            elem['sound'].stopAll()
            elem['sound'] = None
        if elem.has_key('node'):
            elem['node'] = None
        return True

    def prerequisites(self):
        return []

    def __setFriendlyFireRTPC(self, attackerID, sound, soundName):
        if soundName == self._impactNames.impactFNPC_PC and attackerID is not None:
            playerVehiclePosition = BigWorld.player().vehicle.position
            attackerVehiclePosition = BigWorld.entity(attackerID).position
            distance = (playerVehiclePosition - attackerVehiclePosition).length
            sound.setRTPC('RTPC_ext_distance_friendly_attacker', distance)
        return


class _DecalEffectDesc(_EffectDesc):
    __slots__ = ('_texName', '_bumpTexName', '_smTexName', '_groupName', '_size', '_randomYaw', '_variation')
    TYPE = '_DecalEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
        self._texName = dataSection.readString('texName').split()
        self._bumpTexName = dataSection.readString('bumpTexName').split()
        self._smTexName = dataSection.readString('smTexName').split()
        self._groupName = intern(dataSection.readString('groupName'))
        self._size = dataSection.readVector2('size')
        self._randomYaw = dataSection.readBool('randomYaw')
        self._variation = dataSection.readFloat('variation', 0.0)

    def create(self, model, effects, args):
        if not args.get('showDecal', True) or not BigWorld.isDynamicDecalEnabled():
            return
        if not self._texName:
            return
        texIndex = random.randrange(len(self._texName))
        texName = intern(self._texName[texIndex])
        bumpTexName = intern(self._bumpTexName[texIndex]) if texIndex < len(self._bumpTexName) else ''
        smTexName = intern(self._smTexName[texIndex]) if texIndex < len(self._smTexName) else ''
        rayStart = args['start']
        rayEnd = args['end']
        size = self._size.scale(random.uniform(1.0 - self._variation, 1.0 + self._variation))
        center = 0.5 * (rayStart + rayEnd)
        extent = rayEnd - rayStart
        extent.normalise()
        extent *= size.length * 0.707
        BigWorld.wg_addDecal(self._groupName, center - extent, center + extent, size, args['yaw'] if not self._randomYaw else random.uniform(0.0, 3.14), DecalMap.g_instance.getIndex(texName), DecalMap.g_instance.getIndex(bumpTexName), DecalMap.g_instance.getIndex(smTexName))

    def delete(self, elem, reason):
        return True


class _ShockWaveEffectDesc(_EffectDesc):
    __slots__ = ()
    TYPE = '_ShockWaveEffectDesc'

    def __init__(self, dataSection):
        raise SoftException("'shockWave' effect is obsolete, use Dynamic Cameras API instead.")


class _PostProcessEffectDesc(_EffectDesc):
    __slots__ = ()
    TYPE = '_PostProcessEffectDesc'

    def prerequisites(self):
        return []

    def create(self, model, list, args):
        pass

    def delete(self, elem, reason):
        return True


class _FlashBangEffectDesc(_EffectDesc):
    __slots__ = ('_duration', '_keyframes', '__fba', '__clbackId')
    TYPE = '_FlashBangEffectDesc'
    renderSettings = BigWorld.WGRenderSettings()

    def __init__(self, dataSection):
        super(_FlashBangEffectDesc, self).__init__(dataSection)
        self._duration = 0.0
        self._keyframes = list()
        self.__fba = None
        self.__clbackId = None
        for stage in dataSection['stages'].values():
            self._keyframes += [(self._duration, stage.readVector4('color', Math.Vector4(0, 0, 0, 0)))]
            self._duration += stage.asFloat

        return

    def prerequisites(self):
        return []

    def create(self, model, list, args):
        inputHandler = getattr(BigWorld.player(), 'inputHandler')
        if self._isMarkedForPlay(args) and (inputHandler is None or inputHandler.isFlashBangAllowed):
            if self.__fba is not None:
                self.renderSettings.removeFlashBangAnimation(self.__fba)
                BigWorld.cancelCallback(self.__clbackId)
            self.__fba = Math.Vector4Animation()
            self.__fba.keyframes = self._keyframes
            self.__fba.duration = self._duration
            self.renderSettings.flashBangAnimation(self.__fba)
            self.__clbackId = BigWorld.callback(self._duration - 0.05, self.__removeMe)
        elem = {}
        elem['typeDesc'] = self
        list.append(elem)
        return

    @classmethod
    def _isMarkedForPlay(cls, args):
        return args.get('showFlashBang', True)

    def __removeMe(self):
        if self.__fba is not None:
            self.renderSettings.removeFlashBangAnimation(self.__fba)
            self.__clbackId = None
            self.__fba = None
        return

    def delete(self, elem, reason):
        if self.__clbackId is not None:
            BigWorld.cancelCallback(self.__clbackId)
        self.__removeMe()
        return True


class _FriendlyFlashBangEffectDesc(_FlashBangEffectDesc):
    TYPE = '_FriendlyFlashBangEffectDesc'

    @classmethod
    def _isMarkedForPlay(cls, args):
        return args.get('showFriendlyFlashBang', False)


class _StopEmissionEffectDesc(_EffectDesc):
    __slots__ = ()
    TYPE = '_StopEmissionEffectDesc'

    def create(self, model, effects, args):
        for elem in effects:
            pixie = elem.get('pixie')
            if pixie is not None:
                pixie.stopEmission()

        return


class _LightEffectDesc(_EffectDesc):
    __slots__ = ('_innerRadius', '_outerRadius', '_castShadows', '_color', '_alwaysUpdate', '_colorAnimation', '_multiplierAnimation', '_offset')
    TYPE = '_LightEffectDesc'

    def __init__(self, dataSection):
        super(_LightEffectDesc, self).__init__(dataSection)
        self._innerRadius = dataSection.readFloat('innerRadius', 1)
        self._outerRadius = dataSection.readFloat('outerRadius', 2)
        self._castShadows = dataSection.readBool('castShadows', False)
        self._color = dataSection.readVector4('color', Math.Vector4(1, 1, 1, 1))
        self._offset = dataSection.readVector3('offset', Math.Vector3(0, 0, 0))
        self._alwaysUpdate = dataSection.readBool('alwaysUpdateModel', True)
        self._colorAnimation = []
        self._multiplierAnimation = []
        for ds in dataSection.values():
            if ds.name == 'animation':
                t = ds.readFloat('time')
                color = ds.readVector3('color')
                multiplier = ds.readFloat('multiplier')
                self._colorAnimation.append((t, Math.Vector4(color[0], color[1], color[2], 1.0)))
                self._multiplierAnimation.append((t, Math.Vector4(multiplier)))

    def reattach(self, elem, model):
        if not _ALLOW_DYNAMIC_LIGHTS:
            return
        else:
            nodePos = self._nodeName
            if elem['newPos'] is not None:
                nodePos = string.split(elem['newPos'][0], '/') if elem['newPos'][0] else []
            elem['model'] = model
            elem['node'] = _findTargetNode(model, nodePos)
            if elem['light'] is not None:
                elem['light'].source = elem['node'].actualNode
            return

    def create(self, model, effects, args):
        if not _ALLOW_DYNAMIC_LIGHTS:
            return
        else:
            elem = {}
            elem['newPos'] = args.get('position', None)
            nodePos = self._nodeName
            if elem['newPos'] is not None:
                nodePos = string.split(elem['newPos'][0], '/') if elem['newPos'][0] else []
            elem['model'] = model
            elem['node'] = _findTargetNode(model, nodePos)
            elem['typeDesc'] = self
            elem['light'] = None
            elem['callback'] = BigWorld.callback(0.01, partial(self._callbackCreate, elem))
            effects.append(elem)
            return

    def _callbackCreate(self, elem):
        light = BigWorld.PyOmniLight()
        colorKeyFrames = []
        multiplierKeyFrames = []
        for c in self._colorAnimation:
            colorKeyFrames.append((c[0] * self.duration, c[1]))

        for m in self._multiplierAnimation:
            multiplierKeyFrames.append((m[0] * self.duration, m[1]))

        colorAnimator = Math.Vector4Animation()
        colorAnimator.duration = 10000000.0
        colorAnimator.keyframes = colorKeyFrames
        multiplierAnimator = Math.Vector4Animation()
        multiplierAnimator.duration = 10000000.0
        multiplierAnimator.keyframes = multiplierKeyFrames
        light.innerRadius = self._innerRadius
        light.outerRadius = self._outerRadius
        light.castShadows = self._castShadows
        light.offset = self._offset
        light.source = elem['node'].actualNode
        light.colorAnimator = colorAnimator
        light.multiplierAnimator = multiplierAnimator
        elem['light'] = light
        elem['callback'] = None
        return

    def delete(self, elem, reason):
        if not _ALLOW_DYNAMIC_LIGHTS:
            return True
        else:
            callback = elem['callback']
            if callback is not None:
                BigWorld.cancelCallback(callback)
            if elem['light'] is not None:
                elem['light'].destroyLight()
                elem['light'] = None
            return True


_effectDescFactory = {'pixie': _PixieEffectDesc,
 'animation': _AnimationEffectDesc,
 'sound': _SoundEffectDesc,
 'splashSound': _NodeSoundEffectDesc,
 'collisionSound': _CollisionSoundEffectDesc,
 'tracerSound': _TracerSoundEffectDesc,
 'shotSound': _ShotSoundEffectDesc,
 'visibility': _VisibilityEffectDesc,
 'model': _ModelEffectDesc,
 'decal': _DecalEffectDesc,
 'shockWave': _ShockWaveEffectDesc,
 'flashBang': _FlashBangEffectDesc,
 'friendlyFlashBang': _FriendlyFlashBangEffectDesc,
 'stopEmission': _StopEmissionEffectDesc,
 'posteffect': _PostProcessEffectDesc,
 'light': _LightEffectDesc,
 'destructionSound': _DestructionSoundEffectDesc,
 'lifetimeSound': _DestructionSoundEffectDesc}

def _createEffectDesc(eType, dataSection):
    if not dataSection.values():
        return
    else:
        factoryMethod = _effectDescFactory.get(eType, None)
        if factoryMethod is not None:
            return factoryMethod(dataSection)
        raise SoftException('EffectsList factory has no class associated with type %s.' % eType)
        return


def _raiseWrongConfig(paramName, effectType):
    raise SoftException('missing or wrong parameter <%s> in effect descriptor <%s>.' % (paramName, effectType))


def __getTransformAlongNormal(localTransform, worldTransform, normal):
    originalTranslation = Math.Vector3(0, 0, 0) if localTransform is None else localTransform.translation
    localTransform = Math.Matrix()
    localTransform.setRotateYPR((normal.yaw, normal.pitch + 1.57, 0))
    invWorldOrient = Math.Matrix(worldTransform)
    invWorldOrient.translation = Math.Vector3(0, 0, 0)
    invWorldOrient.invert()
    localTransform.postMultiply(invWorldOrient)
    localTransform.translation = originalTranslation
    return localTransform


def _getSurfaceAlignedTransform(model, nodeName, localTransform, precalculatedNormal=None):
    node = model.node(nodeName)
    if node is None:
        worldTransform = Math.Matrix(model.root)
    else:
        worldTransform = Math.Matrix(node)
    if precalculatedNormal is not None:
        return __getTransformAlongNormal(localTransform, worldTransform, precalculatedNormal)
    else:
        if localTransform is not None:
            worldTransform.preMultiply(localTransform)
        pos = worldTransform.applyToOrigin()
        normal = worldTransform.applyVector((0, 0, 1))
        offsets = (Math.Vector3(0, -0.1, 0),
         Math.Vector3(-0.1, 0, 0),
         Math.Vector3(0.1, 0, 0),
         Math.Vector3(0, 0, -0.1),
         Math.Vector3(0, 0, 0.1))
        spaceID = BigWorld.player().spaceID
        for offset in offsets:
            res = BigWorld.wg_collideSegment(spaceID, pos, pos + offset, 128)
            if res is None:
                continue
            normal = res.normal
            localTransform = __getTransformAlongNormal(localTransform, worldTransform, normal)
            break

        return localTransform


class _NodeWithLocal(object):
    actualNode = property(lambda self: self.__node)

    def __init__(self, model, nodeName='', local=None):
        if local is None:
            local = Math.Matrix()
            local.setIdentity()
        if _isPyModel(model):
            allAttachmentsChecked = success = False
            attachmentsChecked = 0
            while not allAttachmentsChecked and not success:
                try:
                    if attachmentsChecked > 0:
                        self.__node = model.root.attachments[attachmentsChecked - 1].node(nodeName, local)
                        success = True
                    else:
                        self.__node = model.node(nodeName, local)
                        success = True
                except Exception:
                    attachmentsChecked += 1
                    allAttachmentsChecked = True if not hasattr(model.root, 'attachments') else 1 + len(model.root.attachments) - attachmentsChecked < 1
                    self.__node = model.node('', local)

            self.__localMatrix = None
        else:
            if nodeName in ('', 'Scene Root'):
                self.__node = model.root
            else:
                self.__node = model.node(nodeName)
            if self.__node is None:
                self.__node = model.root
            self.__localMatrix = local
        return

    def attach(self, attachment):
        if self.__localMatrix is None:
            self.__node.attach(attachment)
            return
        else:
            self.__node.attach(attachment, self.__localMatrix)
            return

    def __getattr__(self, item):
        return getattr(self.__node, item)


def _findTargetNode(model, nodes, localTransform=None, orientByClosestSurfaceNormal=False, precalculatedNormal=None):
    if len(nodes) > 1:
        _logger.debug('Slashed nodepath is not supported any longer')
    if not nodes:
        if orientByClosestSurfaceNormal:
            localTransform = _getSurfaceAlignedTransform(model, '', localTransform, precalculatedNormal)
        return _NodeWithLocal(model, '', localTransform)
    if orientByClosestSurfaceNormal:
        localTransform = _getSurfaceAlignedTransform(model, nodes[-1], localTransform, precalculatedNormal)
    return _NodeWithLocal(model, nodes[-1], localTransform)


def _findTargetNodeSafe(model, nodes, local=None):
    node = None
    if nodes:
        node = _findTargetNode(model, nodes, local)
    if node is None:
        node = _NodeWithLocal(model, '', local)
    return node


def _findTargetModel(model, nodes):
    _logger.debug('THIS FEATURE IS NOT SUPPORTED')
    targetNode = model
    for iter in xrange(0, len(nodes)):
        found = False
        for elem in targetNode.node(nodes[iter]).attachments:
            if isinstance(elem, BigWorld.Model):
                targetNode = elem
                found = True
                break

        if not found:
            raise SoftException("can't find model attachments in %s" % nodes[iter])

    return targetNode


def __keyPointsFromStagesSection(stagesSection):
    keyPoints = []
    stagesNames = set()
    totalTime = 0.0
    for stageName in stagesSection.keys():
        if stageName in stagesNames:
            return stageName
        duration = stagesSection.readFloat(stageName)
        stagesNames.add(stageName)
        keyPoints.append(KeyPoint(stageName, totalTime))
        totalTime += duration

    if keyPoints and keyPoints[0].name != __START_KEY_POINT.name:
        keyPoints.insert(0, __START_KEY_POINT)
    keyPoints.append(KeyPoint(SpecialKeyPointNames.END, totalTime))
    return keyPoints


def __keyPointsFromTimeLineSection(keyPointSection):
    keyPoints = []
    keyPointNames = set()
    for keyPointName in keyPointSection.keys():
        if keyPointName in keyPointNames:
            return keyPointName
        timePoint = keyPointSection.readFloat(keyPointName)
        keyPointNames.add(keyPointName)
        keyPoints.append(KeyPoint(keyPointName, timePoint))

    keyPoints.sort(key=lambda self: self.time)
    if keyPoints and keyPoints[0].name != __START_KEY_POINT.name:
        keyPoints.insert(0, __START_KEY_POINT)
    return keyPoints


def effectsFromSection(section):
    keyPoints = None
    stagesSection = section['stages']
    if stagesSection is not None:
        keyPoints = __keyPointsFromStagesSection(stagesSection)
    timeLineSection = section['timeline']
    if timeLineSection is not None:
        if keyPoints is None:
            keyPoints = __keyPointsFromTimeLineSection(timeLineSection)
        else:
            raise SoftException('Both stages and timeline defined in effect %s' % section.name)
    if keyPoints is None:
        raise SoftException('Neither stages nor timeline defined in effect %s' % section.name)
    if isinstance(keyPoints, str):
        raise SoftException('Duplicate keypoint %s in effect %s' % (keyPoints, section.name))
    effectsSec = section['effects']
    effectList = EffectsList(effectsSec)
    if section['relatedEffects'] is not None:
        for tagName, subSection in section['relatedEffects'].items():
            effectList.relatedEffects[tagName] = effectsFromSection(subSection)

    return EffectsTimeLine(keyPoints, effectList)


class RespawnDestroyEffect(object):

    @staticmethod
    def play(vehicle_id):
        vehicle = BigWorld.entity(vehicle_id)
        if vehicle is None:
            return
        else:
            effects = vehicle.typeDescriptor.type.effects['fullDestruction']
            if not effects:
                return
            vehicle.show(False)
            if vehicle.model is not None:
                fakeModel = helpers.newFakeModel()
                BigWorld.addModel(fakeModel)
                fakeModel.position = vehicle.model.position
                effectsPlayer = EffectsListPlayer(effects[0][1], effects[0][0])
                effectsPlayer.play(fakeModel, SpecialKeyPointNames.START, partial(BigWorld.delModel, fakeModel))
            return
