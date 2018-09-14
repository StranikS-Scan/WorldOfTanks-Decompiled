# Embedded file name: scripts/client/helpers/EffectsList.py
import BigWorld
import ResMgr
import Pixie
import Math
from collections import namedtuple
import random
import DecalMap
import material_kinds
from debug_utils import *
from functools import partial
import string
import SoundGroups
_ALLOW_DYNAMIC_LIGHTS = True
g_disableEffects = False
KeyPoint = namedtuple('KeyPoint', ('name', 'time'))
EffectsTimeLine = namedtuple('EffectsTimeLine', ('keyPoints', 'effectsList'))
EffectsTimeLinePrereqs = namedtuple('EffectsTimeLinePrereqs', ('keyPoints', 'effectsList', 'prereqs'))

class SpecialKeyPointNames:
    START = 'start'
    END = 'end'
    STATIC = 'static'


__START_KEY_POINT = KeyPoint(SpecialKeyPointNames.START, 0.0)
SoundStartParam = namedtuple('SoundStartParam', ('name', 'value'))

def reload():
    import __builtin__
    from sys import modules
    __builtin__.reload(modules[reload.__module__])


class EffectsList(object):

    def __init__(self, section):
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
        for elem in data['_EffectsList_effects']:
            elem['typeDesc'].reattach(elem, model)

    def detachFrom(self, data, key):
        effects = data['_EffectsList_effects']
        for elem in effects[:]:
            if elem['typeDesc'].endKey == key:
                if elem['typeDesc'].delete(elem, 1):
                    effects.remove(elem)

    def detachAllFrom(self, data, keepPosteffects = False):
        effects = data['_EffectsList_effects']
        if keepPosteffects:
            for elem in effects[:]:
                if elem['typeDesc'].delete(elem, 2):
                    effects.remove(elem)

            return
        for elem in effects[:]:
            elem['typeDesc'].delete(elem, 0)
            effects.remove(elem)

        del data['_EffectsList_effects']


class EffectsListPlayer:
    effectsList = property(lambda self: self.__effectsList)
    activeEffects = []

    @staticmethod
    def clear():
        import BattleReplay
        replayCtrl = BattleReplay.g_replayCtrl
        if not replayCtrl.isPlaying:
            return
        else:
            warpDelta = replayCtrl.warpTime - replayCtrl.currentTime
            for effect in EffectsListPlayer.activeEffects[:]:
                if effect.__waitForKeyOff:
                    continue
                if warpDelta <= 0.0 or effect.__keyPoints[-1].time - effect.__curKeyPoint.time < warpDelta:
                    if effect.__callbackFunc is not None:
                        effect.__callbackFunc()
                    effect.stop()

            return

    def __init__(self, effectsList, keyPoints, **args):
        self.__keyPoints = keyPoints
        self.__effectsList = effectsList
        self.__args = args
        self.__args['keyPoints'] = self.__keyPoints
        self.__curKeyPoint = None
        self.__callbackFunc = None
        self.__keyPointIdx = -1
        self.__isStarted = False
        self.__waitForKeyOff = False
        return

    def play(self, model, startKeyPoint = None, callbackFunc = None, waitForKeyOff = False):
        needPlay, newKey = self.__isNeedToPlay(waitForKeyOff)
        if not needPlay:
            return
        else:
            if newKey is not None:
                startKeyPoint = newKey
            if self.__isStarted:
                LOG_ERROR('player already started. To restart it you must before call stop().')
                return
            import BattleReplay
            if BattleReplay.g_replayCtrl.isPlaying:
                EffectsListPlayer.activeEffects.append(self)
            self.__isStarted = True
            self.__callbackID = None
            self.__model = model
            self.__data = {}
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

    def keyOff(self, waitForNextKeyOff = False):
        self.__playKeyPoint(waitForNextKeyOff)

    def reattachTo(self, model):
        if self.__isStarted:
            self.__effectsList.reattachTo(model, self.__data)
            self.__model = model

    def __isNeedToPlay(self, waitForKeyOff):
        global g_disableEffects
        if g_disableEffects:
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

    def stop(self, keepPosteffects = False):
        if not self.__isStarted:
            return
        else:
            import BattleReplay
            if BattleReplay.g_replayCtrl.isPlaying:
                EffectsListPlayer.activeEffects.remove(self)
            self.__isStarted = False
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            self.__effectsList.detachAllFrom(self.__data, keepPosteffects)
            self.__model = None
            self.__data = None
            self.__curKeyPoint = None
            self.__callbackFunc = None
            return

    def __getKeyPointIdx(self, name):
        for i, keyPoint in enumerate(self.__keyPoints):
            if keyPoint.name == name:
                return i

    def __playKeyPoint(self, waitForKeyOff = False):
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
            LOG_CURRENT_EXCEPTION()

        return


