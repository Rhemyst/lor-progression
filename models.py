
import random

NB_CARDS = {
    'common': 150,
    'rare': 108,
    'epic': 36,
    'champ': 24
}

COSTS = {
    'common': 150,
    'rare': 400,
    'epic': 1500,
    'champ': 4000
}

DEZ = {
    'common': 25,
    'rare': 75,
    'epic': 300,
    'champ': 1000
}


class Collection:

    def __init__(self, region_reward):
        self.cards = {
            x:[0] * NB_CARDS[x] for x in NB_CARDS
        }
        self.shards = 0
        self.wildcards = {
            x:0 for x in NB_CARDS
        }
        self.region_level = [0,0,0,0,0,0]
        self.region_progressions = [0,0,0,0,0,0]
        self.current_region=0
        self.region_reward = region_reward

    def gain_item(self, item):
        if item.type == 'card':
            if item.rarity in ['common', 'rare']:
                card_id = random.randint(0, NB_CARDS[item.rarity] - 1)
                if self.cards[item.rarity][card_id] < 3:
                    self.cards[item.rarity][card_id] += 1
                else:
                    self.shards += DEZ[item.rarity]
            elif item.rarity in ['epic', 'champ']:
                if self.gain_non_duplicate_card(item.rarity):
                    pass
                else:
                    self.shards += DEZ[item.rarity]
            else:
                raise Exception('Unknown rarity')

        elif item.type == 'wildcard':
            self.wildcards[item.rarity] += 1

        elif item.type == 'shards':
            self.shards += item.qty
        
        else:
            raise Exception('Unknown type')


    def gain_reward(self, reward):
        for item in reward.open():
            self.gain_item(item)

    def has_complete_rarity(self, rarity):
        return sum(self.cards[rarity]) >= 3 * NB_CARDS[rarity]

    def gain_non_duplicate_card(self, rarity):
        for card_id in range(NB_CARDS[rarity]):
            if self.cards[rarity][card_id] < 3:
                self.cards[rarity][card_id] += 1
                return True
        return False

    def spend_wildcards(self, strategy='spend'):
        for rarity in ['epic', 'champ']:
            while self.wildcards[rarity] and not self.has_complete_rarity(rarity):
                self.gain_non_duplicate_card(rarity)
                self.wildcards[rarity] -= 1

        if strategy == 'wait':
            for rarity in ['common', 'rare']:
                if sum(self.cards[rarity]) + self.wildcards[rarity] >= NB_CARDS[rarity] * 3:
                    for card_id in range(NB_CARDS[rarity]):
                        self.wildcards[rarity] -= (3 - self.cards[rarity][card_id])
                        self.cards[rarity][card_id] = 3

        elif strategy == 'spend':
            for rarity in ['common', 'rare']:
                while self.wildcards[rarity] and not self.has_complete_rarity(rarity):
                    self.gain_non_duplicate_card(rarity)
                    self.wildcards[rarity] -= 1
        else:
            raise Exception('Unknown strat')

    def spend_shards(self, strategy='save'):
        if strategy == 'save':
            for rarity in ('champ', 'epic', 'rare', 'common'):
                while not self.has_complete_rarity(rarity):
                    if not self.shards >= COSTS[rarity]:
                        return
                    else:
                        self.shards -= COSTS[rarity]
                        self.gain_non_duplicate_card(rarity)
        else:
            for rarity in ('champ', 'epic', 'rare', 'common'):
                while not self.has_complete_rarity(rarity) and self.shards >= COSTS[rarity]:
                    self.shards -= COSTS[rarity]
                    self.gain_non_duplicate_card(rarity)


    def get_completion(self):
        return [sum(self.cards[rarity]) / (3*NB_CARDS[rarity]) for rarity in ['common', 'rare', 'epic', 'champ']]

    def get_global_completion(self):
        return sum(sum(self.cards[r]) for r in self.cards) / (3 * sum(NB_CARDS[r] for r in NB_CARDS))

    def get_nb_cards(self):
        return [sum(self.cards[rarity]) for rarity in ['common', 'rare', 'epic', 'champ']]

    def gain_region_reward(self, level):
        self.gain_reward(self.region_reward[level])

    def gain_xp(self, xp):
        # Gain some XP and progress on region path
        # No complex strategy here: we just level each region to level 20 before starting the next one.
        if xp>250:
            self.gain_xp(250)
            self.gain_xp(xp-250)
            return
        if self.current_region == 6:
            return
        self.region_progressions[self.current_region]+=xp
        thresh = (self.region_level[self.current_region]+1)*250
        if self.region_progressions[self.current_region] >= thresh:
            self.gain_region_reward(self.region_level[self.current_region])
            self.region_level[self.current_region]+=1
            self.region_progressions[self.current_region]-=thresh

            if self.region_level[self.current_region] == 20:
                x=self.region_progressions[self.current_region]
                self.region_progressions[self.current_region]=0
                self.current_region += 1
                if self.current_region < 6:
                    self.region_level[self.current_region] = 0
                    self.region_progressions[self.current_region]=x




