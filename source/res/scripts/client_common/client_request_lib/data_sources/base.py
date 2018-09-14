# Embedded file name: scripts/client_common/client_request_lib/data_sources/base.py
"""
Created on Jul 1, 2015

@author: oleg
"""
from abc import ABCMeta, abstractmethod
__all__ = ('BaseDataAccessor',)

class BaseDataAccessor(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def login(self, callback, account_id, token):
        pass

    @abstractmethod
    def logout(self, callback):
        pass

    @abstractmethod
    def get_clans_ratings(self, callback, clan_ids, fields = None):
        """
        return clan rating info as dict with possible keys:
        
                - efficiency
                - elo_10
                - elo_10_rank
                - elo_8
                - elo_8_rank
                - elo_6
                - elo_6_rank
                - battles_count_avg
                - wins_ratio_avg
        """
        pass

    @abstractmethod
    def get_accounts_names(self, callback, account_ids):
        """
        return accounts info as list of dicts with possible keys:
        
                - account_id
                - name
        """
        pass

    @abstractmethod
    def get_clan_invites(self, callback, clan_id, fields = None, statuses = None, offset = 0, limit = 18):
        """
        return clan invites as dict with 'items' value as dict with possible keys:
        
                - status
                - created_at
                - updated_at
                - sender_id
                - id
                - account_id
                - clan_id
                - comment
        
        total count of records can be requested using 'total' field passed
        """
        pass

    @abstractmethod
    def get_account_invites(self, callback, account_id, fields = None, statuses = None, offset = 0, limit = 18):
        """
        return clan invites as dict with 'items' value as dict with possible keys:
        
                - status
                - created_at
                - updated_at
                - sender_id
                - id
                - account_id
                - clan_id
                - comment
        
        total count of records can be requested using 'total' field passed
        """
        pass

    @abstractmethod
    def get_account_applications_count_since(self, callback, account_id, since = None):
        """
        return account applications count created since passed date, returned as dict:
        
                - total
        """
        pass

    @abstractmethod
    def get_clan_invites_count_since(self, callback, clan_id, since = None):
        """
        return clan invitation count created since passed date, returned as dict:
        
                - total
        """
        pass

    @abstractmethod
    def get_clan_applications(self, callback, clan_id, fields = None, statuses = None, offset = 0, limit = 18):
        """
        return clan applications as dict with 'items' value as dict with possible keys:
        
                - status
                - created_at
                - updated_at
                - sender_id
                - id
                - account_id
                - clan_id
                - comment
        
        total count of records can be requested using 'total' field passed
        """
        pass

    @abstractmethod
    def search_clans(self, callback, search, get_total_count = False, fields = None, offset = 0, limit = 18):
        """
        return clan applications as dict with 'items' value as dict with possible keys:
        
                - name
                - tag
                - motto
                - emblems
                - members_count
        
        total count of records can be requested using 'total' field passed
        """
        pass

    @abstractmethod
    def get_clans_info(self, callback, clan_ids, fields = None):
        """
        return clan info as dict with possible keys:
        
                - name
                - tag
                - motto
                - members_count
                - created_at
                - leader_id
        """
        pass

    @abstractmethod
    def get_clan_members(self, callback, clan_id, fields = None):
        """
        return clan info as dict with possible keys:
        
                - account_id
                - role
                - days_in_the_clan
        """
        pass

    @abstractmethod
    def get_clan_favorite_attributes(self, callback, clan_id, fields = None):
        """
        return clans favorite_arena and favorite_primetime as dict with possible keys:
        
                - clan_id
                - favorite_arena
                - favorite_primetime
        """
        pass

    @abstractmethod
    def get_accounts_clans(self, callback, account_ids, fields = None):
        """
        return clan info as dict with possible keys:"clan_id": 4727,
        
                - clan_id
                - role_bw_flag
                - role_name
                - account_id
        """
        pass

    @abstractmethod
    def get_accounts_info(self, callback, account_ids, fields = None):
        """
        return accounts info as list of dicts with possible keys:
        
                - global_rating
                - battle_avg_xp
                - battles_count
                - battle_avg_performance
                - xp_amount
        """
        pass

    @abstractmethod
    def get_clan_provinces(self, callback, clan_id, fields = None):
        """
        return clan provinces info as list of dicts with possible keys:
        
                - front_name
                - province_id
                - revenue
                - hq_connected
                - prime_time
                - game_map
                - turns_owned
        """
        pass

    @abstractmethod
    def get_clan_globalmap_stats(self, callback, clan_id, fields = None):
        """
        return clan statistic info as dict with possible keys:
        
                - battles_lost
                - influence_points
                - provinces_captured
                - battles_played
                - battles_won
                - battles_played_on_6_level
                - battles_won_on_6_level
                - battles_played_on_8_level
                - battles_won_on_8_level
                - battles_played_on_10_level
                - battles_won_on_10_level
        """
        pass

    @abstractmethod
    def get_fronts_info(self, callback, front_names = None, fields = None):
        """
        return fronts info as list of dicts with possible keys:
        
                - id
                - min_vehicle_level
                - max_vehicle_level
        """
        pass

    @abstractmethod
    def get_stronghold_info(self, callback, clan_id = None, fields = None):
        """
        return stronghold info as dict with possible keys:
        
                - sortie_battles_count
                - sortie_wins
                - defence_battles_count
                - defence_combat_wins
                - sortie_middle_battles_count
                - sortie_champion_battles_count
                - sortie_absolute_battles_count
                - defence_enemy_base_capture_count
                - defence_capture_enemy_building_total_count
                - defence_loss_own_building_total_count
                - defence_attack_efficiency
                - defence_defence_efficiency
                - total_resource_amount
                - defence_resource_loss_count
                - defence_resource_capture_count
        """
        pass

    @abstractmethod
    def get_strongholds_statistics(self, callback, clan_id, fields = None):
        """
        return stronghold statistics info as dict with possible keys:
        
                - buildings_count
                - directions_count
                - buildings
                - directions
                - off_day
                - vacation_start
                - vacation_finish
                - periphery_id
                - clan_tag
                - clan_name
                - clan_id
                - sortie_wins_period
                - sortie_battles_wins_percentage_period
        """
        pass

    @abstractmethod
    def get_strongholds_state(self, callback, clan_id, fields = None):
        """
        return stronghold statistics info as dict with possible keys:
        
                - clan_id
                - defence_hour
        """
        pass