class _EffectDesc:

    def __init__(self, dataSection):
        self.startKey = dataSection.readString('startKey')
        if not self.startKey:
            _raiseWrongConfig('startKey', self.TYPE)
        self.endKey = dataSection.readString('endKey')
        pos = dataSection.readString('position')
        self.modelPart = dataSection.readString('modelPart', '')
        self._pos = string.split(pos, '/') if pos else []

    def prerequisites(self):
        return []

    def reattach(self, elem, model):
        pass

    def create(self, model, list, args):
        pass

    def delete(self, elem, reason):
        return True


class _PixieEffectDesc(_EffectDesc):
    TYPE = '_PixieEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
        self._files = [ f for f in dataSection.readStrings('file') if f ]
        if len(self._files) == 0:
            _raiseWrongConfig('file', self.TYPE)
        self._havokFiles = None
        if dataSection.readBool('hasHavokVersion', False):
            self._havokFiles = tuple([ self.__getHavokFileName(f) for f in self._files ])
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
        nodePos = self._pos
        elem['model'] = model
        if elem['newPos'] is not None:
            nodePos = string.split(elem['newPos'][0], '/') if elem['newPos'][0] else []
        if elem['pixie'] is not None and elem['pixie'] in elem['node'].attachments:
            elem['node'].detach(elem['pixie'])
            elem['node'] = _findTargetNode(model, nodePos, elem['newPos'][1] if elem['newPos'] else None, self._orientByClosestSurfaceNormal, elem['surfaceNormal'])
            elem['node'].attach(elem['pixie'])
        else:
            elem['node'] = _findTargetNode(model, nodePos, None, self._orientByClosestSurfaceNormal, elem['surfaceNormal'])
        return

    def create(self, model, list, args):
        elem = {}
        elem['newPos'] = args.get('position', None)
        nodePos = self._pos
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
        elem['model'] = model
        elem['typeDesc'] = self
        elem['pixie'] = None
        elem['cancelLoadCallback'] = False
        elem['callbackID'] = None
        if self._havokFiles is None:
            file = random.choice(self._files)
        else:
            file, fileToClear = random.choice(zip(self._files, self._havokFiles))
            if args.get('havokEnabled', False):
                file, fileToClear = fileToClear, file
            self.__prototypePixies.pop(fileToClear, None)
        prototypePixie = self.__prototypePixies.get(file)
        if prototypePixie is not None:
            elem['pixie'] = prototypePixie.clone()
            self._callbackCreate(elem)
        else:
            elem['file'] = file
            Pixie.createBG(file, partial(self._callbackAfterLoading, elem))
        list.append(elem)
        return

    def delete(self, elem, reason):
        callbackID = elem['callbackID']
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
            elem['callbackID'] = None
        elif elem['pixie'] is None:
            elem['cancelLoadCallback'] = True
        else:
            elem['node'].detach(elem['pixie'])
        elem['pixie'] = None
        return True

    def _callbackAfterLoading(self, elem, pixie):
        if pixie is None:
            LOG_ERROR("Can't create pixie '%s'." % elem['file'])
            return
        else:
            if not elem['cancelLoadCallback']:
                self.__prototypePixies[elem['file']] = pixie
                elem['pixie'] = pixie.clone()
                self._callbackCreate(elem)
            return

    def _callbackCreate(self, elem):
        if elem['pixie'] is None:
            LOG_CODEPOINT_WARNING()
            return
        else:
            scale = elem.get('scale')
            if scale is not None:
                elem['pixie'].scale = scale
            elem['callbackID'] = None
            if self._force > 0:
                elem['pixie'].force(self._force)
            elem['node'].attach(elem['pixie'])
            return

    @staticmethod
    def __getHavokFileName(fileName):
        import os
        fileName, fileExtension = os.path.splitext(fileName)
        return fileName + '_havok' + fileExtension


