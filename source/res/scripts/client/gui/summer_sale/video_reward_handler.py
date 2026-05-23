# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/summer_sale/video_reward_handler.py
from functools import partial
from ExtensionsManager import g_extensionsManager
from gui.impl.lobby.loot_box.sound_control import VideoRewardsSoundControl
from gui.server_events.events_dispatcher import showSummerSaleRewardView
if g_extensionsManager.isExtensionEnabled('gui_lootboxes'):
    from gui_lootboxes.gui.impl.lobby.gui_lootboxes.common_video_reward import CommonUniqueRewardHandler, FakeGUILootbox

    class SummerSaleSoundControl(VideoRewardsSoundControl):
        LOOTBOXES_REWARD_VIDEO_START = 'summer_sale_video_start_01'
        LOOTBOXES_REWARD_VIDEO_STOP = 'summer_sale_video_stop'
        LOOTBOXES_REWARD_VIDEO_PAUSE = 'summer_sale_video_pause'
        LOOTBOXES_REWARD_VIDEO_RESUME = 'summer_sale_video_resume'


    class SummerSaleVideoHandler(CommonUniqueRewardHandler):

        def getVideoRewarsdSoundControl(self):
            return SummerSaleSoundControl


    def tryShowWithVideoReward(rewards, lootBox=None, summerSale=None):
        if lootBox is None:
            lootBox = FakeGUILootbox('common')
        handler = SummerSaleVideoHandler.createHandler(rewards, lootBox)
        if handler:
            handler.showRewardsWindow(None, closeCallback=partial(showSummerSaleRewardView, rewards))
        else:
            showSummerSaleRewardView(rewards)
        return


else:

    def tryShowWithVideoReward(rewards, closeCallbac, lootBox=None, summerSale=None):
        showSummerSaleRewardView(rewards)
