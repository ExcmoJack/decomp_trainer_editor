#! /usr/bin/env python3

class Trainer:
    def __init__(self, id):
        self.id = id

        self.name = "TRAINER"
        self.trainer_class = "TRAINER_CLASS_PKMN_TRAINER_1"
        self.trainer_pic = "TRAINER_PIC_HIKER"
        self.encounter_music = "TRAINER_ENCOUNTER_MUSIC_MALE"
        self.gender = "MALE"
        self.double_battle = False
        self.items = []
        self.ai_flags = AiFlags()
        self.pokemon = []
        self.maps = []


class Pokemon:
    def __init__(self, species):
        self.species = species

        self.level = 5
        self.held_item = "ITEM_NONE"
        self.moves = []
        self.ivs = {"HP": 0, "ATK": 0, "DEF": 0, "SPD": 0, "SPATK": 0, "SPDEF": 0}
        self.evs = {"HP": 0, "ATK": 0, "DEF": 0, "SPD": 0, "SPATK": 0, "SPDEF": 0}
        self.nature = "NATURE_HARDY"
        self.ability = "ABILITY_NONE"

class AiFlags:
    def __init__(self):
        self.AI_FLAG_CHECK_BAD_MOVE = False
        self.AI_FLAG_TRY_TO_FAINT = False
        self.AI_FLAG_CHECK_VIABILITY = False
        self.AI_FLAG_FORCE_SETUP_FIRST_TURN = False
        self.AI_FLAG_RISKY = False
        self.AI_FLAG_TRY_TO_2HKO = False
        self.AI_FLAG_PREFER_BATON_PASS = False
        self.AI_FLAG_DOUBLE_BATTLE = False
        self.AI_FLAG_HP_AWARE = False
        self.AI_FLAG_POWERFUL_STATUS = False
        self.AI_FLAG_NEGATE_UNAWARE = False
        self.AI_FLAG_WILL_SUICIDE = False
        self.AI_FLAG_PREFER_STATUS_MOVES = False
        self.AI_FLAG_STALL = False
        self.AI_FLAG_SMART_SWITCHING = False
        self.AI_FLAG_ACE_POKEMON = False
        self.AI_FLAG_OMNISCIENT = False
        self.AI_FLAG_SMART_MON_CHOICES = False
        self.AI_FLAG_CONSERVATIVE = False
        self.AI_FLAG_SEQUENCE_SWITCHING = False
        self.AI_FLAG_DOUBLE_ACE_POKEMON = False
        self.AI_FLAG_WEIGH_ABILITY_PREDICTION = False
        self.AI_FLAG_PREFER_HIGHEST_DAMAGE_MOVE = False
        self.AI_FLAG_PREDICT_SWITCH = False
        self.AI_FLAG_PREDICT_INCOMING_MON = False