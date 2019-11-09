from models import *

# Probabilities of upgrade.
# Provided by Riot, but subject to change
CARD_RARITY_UPGRADE = 0.1
NONCHAMP_CARD_WILDCARD_UPGRAGE = 0.1
CHAMP_CARD_WILDCARD_UPGRAGE = 0.05
WILDCARD_UPGRADE = 0.1

CAPSULE_WILDCAPSULE_UPGRADE = 0.05
CAPSULE_EPICCAPSULE_UPGRADE = 0.1
EPICCAPSULE_CHAMPCAPSULE_UPGRADE = 0.1

CHEST_UPGRADE = 0.2

# This class represent an item in the collection : card, wildcard, or shards.
class Item:
    def __init__(self, type, rarity, qty=1):
        self.type = type
        self.rarity = rarity
        self.qty = qty # only used for shard.

# Shortcuts for all the cards and wildcards items.
common_card = Item('card', 'common')
rare_card = Item('card', 'rare')
epic_card = Item('card', 'epic')
champ_card = Item('card', 'champ')

common_wildcard = Item('wildcard', 'common')
rare_wildcard = Item('wildcard', 'rare')
epic_wildcard = Item('wildcard', 'epic')
champ_wildcard = Item('wildcard', 'champ')


# This class represent a reward. Rewards can be :
#   - cards
#   - wildcards
#   - Capsules
#   - Chests
# All rewards, when opened, have a chance to upgrade to something better.
class Reward:

    # Content of the reward (can be items or other rewards)
    content = []
    # List of possible upgrades for that reward, with probabilities to upgrade.
    possible_upgrades = []

    def open(self):
        # When opened, reward has a random chance to update
        for up in self.possible_upgrades:
            rng = random.random()
            if rng < up['prob']:
                return up['reward'].open()
        # If the reward didn't update, we return its regular content.
        r = []
        for element in self.content:
            if isinstance(element, Item):
                r.append(element)
            elif isinstance(element, Reward):
                # It the reward contain other rewards,
                # open then and add the content to the list.
                r.extend(element.open())
            else:
                raise Exception('Unknown element {}'.format(element))
        return r


# Declaration of ALL the rewards
# Note that we make the distinction between a card as an item and a card as a reward
# A card as a Reward has a chance to upgrade to another reward
# A card as an Item cant upgrade. It's just added to the collection.
class ChampWildcardReward(Reward):
    content = [champ_wildcard]
    possible_upgrades = []

class EpicWildcardReward(Reward):
    content = [epic_wildcard]
    possible_upgrades = [
        {'prob': WILDCARD_UPGRADE, 'reward': ChampWildcardReward()}
    ]

class RareWildcardReward(Reward):
    content = [rare_wildcard]
    possible_upgrades = [
        {'prob': WILDCARD_UPGRADE, 'reward': EpicWildcardReward()}
    ]

class CommonWildcardReward(Reward):
    content = [common_wildcard]
    possible_upgrades = [
        {'prob': WILDCARD_UPGRADE, 'reward': RareWildcardReward()}
    ]

class ChampCardReward(Reward):
    content = [champ_card]
    possible_upgrades = [
        {'prob': CHAMP_CARD_WILDCARD_UPGRAGE, 'reward': ChampWildcardReward()}
    ]

class EpicCardReward(Reward):
    content = [epic_card]
    possible_upgrades = [
        {'prob': CARD_RARITY_UPGRADE, 'reward': ChampCardReward()},
        {'prob': NONCHAMP_CARD_WILDCARD_UPGRAGE, 'reward': EpicWildcardReward()}
    ]

class RareCardReward(Reward):
    content = [rare_card]
    possible_upgrades = [
        {'prob': CARD_RARITY_UPGRADE, 'reward': EpicCardReward()},
        {'prob': NONCHAMP_CARD_WILDCARD_UPGRAGE, 'reward': RareWildcardReward()}
    ]

class CommonCardReward(Reward):
    content = [common_card]
    possible_upgrades = [
        {'prob': CARD_RARITY_UPGRADE, 'reward': RareCardReward()},
        {'prob': NONCHAMP_CARD_WILDCARD_UPGRAGE, 'reward': CommonWildcardReward()}
    ]

