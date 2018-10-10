# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/live_crc_accountdata.py
from live_crc import *
accountPersistentCacheDataScheme = {INCLUDE: {'economics',
           'inventory',
           'quests',
           'tokens',
           'potapovQuests',
           'intUserSettings'},
 'stats': {INCLUDE: {'dossier',
                     'eliteVehicles',
                     'unlocks',
                     'vehTypeXP'}}}
accountDataPersistentHash = gen_livehash_fn(accountPersistentCacheDataScheme)
accountDataDelPersistent = gen_delSubkeys_fn(accountPersistentCacheDataScheme)
accountDataMergePersistent = gen_mergeCache_fn(overwrite=False)
accountDataExtractPersistent = gen_extract_fn(accountPersistentCacheDataScheme)

def accountDataGetDiffForPersistent(diff):
    good_keys = {'economics',
     'inventory',
     'stats',
     'quests',
     'tokens',
     'potapovQuests',
     'intUserSettings'}
    mydiff = {}
    for k, v in diff.items():
        if k in good_keys or isinstance(k, tuple) and k[0] in good_keys:
            mydiff[k] = v

    return mydiff
