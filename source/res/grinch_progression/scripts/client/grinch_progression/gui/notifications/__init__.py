# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/notifications/__init__.py
from gui.shared.system_factory import registerGamefaceNotifications
from gui.impl.gen import R

def registerGPNotifications():
    from grinch_progression.gui.impl.lobby.notifications.gp_style_reward import GpStyleReward
    gpStyleReward = (R.views.grinch_progression.lobby.notifications.GpStyleReward(), GpStyleReward)
    registerGamefaceNotifications({'GpStyleReward': gpStyleReward})
