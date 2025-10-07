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
        self.ai_flags = []
        self.pokemon = []
        self.party_name = ""
        self.maps = []


class Pokemon:
    def __init__(self, species):
        self.species = species

        self.level = 5
        self.held_item = "ITEM_NONE"
        self.moves = []
        self.iv = 0
        self.ivs = {"HP": 0, "ATK": 0, "DEF": 0, "SPD": 0, "SPATK": 0, "SPDEF": 0}
        self.evs = {"HP": 0, "ATK": 0, "DEF": 0, "SPD": 0, "SPATK": 0, "SPDEF": 0}
        self.nature = "NATURE_HARDY"
        self.ability = "ABILITY_NONE"

class AiFlagList:
    def __init__(self):
        self.flags = []
    
    def add_flag(self, flag):
        self.flags.append(flag)
    
    def clear_flags(self):
        self.flags = []
    
    def is_flag(self, checkflag):
        for flag in self.flags:
            if checkflag == flag:
                return True
        return False