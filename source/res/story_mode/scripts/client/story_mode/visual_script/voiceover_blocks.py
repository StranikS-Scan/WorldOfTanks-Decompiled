# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/visual_script/voiceover_blocks.py
from visual_script.block import Block
from visual_script.slot_types import SLOT_TYPE
from visual_script_client.sound_blocks import SoundMeta

class PlayVoiceover(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(PlayVoiceover, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._vehicle = self._makeDataInputSlot('vehicle', SLOT_TYPE.VEHICLE)
        self._voiceover = self._makeDataInputSlot('voiceover', SLOT_TYPE.STR)
        self._delay = self._makeDataInputSlot('delay', SLOT_TYPE.FLOAT)
        self._out = self._makeEventOutputSlot('out')
        self._finished = self._makeEventOutputSlot('finished')

    def validate(self):
        return 'Voiceover value is required' if not self._voiceover.hasValue() else super(PlayVoiceover, self).validate()

    def _execute(self):
        if self._voiceover.hasValue():
            from helpers import dependency
            from story_mode.skeletons.voiceover_controller import IVoiceoverManager
            manager = dependency.instance(IVoiceoverManager)
            ctx = {'onEnd': self._finished.call}
            if self._vehicle.hasValue():
                ctx['vehicleId'] = self._vehicle.getValue().id
            if not self._delay.hasValue() or self._delay.getValue() <= 0.0:
                delay = None
            else:
                delay = self._delay.getValue()
            manager.playVoiceover(voiceoverId=self._voiceover.getValue(), ctx=ctx, delay=delay)
        self._out.call()
        return


class StopVoiceover(Block, SoundMeta):

    def __init__(self, *args, **kwargs):
        super(StopVoiceover, self).__init__(*args, **kwargs)
        self._in = self._makeEventInputSlot('in', self._execute)
        self._out = self._makeEventOutputSlot('out')

    def _execute(self):
        from helpers import dependency
        from story_mode.skeletons.voiceover_controller import IVoiceoverManager
        manager = dependency.instance(IVoiceoverManager)
        manager.stopVoiceover()
        self._out.call()
