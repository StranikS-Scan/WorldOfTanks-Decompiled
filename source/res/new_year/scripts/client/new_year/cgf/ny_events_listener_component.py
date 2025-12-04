# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/cgf/ny_events_listener_component.py
import CGF
from cgf_script.component_meta_class import registerComponent, ComponentProperty, CGFMetaTypes
from new_year.skeletons.new_year import INewYearController
from skeletons.gui.game_control import IPlatoonController
from PlayerEvents import g_playerEvents
from Sound import Sound3DComponent
from constants import IS_EDITOR
from helpers import dependency
if not IS_EDITOR:
    from new_year.gui.impl.new_year.sounds import NewYearCelebVoiceOvers
    from new_year.gui.shared.ny_level_helper import parseNYLevelToken
    from messenger.proto.events import g_messengerEvents
    from chat_shared import SYS_MESSAGE_TYPE
    from new_year_common.items.components.ny_constants import MAX_ATMOSPHERE_LVL

@registerComponent
class NyEventsListenerComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'NY Actions Listener'
    category = 'New Year'
    fightSound = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Fight 3D Sound Component', value=Sound3DComponent)
    atmSoundHandler = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Atmosphere Sound Handler', value=CGF.GameObject)

    def playFightSound(self):
        sound = self.fightSound()
        if sound is None or sound.isPlaying():
            return
        else:
            sound.play()
            return

    def playAtmosphereSound(self, soundEvent):
        soundComp = self.atmSoundHandler.findComponentByType(Sound3DComponent)
        if soundComp is not None:
            if soundComp.isPlaying():
                soundComp.stop()
            self.atmSoundHandler.removeComponent(soundComp)
        self.atmSoundHandler.createComponent(Sound3DComponent, '', soundEvent, True)
        return


class NewYearEventsListenerManager(CGF.ComponentManager):
    __platoonController = dependency.descriptor(IPlatoonController)
    __newYearController = dependency.descriptor(INewYearController)

    def __init__(self, *args):
        super(NewYearEventsListenerManager, self).__init__(*args)
        self.__wasInQueue = False
        self.__wasInSearch = False

    def activate(self):
        self.__snapshotPlatoonState(self.__platoonController.isInQueue(), self.__platoonController.isInSearch())
        g_playerEvents.onEnqueued += self.__onSingleFightClick
        self.__platoonController.onMembersUpdate += self.__onPlatoonMembersUpdate
        if not self.__newYearController.isMaxAtmosphereLevel():
            g_messengerEvents.serviceChannel.onChatMessageReceived += self.__onServiceMsg

    def deactivate(self):
        g_playerEvents.onEnqueued -= self.__onSingleFightClick
        self.__platoonController.onMembersUpdate -= self.__onPlatoonMembersUpdate
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__onServiceMsg

    def __broadcastFightSound(self):
        for listener in CGF.Query(self.spaceID, NyEventsListenerComponent):
            listener.playFightSound()

    def __onSingleFightClick(self, *_):
        if not self.__newYearController.isCelebVoiceoverEnabled():
            return
        self.__broadcastFightSound()

    def __onPlatoonMembersUpdate(self, *_):
        if not self.__newYearController.isCelebVoiceoverEnabled():
            return
        nowInQueue = self.__platoonController.isInQueue()
        nowInSearch = self.__platoonController.isInSearch()
        isFightClicked = not self.__wasInQueue and nowInQueue or not self.__wasInSearch and nowInSearch
        if isFightClicked:
            self.__broadcastFightSound()
        self.__snapshotPlatoonState(nowInQueue, nowInSearch)

    def __snapshotPlatoonState(self, inQueue, inSearch):
        self.__wasInQueue = inQueue
        self.__wasInSearch = inSearch

    def __onServiceMsg(self, clientID, message):
        if message is None or not message.data:
            return
        elif message.type != SYS_MESSAGE_TYPE.tokenQuests.index():
            return
        elif not self.__newYearController.isCelebVoiceoverEnabled():
            return
        else:
            completedQuestIDs = message.data.get('completedQuestIDs', ())
            for questID in completedQuestIDs:
                level = parseNYLevelToken(questID)
                if level not in NewYearCelebVoiceOvers.ENABLE_SOUND_RANGE:
                    continue
                if level == MAX_ATMOSPHERE_LVL:
                    g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__onServiceMsg
                    soundEvent = NewYearCelebVoiceOvers.LAST_LEVEL_UP
                else:
                    soundEvent = NewYearCelebVoiceOvers.FIRST_LEVEL_UP
                for listener in CGF.Query(self.spaceID, NyEventsListenerComponent):
                    listener.playAtmosphereSound(soundEvent)

            return
