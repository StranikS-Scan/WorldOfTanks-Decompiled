# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/challenges/__init__.py
from __future__ import absolute_import
from gui.impl.gen import R
from gui.impl.lobby.challenges.notifications.challenges_challenge_completed_notification import ChallengesChallengeCompletedNotification
from gui.impl.lobby.challenges.notifications.challenges_fail_notification import ChallengesFailNotification
from gui.impl.lobby.challenges.notifications.challenges_mission_completed_notification import ChallengesMissionCompletedNotification
from gui.impl.lobby.challenges.notifications.challenges_shield_used_notification import ChallengesShieldUsedNotification
from gui.impl.lobby.challenges.notifications.challenges_start_notification import ChallengesStartNotification
from gui.impl.lobby.gf_notifications import GFNotificationTemplates
from gui.shared.system_factory import registerGamefaceNotifications
registerGamefaceNotifications({GFNotificationTemplates.CHALLENGES_FAIL_NOTIFICATION: (R.views.mono.user_missions.notifications.fail_notification(), ChallengesFailNotification),
 GFNotificationTemplates.CHALLENGES_SHIELD_USED_NOTIFICATION: (R.views.mono.user_missions.notifications.shield_notification(), ChallengesShieldUsedNotification),
 GFNotificationTemplates.CHALLENGES_START_NOTIFICATION: (R.views.mono.user_missions.notifications.start_notification(), ChallengesStartNotification),
 GFNotificationTemplates.CHALLENGES_MISSION_COMPLETED_NOTIFICATION: (R.views.mono.user_missions.notifications.mission_complete_notification(), ChallengesMissionCompletedNotification),
 GFNotificationTemplates.CHALLENGES_CHALLENGE_COMPLETED_NOTIFICATION: (R.views.mono.user_missions.notifications.complete_notification(), ChallengesChallengeCompletedNotification)})