class _AnimationEffectDesc(_EffectDesc):
    TYPE = '_AnimationEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
        self._name = dataSection.readString('name')
        if not self._name:
            _raiseWrongConfig('name', self.TYPE)

    def create(self, model, list, args):
        targetModel = _findTargetModel(model, self._pos)
        self._action = targetModel.action(self._name)
        self._action()
        list.append({'typeDesc': self,
         'action': self._action})

    def delete(self, elem, reason):
        if reason == 2:
            if self.endKey:
                elem['action'].stop()
                return True
            return False
        else:
            elem['action'].stop()
            return True


class _VisibilityEffectDesc(_EffectDesc):
    TYPE = '_VisibilityEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
        self._hasInitial = False
        self._initial = False
        key = 'initial'
        if dataSection.has_key(key):
            self._initial = dataSection.readBool(key, False)
            self._hasInitial = True

    def create(self, model, list, args):
        targetModel = _findTargetModel(model, self._pos)
        if self._hasInitial:
            targetModel.visible = self._initial
        else:
            targetModel.visible = not targetModel.visible
        list.append({'typeDesc': self,
         'model': targetModel})

    def delete(self, elem, reason):
        if self._hasInitial:
            elem['model'].visible = not self._initial
        else:
            elem['model'].visible = not elem['model'].visible
        return True

    def delete(self, elem, reason):
        return True


class _ModelEffectDesc(_EffectDesc):
    TYPE = '_ModelEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
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
        nodeName = self._pos
        if elem['newPos'] is not None:
            nodeName = string.split(elem['newPos'][0], '/') if elem['newPos'][0] else []
        targetNode = _findTargetNode(model, nodeName, elem['newPos'][1] if elem['newPos'] else None)
        targetNode.attach(model)
        return

    def create(self, model, list, args):
        currentModel = BigWorld.Model(self._modelName)
        newPos = args.get('position', None)
        nodeName = self._pos
        if newPos is not None:
            nodeName = string.split(newPos[0], '/') if newPos[0] else []
        targetNode = _findTargetNode(model, nodeName, newPos[1] if newPos else None)
        targetNode.attach(currentModel)
        if self._animation:
            currentModel.action(self._animation)()
        elem = {'typeDesc': self,
         'model': model,
         'attachment': currentModel,
         'newPos': newPos,
         'node': targetNode}
        list.append(elem)
        return currentModel

    def delete(self, elem, reason):
        elem['node'].detach(elem['attachment'])
        return True


