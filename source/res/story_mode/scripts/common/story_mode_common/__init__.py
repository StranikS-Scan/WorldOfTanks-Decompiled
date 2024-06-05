# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/common/story_mode_common/__init__.py


def injectConsts(personality):
    import constants
    from story_mode_common.configs.story_mode_missions import missionsSchema
    from story_mode_common.configs.story_mode_settings import settingsSchema
    from story_mode_common.configs.story_mode_battle_mgr_quotums import quotumsSchema
    constants.INBATTLE_CONFIGS.append(settingsSchema.gpKey)
    constants.INBATTLE_CONFIGS.append(missionsSchema.gpKey)
    constants.INBATTLE_CONFIGS.append(quotumsSchema.gpKey)
