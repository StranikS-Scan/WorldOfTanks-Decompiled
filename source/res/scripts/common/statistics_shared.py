# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/statistics_shared.py
# Compiled at: 2010-04-28 21:40:03
"""
Created on 23.04.2010

@author: vital
"""
from enumerations import Enumeration, AttributeEnumItem
CLIENT_STATISTIC_ARTICLES = Enumeration('client statistic articles', [('hangar', {}),
 ('inventory', {}),
 ('shop', {}),
 ('profile', {}),
 ('construction_department', {}),
 ('prebattle', {}),
 ('fitting', {}),
 ('messenger', {}),
 ('modules', {}),
 ('ammo_loader', {}),
 ('none', {'skipped': 1}),
 ('prev_state', {'skipped': 1}),
 ('login', {'skipped': 1})], instance=AttributeEnumItem)