class _SoundEffectDesc(_EffectDesc):
    TYPE = '_SoundEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
        self._soundName = None
        self._soundNames = None
        self._fakeModel = None
        self._node = None
        if dataSection.has_key('soundPC') and dataSection.has_key('soundNPC'):
            self._soundNames = (dataSection.readString('soundPC'), dataSection.readString('soundNPC'))
        else:
            self._soundName = dataSection.readString('sound')
        if not self._soundName and not self._soundNames:
            _raiseWrongConfig('sound or soundNPC/soundPC', self.TYPE)
        return

    def reattach(self, elem, model):
        pass

    def create(self, model, list, args):
        isPlayer = args.get('isPlayer')
        if isPlayer is None:
            if args.has_key('entity') and hasattr(args['entity'], 'isPlayer'):
                isPlayer = args['entity'].isPlayer
            else:
                isPlayer = False
        soundName = self._soundNames[0 if isPlayer else 1] if self._soundNames is not None else self._soundName
        part = args.get('modelMap', {}).get(self.modelPart)
        if part is not None:
            model = part
        if len(self._pos) > 0:
            self._node = _findTargetNode(model, self._pos)
        sound = None
        try:
            if self._node is not None:
                self._fakeModel = BigWorld.player().newFakeModel()
                self._node.attach(self._fakeModel)
                sound = SoundGroups.g_instance.getSound(self._fakeModel, soundName)
            else:
                sound = SoundGroups.g_instance.getSound(model, soundName)
        except Exception:
            LOG_CURRENT_EXCEPTION()

        if sound is not None:
            startParams = args.get('soundParams', ())
            for soundStartParam in startParams:
                param = sound.param(soundStartParam.name)
                if param is not None:
                    param.value = soundStartParam.value

            sound.play()
            list.append({'typeDesc': self,
             'sound': sound})
        return

    def delete(self, elem, reason):
        if self._node is not None:
            self._node.detach(self._fakeModel)
            self._node = None
        self._fakeModel = None
        if reason == 2:
            if self.endKey:
                elem['sound'].stop()
                return True
            return False
        else:
            elem['sound'].stop()
            return True
            return

    def prerequisites(self):
        try:
            for soundName in [self._soundNames and self._soundNames[0] or '', self._soundNames and self._soundNames[1] or '', self._soundName or '']:
                if soundName.find('/guns/') > -1:
                    SoundGroups.g_instance.FMODloadSound(soundName)

        except Exception as e:
            LOG_ERROR(e.message)

        return []


class _SoundParameterEffectDesc(_EffectDesc):
    TYPE = '_SoundParameterEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
        self.__params = []
        self._paramName = dataSection.readString('paramName')
        self._paramValue = dataSection.readFloat('paramValue', -100000.0)
        if self._paramName == '' or self._paramValue == -100000.0:
            raise Exception, "parameter 'paramName' or 'paramValue' is missing in soundParam effect descriptor."
        self.__sniperModeUpdateCb = None
        if dataSection.has_key('paramValue/sniperMode'):
            self._sniperModeValue = dataSection.readFloat('paramValue/sniperMode')
        else:
            self._sniperModeValue = None
        return

    def reattach(self, elem, model):
        pass

    def create(self, model, list, args):
        self.__params = []
        processedSoundNames = []
        for elem in list:
            if elem.get('isSoundParam'):
                elem['typeDesc'].delete(None, None)
                continue
            if elem.get('sound') is not None:
                processedSoundNames.append(elem['sound'].name)
                param = elem['sound'].param(self._paramName)
                if param is not None:
                    param.seekSpeed = 0
                    self.__params.append(param)

        if len(self.__params) == 0:
            LOG_ERROR("Failed to find parameter named '" + self._paramName + "' in sound events: '" + str(processedSoundNames) + "'")
        self.__isPlayer = args.get('isPlayer', False)
        self.__updateParamValue()
        list.append({'typeDesc': self,
         'isSoundParam': True})
        return

    def __updateParamValue(self):
        if len(self.__params) == 0:
            return
        else:
            try:
                val = self._paramValue
                if self.__isPlayer and self._sniperModeValue is not None:
                    aih = BigWorld.player().inputHandler
                    if aih.ctrl == aih.ctrls['sniper']:
                        val = self._sniperModeValue
                for param in self.__params:
                    param.value = val

            except Exception:
                LOG_CURRENT_EXCEPTION()

            if self._sniperModeValue is not None:
                self.__sniperModeUpdateCb = BigWorld.callback(0.1, self.__updateParamValue)
            return

    def delete(self, elem, reason):
        if self.__sniperModeUpdateCb is not None:
            BigWorld.cancelCallback(self.__sniperModeUpdateCb)
            self.__sniperModeUpdateCb = None
        self.__params = []
        return True


