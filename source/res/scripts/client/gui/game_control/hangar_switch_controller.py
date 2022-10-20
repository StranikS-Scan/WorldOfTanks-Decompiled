# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/hangar_switch_controller.py
import json
import logging
import BigWorld
import Event
import ResMgr
from constants import DEFAULT_HANGAR_SCENE
from soft_exception import SoftException
from PlayerEvents import g_playerEvents
from helpers import dependency
from gui.prb_control.entities.listener import IGlobalListener
from skeletons.gui.game_control import IHangarSpaceSwitchController
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.utils.hangar_space_reloader import ErrorFlags
from shared_utils import nextTick
from skeletons.gui.shared.utils import IHangarSpaceReloader, IHangarSpace
from gui.ClientHangarSpace import SERVER_CMD_CHANGE_HANGAR, SERVER_CMD_CHANGE_HANGAR_PREM, getDefaultHangarPath, SERVER_CMD_CHANGE_HANGAR_ALT, getHangarFullVisibilityMask, g_clientHangarSpaceOverride
_logger = logging.getLogger(__name__)

class DefaultHangarSpaceConfig(object):

    def __init__(self):
        self._visibilityMask = {True: None,
         False: None}
        self._spaceIdOverride = {}
        return

    def getVisibilityMask(self, isPremium):
        return self._visibilityMask[isPremium] if self._visibilityMask[isPremium] is not None else getHangarFullVisibilityMask(self.getHangarSpaceId(isPremium))

    def discardVisibilityMaskOverride(self, isPremium):
        self._visibilityMask[isPremium] = None
        return

    def setVisibilityMask(self, isPremium, visibilityMask):
        self._visibilityMask[isPremium] = visibilityMask

    def getHangarSpaceId(self, isPremium):
        path = self._spaceIdOverride.get(isPremium)
        return path if path is not None else getDefaultHangarPath(isPremium)

    def setSpaceIdOverride(self, isPremium, newId):
        self._spaceIdOverride[isPremium] = newId

    def discardSpaceIdOverride(self, isPremium):
        del self._spaceIdOverride[isPremium]


class SceneSpaceConfig(object):

    def __init__(self, spaceId=None, waitingMessage=None, waitingBackground=None, spaceIdOverride=None, visibilityMask=None):
        self._waitingMessage = waitingMessage
        self._waitingBackground = waitingBackground
        self._spaceId = spaceId
        self._spaceIdOverride = spaceIdOverride
        self._visibilityMask = visibilityMask

    @property
    def waitingMessage(self):
        return self._waitingMessage

    @property
    def waitingBackground(self):
        return self._waitingBackground

    def getVisibilityMask(self):
        return self._visibilityMask if self._visibilityMask is not None else getHangarFullVisibilityMask(self.getHangarSpaceId())

    def discardVisibilityMaskOverride(self):
        self._visibilityMask = None
        return

    def setVisibilityMask(self, visibilityMask):
        self._visibilityMask = visibilityMask

    def getHangarSpaceId(self):
        return self._spaceIdOverride if self._spaceIdOverride is not None else self._spaceId

    def setSpaceIdOverride(self, newId):
        self._spaceIdOverride = newId

    def discardSpaceIdOverride(self):
        self._spaceIdOverride = None
        return


