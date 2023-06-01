# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/resources/cdn/types.py
import typing
from gui.game_loading.resources.cdn.models import ConfigSequenceModel, ConfigSlideModel, LocalSlideModel, LocalSequenceModel
SequenceType = typing.Union[ConfigSequenceModel, LocalSequenceModel]
SlideType = typing.Union[ConfigSlideModel, LocalSlideModel]