class _DecalEffectDesc(_EffectDesc):
    TYPE = '_DecalEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
        self._texName = dataSection.readString('texName')
        bumpSubsection = dataSection['bumpTexName']
        if bumpSubsection is None:
            self._bumpTexName = ''
        else:
            self._bumpTexName = bumpSubsection.asString
        self._groupName = dataSection.readString('groupName')
        self._size = dataSection.readVector2('size')
        self._randomYaw = dataSection.readBool('randomYaw')
        self._variation = dataSection.readFloat('variation', 0.0)
        return

    def create(self, model, list, args):
        if not args.get('showDecal', True):
            return
        rayStart = args['start']
        rayEnd = args['end']
        size = self._size.scale(random.uniform(1.0 - self._variation, 1.0 + self._variation))
        center = 0.5 * (rayStart + rayEnd)
        extent = rayEnd - rayStart
        extent.normalise()
        extent *= size.length * 0.707
        BigWorld.wg_addDecal(self._groupName, center - extent, center + extent, size, args['yaw'] if not self._randomYaw else random.uniform(0.0, 3.14), DecalMap.g_instance.getIndex(self._texName), DecalMap.g_instance.getIndex(self._bumpTexName))

    def delete(self, elem, reason):
        return True


class _ShockWaveEffectDesc(_EffectDesc):
    TYPE = '_ShockWaveEffectDesc'

    def __init__(self, dataSection):
        raise Exception, "'shockWave' effect is obsolete, use Dynamic Cameras API instead."


class _PostProcessEffectDesc(_EffectDesc):
    TYPE = '_PostProcessEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)

    def prerequisites(self):
        return []

    def create(self, model, list, args):
        pass

    def delete(self, elem, reason):
        return True


class _FlashBangEffectDesc(_EffectDesc):
    TYPE = '_FlashBangEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
        self._duration = 0.0
        self._keyframes = list()
        for stage in dataSection['stages'].values():
            self._keyframes += [(self._duration, stage.readVector4('color', Math.Vector4(0, 0, 0, 0)))]
            self._duration += stage.asFloat

    def prerequisites(self):
        return []

    def create(self, model, list, args):
        inputHandler = getattr(BigWorld.player(), 'inputHandler')
        if args.get('showFlashBang', True) and (inputHandler is None or inputHandler.isFlashBangAllowed):
            fba = Math.Vector4Animation()
            fba.keyframes = self._keyframes
            fba.duration = self._duration
            BigWorld.flashBangAnimation(fba)
            BigWorld.callback(self._duration - 0.05, partial(BigWorld.removeFlashBangAnimation, fba))
        return

    def delete(self, elem, reason):
        return True


class _StopEmissionEffectDesc(_EffectDesc):
    TYPE = '_StopEmissionEffectDesc'

    def create(self, model, list, args):
        for elem in list:
            pixie = elem.get('pixie')
            if pixie is None:
                continue
            for i in xrange(pixie.nSystems()):
                source = pixie.system(i).action(1)
                source.rate = 0

        return


class _LightEffectDesc(_EffectDesc):
    TYPE = '_LightEffectDesc'

    def __init__(self, dataSection):
        _EffectDesc.__init__(self, dataSection)
        self._innerRadius = dataSection.readFloat('innerRadius', 1)
        self._outerRadius = dataSection.readFloat('outerRadius', 2)
        self._castShadows = dataSection.readBool('castShadows', False)
        self._color = dataSection.readVector4('color', Math.Vector4(1, 1, 1, 1))
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
            nodePos = self._pos
            if elem['newPos'] is not None:
                nodePos = string.split(elem['newPos'][0], '/') if elem['newPos'][0] else []
            elem['model'] = model
            elem['node'] = _findTargetNode(model, nodePos)
            if elem['light'] is not None:
                elem['light'].source = elem['node']
            return

    def create(self, model, list, args):
        if not _ALLOW_DYNAMIC_LIGHTS:
            return
        else:
            elem = {}
            elem['newPos'] = args.get('position', None)
            nodePos = self._pos
            if elem['newPos'] is not None:
                nodePos = string.split(elem['newPos'][0], '/') if elem['newPos'][0] else []
            elem['model'] = model
            elem['node'] = _findTargetNode(model, nodePos)
            elem['typeDesc'] = self
            elem['light'] = None
            elem['callback'] = BigWorld.callback(0.01, partial(self._callbackCreate, elem))
            list.append(elem)
            return

    def _callbackCreate(self, elem):
        light = BigWorld.PyChunkLight()
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
        light.source = elem['node']
        light.colorAnimator = colorAnimator
        light.multiplierAnimator = multiplierAnimator
        light.specular = 1
        light.diffuse = 1
        light.visible = True
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
                elem['light'].visible = False
                elem['light'].source = None
                elem['light'] = None
            return True