class HangarSpaceSwitchController(IHangarSpaceSwitchController, IGlobalListener):
    hangarSpaceReloader = dependency.descriptor(IHangarSpaceReloader)
    hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(HangarSpaceSwitchController, self).__init__()
        self.onCheckSceneChange = Event.Event()
        self.onSpaceUpdated = Event.Event()
        self.hangarSpaceUpdated = False
        self.currentSceneName = DEFAULT_HANGAR_SCENE
        self._defaultHangars = {}
        self._sceneSpaceParams = {}
        self._defaultHangarSpaceConfig = DefaultHangarSpaceConfig()

    def init(self):
        self._readHangarSceneSpaceSettings()
        g_playerEvents.onEventNotificationsChanged += self._onEventNotificationsChanged

    def fini(self):
        g_playerEvents.onEventNotificationsChanged -= self._onEventNotificationsChanged

    def onLobbyInited(self, event):
        super(HangarSpaceSwitchController, self).onLobbyInited(event)
        self.startGlobalListening()
        if not self.hangarSpace.inited or self.hangarSpace.spaceLoading():
            self.hangarSpace.onSpaceCreate += self._delayedProcessChange
        else:
            self.processPossibleSceneChange()

    def onPrbEntitySwitched(self):
        self.processPossibleSceneChange()
        g_eventBus.handleEvent(events.HangarSpacesSwitcherEvent(events.HangarSpacesSwitcherEvent.SWITCH_TO_HANGAR_SPACE), scope=EVENT_BUS_SCOPE.LOBBY)

    def hangarSpaceUpdate(self, sceneName):
        if sceneName not in self._sceneSpaceParams:
            _logger.error('There is no space config for the key %s.', sceneName)
        if self.hangarSpaceUpdated and self.currentSceneName != sceneName:
            _logger.error('There is more than one component that requires space change is active!')
            return
        self.currentSceneName = sceneName
        self.hangarSpaceUpdated = True

    def onDisconnected(self):
        self._clear()
        super(HangarSpaceSwitchController, self).onDisconnected()

    def onAvatarBecomePlayer(self):
        self._clear()
        super(HangarSpaceSwitchController, self).onAvatarBecomePlayer()

    def _clear(self):
        self.stopGlobalListening()

    def _delayedProcessChange(self):
        self.hangarSpace.onSpaceCreate -= self._delayedProcessChange
        nextTick(self.processPossibleSceneChange)()

    def processPossibleSceneChange(self):
        self.hangarSpaceUpdated = False
        prevSceneName = self.currentSceneName
        self.onCheckSceneChange()
        success = None
        err = ErrorFlags.NONE
        if self.hangarSpaceUpdated:
            currentSceneConifg = self._sceneSpaceParams[self.currentSceneName]
            success, err = self.hangarSpaceReloader.changeHangarSpace(currentSceneConifg.getHangarSpaceId(), currentSceneConifg.getVisibilityMask(), currentSceneConifg.waitingMessage, currentSceneConifg.waitingBackground)
        else:
            self.currentSceneName = DEFAULT_HANGAR_SCENE
            hangarSpacePath = self._defaultHangarSpaceConfig.getHangarSpaceId(self.hangarSpace.isPremium)
            if hangarSpacePath != self.hangarSpaceReloader.hangarSpacePath:
                success, err = self.hangarSpaceReloader.changeHangarSpace(hangarSpacePath, self._defaultHangarSpaceConfig.getVisibilityMask(self.hangarSpace.isPremium))
        if success:
            self.hangarSpace.onSpaceCreate += self._onSpaceCreatedCallback
        elif err == ErrorFlags.DUPLICATE_REQUEST:
            self.onSpaceUpdated()
        elif err != ErrorFlags.NONE:
            self.currentSceneName = prevSceneName
            _logger.error('Could not perform space reload, see hangar_space_reloader.py error flag %d.', err)
        return

    def _onSpaceCreatedCallback(self):
        self.hangarSpace.onSpaceCreate -= self._onSpaceCreatedCallback
        self.onSpaceUpdated()

    def _readHangarSceneSpaceSettings(self):
        hangarsXml = ResMgr.openSection('gui/hangars.xml')
        if hangarsXml and hangarsXml.has_key('hangar_scene_spaces'):
            switchItems = hangarsXml['hangar_scene_spaces']
            for item in switchItems.values():
                name = item.readString('name')
                spaceId = item.readString('space')
                waitingMessage = item.readString('waitingMessage') or None
                waitingBackground = item.readString('waitingBackground') or None
                self._sceneSpaceParams[name] = SceneSpaceConfig(spaceId, waitingMessage, waitingBackground)

        return

    def _onEventNotificationsChanged(self, diff):
        currentSceneChanged = False
        currentSceneMaskChanged = False
        for notification in diff['removed']:
            if not notification['data']:
                continue
            if notification['type'] == SERVER_CMD_CHANGE_HANGAR_ALT:
                data = json.loads(notification['data'])
                name = data['name']
                sceneConfig = self._sceneSpaceParams.get(name)
                if sceneConfig is None:
                    _logger.error('Cannot remove space settings for not existing scene %s', name)
                    continue
                if 'hangar' in data:
                    sceneConfig.discardSpaceIdOverride()
                    sceneConfig.discardVisibilityMaskOverride()
                    if name == self.currentSceneName:
                        currentSceneChanged = True
                    continue
                if 'visibilityMask' in data:
                    sceneConfig.discardVisibilityMaskOverride()
                    if name == self.currentSceneName:
                        currentSceneMaskChanged = True
            if notification['type'] in (SERVER_CMD_CHANGE_HANGAR, SERVER_CMD_CHANGE_HANGAR_PREM):
                isPremium = notification['type'] == SERVER_CMD_CHANGE_HANGAR_PREM
                data = json.loads(notification['data'])
                if 'hangar' in data:
                    self._defaultHangarSpaceConfig.discardSpaceIdOverride(isPremium)
                    self._defaultHangarSpaceConfig.discardVisibilityMaskOverride(isPremium)
                    if DEFAULT_HANGAR_SCENE == self.currentSceneName:
                        currentSceneChanged = True
                    continue
                if 'visibilityMask' in data:
                    self._defaultHangarSpaceConfig.discardVisibilityMaskOverride(isPremium)
                    if DEFAULT_HANGAR_SCENE == self.currentSceneName:
                        currentSceneMaskChanged = True

        for notification in diff['added']:
            if not notification['data']:
                continue
            if notification['type'] == SERVER_CMD_CHANGE_HANGAR_ALT:
                data = json.loads(notification['data'])
                name = data['name']
                sceneConfig = self._sceneSpaceParams.get(name)
                if sceneConfig is None:
                    _logger.error('Cannot add space settings for not existing scene %s', name)
                    continue
                if 'hangar' in data:
                    sceneConfig.setSpaceIdOverride(data['hangar'])
                    if self.currentSceneName == name:
                        currentSceneChanged = True
                if 'visibilityMask' in data:
                    sceneConfig.setVisibilityMask(int(data['visibilityMask'], 16))
                    if self.currentSceneName == name:
                        currentSceneMaskChanged = True
            if notification['type'] in (SERVER_CMD_CHANGE_HANGAR, SERVER_CMD_CHANGE_HANGAR_PREM):
                isPremium = notification['type'] == SERVER_CMD_CHANGE_HANGAR_PREM
                try:
                    data = json.loads(notification['data'])
                    if 'hangar' in data:
                        self._defaultHangarSpaceConfig.setSpaceIdOverride(isPremium, data['hangar'])
                        if self.currentSceneName == DEFAULT_HANGAR_SCENE:
                            currentSceneChanged = True
                    if 'visibilityMask' in data:
                        self._defaultHangarSpaceConfig.setVisibilityMask(isPremium, int(data['visibilityMask'], 16))
                        if self.currentSceneName == DEFAULT_HANGAR_SCENE:
                            currentSceneMaskChanged = True
                except Exception:
                    self._defaultHangarSpaceConfig.setSpaceIdOverride(isPremium, notification['data'])
                    if self.currentSceneName == DEFAULT_HANGAR_SCENE:
                        currentSceneChanged = True

        if currentSceneChanged and self.hangarSpace.inited:
            if self.currentSceneName == DEFAULT_HANGAR_SCENE:
                spaceId = self._defaultHangarSpaceConfig.getHangarSpaceId(self.hangarSpace.isPremium)
                visibilityMask = self._defaultHangarSpaceConfig.getVisibilityMask(self.hangarSpace.isPremium)
                success, err = self.hangarSpaceReloader.changeHangarSpace(spaceId, visibilityMask)
            else:
                currentSceneConfig = self._sceneSpaceParams[self.currentSceneName]
                spaceId = currentSceneConfig.getHangarSpaceId()
                visibilityMask = currentSceneConfig.getVisibilityMask()
                success, err = self.hangarSpaceReloader.changeHangarSpace(spaceId, visibilityMask, currentSceneConfig.waitingMessage, currentSceneConfig.waitingBackground)
            if success:
                self.hangarSpace.onSpaceCreate += self._onSpaceCreatedCallback
            elif err == ErrorFlags.HANGAR_NOT_READY:
                if self.currentSceneName == DEFAULT_HANGAR_SCENE:
                    g_clientHangarSpaceOverride.setPath(spaceId, visibilityMask, isPremium=self.hangarSpace.isPremium, isReload=False)
                    spaceId = self._defaultHangarSpaceConfig.getHangarSpaceId(not self.hangarSpace.isPremium)
                    visibilityMask = self._defaultHangarSpaceConfig.getVisibilityMask(not self.hangarSpace.isPremium)
                    g_clientHangarSpaceOverride.setPath(spaceId, visibilityMask, isPremium=not self.hangarSpace.isPremium, isReload=False)
                else:
                    g_clientHangarSpaceOverride.setPath(spaceId, visibilityMask, isReload=False)
            elif err == ErrorFlags.DUPLICATE_REQUEST:
                _logger.warning('Redundant hangar update via event_notifications')
            else:
                raise SoftException('Could not perform space reload, see hangar_space_reloader.py error flag {}.'.format(err))
            return
        else:
            if currentSceneMaskChanged and self.hangarSpace.inited:
                if self.currentSceneName == DEFAULT_HANGAR_SCENE:
                    visibilityMask = self._defaultHangarSpaceConfig.getVisibilityMask(self.hangarSpace.isPremium)
                else:
                    visibilityMask = self._sceneSpaceParams[self.currentSceneName].getVisibilityMask()
                BigWorld.wg_setSpaceItemsVisibilityMask(self.hangarSpace.space.spaceId, visibilityMask)
            return
