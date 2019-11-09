from rewards import *
import numpy as np

# Main script simulating progression.

## PARAMETERS ##
# The vault level reached each week
vault_level_per_week = 10
# The list of wildcards bought each week.
wildcards_per_week = 0*[ChampWildcardReward(), EpicWildcardReward()]
# total number of weeks to simulated
nb_weeks = 16
# Initial Content of the collection
starter = [] # empty start
#starter = [common_card]*6*6 + [rare_card]*4*6 + [epic_card]*6 # Starter kit
# TODO content of the prologue path ?

total_stats = []
for runs in range(100):

    # Create a new collection
    coll = Collection(REGION_REWARDS_ORDERED)
    stats = []

    # Initialize collection content.
    for item in starter:
        coll.gain_item(item)

    # Simulate n weeks...
    for week in range(nb_weeks):

        # Each week, we get a certain amount of xp to reach a set vault level
        xp = VAULT_REWARD[vault_level_per_week-1]['xp']
        vault_reward = VAULT_REWARD[vault_level_per_week-1]['reward']
        # Add XP to collection, which will trigger region rewards as well
        coll.gain_xp(xp)
        # Then gain the vault rewards and the wildcards we bought.
        for reward in vault_reward + wildcards_per_week:
            coll.gain_reward(reward)
        # Finally, each week we spent our shards and wildcard.
        # We could save those, but let's assume we want to play, not ONLY grind.
        coll.spend_shards()
        coll.spend_wildcards()
        # Compute the global and by-rarity completion
        stats.append([coll.get_global_completion()]+coll.get_completion())
    total_stats.append(stats)

# Convert to numpy for easier manipulation and plot TODO
a = np.array(total_stats)
m = np.floor(np.mean(a,0)*100)

# Only show set completion every month
print(m[3,0], m[7,0], m[11,0], m[15,0])