def _createEffectDesc(type, dataSection):
    if len(dataSection.values()) == 0:
        return None
    elif type == 'pixie':
        return _PixieEffectDesc(dataSection)
    elif type == 'animation':
        return _AnimationEffectDesc(dataSection)
    elif type == 'sound':
        return _SoundEffectDesc(dataSection)
    elif type == 'soundParam':
        return _SoundParameterEffectDesc(dataSection)
    elif type == 'visibility':
        return _VisibilityEffectDesc(dataSection)
    elif type == 'model':
        return _ModelEffectDesc(dataSection)
    elif type == 'decal':
        return _DecalEffectDesc(dataSection)
    elif type == 'shockWave':
        return _ShockWaveEffectDesc(dataSection)
    elif type == 'flashBang':
        return _FlashBangEffectDesc(dataSection)
    elif type == 'stopEmission':
        return _StopEmissionEffectDesc(dataSection)
    elif type == 'posteffect':
        return _PostProcessEffectDesc(dataSection)
    elif type == 'light':
        return _LightEffectDesc(dataSection)
    else:
        raise Exception, 'EffectsList factory has no class associated with type %s.' % type
        return None


def _raiseWrongConfig(paramName, effectType):
    raise Exception, 'missing or wrong parameter <%s> in effect descriptor <%s>.' % (paramName, effectType)


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


def _getSurfaceAlignedTransform(model, nodeName, localTransform, precalculatedNormal = None):
    worldTransform = Math.Matrix(model.node(nodeName))
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
        isFound = False
        spaceID = BigWorld.player().spaceID
        for offset in offsets:
            res = BigWorld.wg_collideSegment(spaceID, pos, pos + offset, 128)
            if res is None:
                continue
            normal = res[1]
            localTransform = __getTransformAlongNormal(localTransform, worldTransform, normal)
            break

        return localTransform


def _findTargetNode(model, nodes, localTransform = None, orientByClosestSurfaceNormal = False, precalculatedNormal = None):
    targetNode = model
    length = len(nodes)
    find = False
    if length == 0:
        if orientByClosestSurfaceNormal:
            localTransform = _getSurfaceAlignedTransform(model, 'Scene Root', localTransform, precalculatedNormal)
        return model.node('Scene Root', localTransform)
    for iter in range(0, length - 1):
        find = False
        for elem in targetNode.node(nodes[iter]).attachments:
            if isinstance(elem, BigWorld.Model):
                targetNode = elem
                find = True
                break

        if not find:
            raise Exception, "can't find model attachments in %s" % nodes[iter]

    if orientByClosestSurfaceNormal:
        localTransform = _getSurfaceAlignedTransform(targetNode, nodes[length - 1], localTransform, precalculatedNormal)
    return targetNode.node(nodes[length - 1], localTransform)


def _findTargetModel(model, nodes):
    targetNode = model
    find = False
    for iter in range(0, len(nodes)):
        find = False
        for elem in targetNode.node(nodes[iter]).attachments:
            if isinstance(elem, BigWorld.Model):
                targetNode = elem
                find = True
                break

        if not find:
            raise Exception, "can't find model attachments in %s" % nodes[iter]

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
            raise Exception, 'Both stages and timeline defined in effect %s' % section.name
    if keyPoints is None:
        raise Exception, 'Neither stages nor timeline defined in effect %s' % section.name
    if isinstance(keyPoints, str):
        raise Exception, 'Duplicate keypoint %s in effect %s' % (keyPoints, section.name)
    effectsSec = section['effects']
    effectList = EffectsList(effectsSec)
    if section['relatedEffects'] is not None:
        for tagName, subSection in section['relatedEffects'].items():
            effectList.relatedEffects[tagName] = effectsFromSection(subSection)

    return EffectsTimeLine(keyPoints, effectList)
