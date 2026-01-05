#! /usr/bin/env python3

class Trainer:
    '''
    Represents a Pokémon trainer with their properties, party, items, and AI flags.
    '''
    def __init__(self, id):
        '''
        Initializes a Trainer with the given ID and default attributes.
        '''
        self.id = id

        self.name = 'TRAINER'
        self.trainer_class = 'TRAINER_CLASS_PKMN_TRAINER_1'
        self.trainer_pic = 'TRAINER_PIC_HIKER'
        self.encounter_music = 'TRAINER_ENCOUNTER_MUSIC_MALE'
        self.gender = 'MALE'
        self.double_battle = False
        self.items = []
        self.ai_flags = []
        self.pokemon = []
        self.party_name = ''
        self.maps = []
        self.difficulty_level = DifficultyLevel()
        self.party_size = 0 # This will be unused in vanilla projects


class Pokemon:
    '''
    Represents a Pokémon with its species, stats, moves, and other attributes.
    '''
    def __init__(self, species):
        '''
        Initializes a Pokémon with the given species and default stats and attributes.
        '''
        self.nickname = species[8:].capitalize()  # Remove 'SPECIES_' prefix for nickname
        self.evs = {'HP': 0, 'ATK': 0, 'DEF': 0, 'SPD': 0, 'SPATK': 0, 'SPDEF': 0}
        self.iv = 0
        self.ivs = {'HP': 0, 'ATK': 0, 'DEF': 0, 'SPD': 0, 'SPATK': 0, 'SPDEF': 0}
        self.moves = ['MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE']
        self.species = species
        self.held_item = 'ITEM_NONE'
        self.ability = 'ABILITY_NONE'
        self.level = 5
        self.ball = 'ITEM_POKE_BALL'
        self.friendship = 0
        self.nature = 'NATURE_HARDY'
        self.gender = 'TRAINER_MON_RANDOM_GENDER'
        self.is_shiny = False
        self.tera_type = 'TYPE_NORMAL' # Apparently not implemented yet
        self.gigantamax_factor = False
        self.use_dynamax = 1
        self.dynamax_lvl = 'MAX_DYNAMAX_LEVEL'


class SpeciesData:
    '''
    Represents a Pokémon species with its base stats.
    '''
    def __init__(self, species):
        self.species = species
        self.abilities = {'ABILITY_NONE', 'ABILITY_NONE', 'ABILITY_NONE'}


class AiFlagList:
    '''
    Stores a list of AI flags for trainers.
    '''
    def __init__(self):
        '''
        Initializes an empty list of AI flags.
        '''
        self.flags = []
    
    def add_flag(self, flag):
        '''
        Adds a flag to the list of AI flags.
        '''
        self.flags.append(flag)
    
    def clear_flags(self):
        '''
        Removes all flags from the list.
        '''
        self.flags = []
    
    def is_flag(self, checkflag):
        '''
        Checks if the given flag is present in the list.
        Returns True if found, False otherwise.
        '''
        for flag in self.flags:
            if checkflag == flag:
                return True
        return False
    

class DifficultyLevel:
    def __init__(self, current_level='DIFFICULTY_NORMAL'):
        self.levels = ['DIFFICULTY_EASY', 'DIFFICULTY_NORMAL', 'DIFFICULTY_HARD']
        self.current_level = current_level
    
    def get_level_length(self):
        return len(self.current_level)