class WildCapsule(Reward):
    content = 4*[common_wildcard] + [rare_wildcard]

class ChampionCapsule(Reward):
    content = [RareCardReward(), RareCardReward(), RareCardReward()] + [EpicCardReward(), ChampCardReward()]

class EpicCapsule(Reward):
    content = [CommonCardReward(), CommonCardReward()] + [RareCardReward(), RareCardReward()] + [EpicCardReward()]
    possible_upgrades = [
        {'prob': EPICCAPSULE_CHAMPCAPSULE_UPGRADE, 'reward': ChampionCapsule()},
    ]

class Capsule(Reward):
    content = [CommonCardReward(), CommonCardReward(), CommonCardReward(), CommonCardReward()] + [RareCardReward()]
    possible_upgrades = [
        {'prob': CAPSULE_EPICCAPSULE_UPGRADE, 'reward': EpicCapsule()},
    ]

class DiamondChest(Reward):
    content = [Capsule(), Capsule(), Capsule()] + [Item('shards','',800)]

class PlatinumChest(Reward):
    content = [Capsule(), Capsule()] + [Item('shards','',560)]
    possible_upgrades = [
        {'prob': CHEST_UPGRADE, 'reward': DiamondChest()},
    ]

class GoldChest(Reward):
    content = [Capsule()] + [Item('shards','',360)]
    possible_upgrades = [
        {'prob': CHEST_UPGRADE, 'reward': PlatinumChest()},
    ]

class SilverChest(Reward):
    content = [CommonCardReward(), CommonCardReward(), RareCardReward()] + [Item('shards','',200)]
    possible_upgrades = [
        {'prob': CHEST_UPGRADE, 'reward': GoldChest()},
    ]

class BronzeChest(Reward):
    content = [CommonCardReward(), CommonCardReward()] + [Item('shards','',80)]
    possible_upgrades = [
        {'prob': CHEST_UPGRADE, 'reward': SilverChest()},
    ]

# List of vault levels / rewards
VAULT_REWARD=[
    {'xp':0, 'reward': [BronzeChest(), BronzeChest(), BronzeChest()]},
    {'xp':1000, 'reward': [BronzeChest(), BronzeChest(), SilverChest()]},
    {'xp':2000, 'reward': [BronzeChest(), SilverChest(), SilverChest()]},
    {'xp':3000, 'reward': [BronzeChest(), SilverChest(), GoldChest()]},
    {'xp':4000, 'reward': [SilverChest(), SilverChest(), GoldChest()]},
    {'xp':5000, 'reward': [SilverChest(), GoldChest(), GoldChest()]},
    {'xp':7000, 'reward': [GoldChest(), GoldChest(), GoldChest()]},
    {'xp':9000, 'reward': [GoldChest(), GoldChest(), PlatinumChest()]},
    {'xp':11000, 'reward': [GoldChest(), PlatinumChest(), PlatinumChest()]},
    {'xp':13000, 'reward': [PlatinumChest(), PlatinumChest(), PlatinumChest(), ChampWildcardReward()]},
    {'xp':17000, 'reward': [PlatinumChest(), PlatinumChest(), DiamondChest(), ChampWildcardReward()]},
    {'xp':21000, 'reward': [PlatinumChest(), DiamondChest(), DiamondChest(), ChampWildcardReward()]},
    {'xp':25000, 'reward': [DiamondChest(), DiamondChest(), DiamondChest(), ChampWildcardReward()]},
]

# List of region rewards.
# The order here is by value, this is not the actual order ingame.
REGION_REWARDS_ORDERED=[
    RareWildcardReward(),
    EpicWildcardReward(),
    ChampWildcardReward(),
    EpicCardReward(),
    EpicCardReward(),
    BronzeChest(),
    SilverChest(),
    GoldChest(),
    GoldChest(),
    PlatinumChest(),
    PlatinumChest(),
    DiamondChest(),
    Capsule(),
    Capsule(),
    WildCapsule(),
    WildCapsule(),
    EpicCapsule(),
    EpicCapsule(),
    ChampionCapsule(),
    ChampionCapsule(),
]