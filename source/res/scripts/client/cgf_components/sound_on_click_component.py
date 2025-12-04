# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/cgf_components/sound_on_click_component.py
import CGF
from Sound import Sound3DComponent
from cgf_components.hover_component import SelectionComponent
from debug_utils import LOG_ERROR
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent
from cgf_script.managers_registrator import autoregister, onAddedQuery, onRemovedQuery

@registerComponent
class SoundOnClickComponent(object):
    domain = CGF.DomainOption.DomainClient | CGF.DomainOption.DomainEditor
    editorTitle = 'Sound on click'
    category = 'Sound'
    stopActiveSound = ComponentProperty(type=CGFMetaTypes.BOOL, editorName='stop sound on next click', value=False)
    sound3DComponent = ComponentProperty(type=CGFMetaTypes.LINK, editorName='3D sound Component', value=Sound3DComponent)

    def clickAction(self):
        sound = self.sound3DComponent()
        if sound is None:
            return
        else:
            isPlaying = sound.isPlaying()
            sound.stop()
            if self.stopActiveSound and isPlaying:
                return
            sound.play()
            return


@autoregister(presentInAllWorlds=True)
class SoundOnClick(CGF.ComponentManager):

    @onAddedQuery(SoundOnClickComponent, SelectionComponent)
    def handleSoundsAdded(self, soundOnClickComponent, selectionComponent):
        if soundOnClickComponent.sound3DComponent() is None:
            LOG_ERROR('Added SoundOnClickComponent without configured sound')
            return
        else:
            selectionComponent.onClickAction += soundOnClickComponent.clickAction
            return

    @onRemovedQuery(SoundOnClickComponent, SelectionComponent)
    def handleSoundsRemoved(self, soundOnClickComponent, selectionComponent):
        sound = soundOnClickComponent.sound3DComponent()
        if sound is not None:
            sound.stop()
        selectionComponent.onClickAction -= soundOnClickComponent.clickAction
        return
