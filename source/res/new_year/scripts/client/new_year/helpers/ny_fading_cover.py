# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/helpers/ny_fading_cover.py
from helpers import dependency
from gui.impl.common.fade_manager import DefaultFadingCover
from new_year.skeletons.new_year import IRaccoonAnimationController

class NYFadingCover(DefaultFadingCover):
    __raccoonCtrl = dependency.descriptor(IRaccoonAnimationController)
    _FADE_IN_DURATION = 0.15
    _FADE_OUT_DURATION = 0.15

    def __init__(self):
        super(NYFadingCover, self).__init__(fadeInDuration=self._FADE_IN_DURATION, fadeOutDuration=self._FADE_OUT_DURATION)
