# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/gui/game_control/__init__.py
from gui.shared.system_factory import registerGameControllers
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController
from one_time_gift.gui.game_control.one_time_gift_controller import OneTimeGiftController

def registerOneTimeGiftController():
    registerGameControllers([(IOneTimeGiftController, OneTimeGiftController, False)])
