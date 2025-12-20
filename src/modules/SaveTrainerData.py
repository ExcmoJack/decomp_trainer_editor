import os
import datetime

INITIAL_FILE_CONTENT = \
{
    'pokeruby': \
        'const struct Trainer gTrainers[] = {\n'
        '    [TRAINER_NONE] =\n' +
        '    {\n' +
        '        .partyFlags = 0,\n' +
        '        .trainerClass = TRAINER_CLASS_POKEMON_TRAINER_1,\n' +
        '        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_MALE,\n' +
        '        .trainerPic = TRAINER_PIC_BRENDAN,\n' +
        '        .trainerName = _(""),\n' +
        '        .items = {ITEM_NONE, ITEM_NONE, ITEM_NONE, ITEM_NONE},\n' +
        '        .doubleBattle = FALSE,\n' +
        '        .aiFlags = 0x0,\n' +
        '        .partySize = 0,\n' +
        '        .party = {.NoItemDefaultMoves = NULL }\n' +
        '    },\n',
    'pokefirered': \
        'const struct Trainer gTrainers[] = {\n' + \
        '    [TRAINER_NONE] = {\n' + \
        '       .trainerName = _(""),\n' + \
        '    },\n',
    'pokeemerald': \
        'const struct Trainer gTrainers[] = {\n' + \
        '    [TRAINER_NONE] =\n' + \
        '    {\n' + \
        '        .partyFlags = 0,\n' + \
        '        .trainerClass = TRAINER_CLASS_PKMN_TRAINER_1,\n' + \
        '        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_MALE,\n' + \
        '        .trainerPic = TRAINER_PIC_HIKER,\n' + \
        '        .trainerName = _(""),\n' + \
        '        .items = {},\n' + \
        '        .doubleBattle = FALSE,\n' + \
        '        .aiFlags = 0,\n' + \
        '        .partySize = 0,\n' + \
        '        .party = {.NoItemDefaultMoves = NULL},\n' + \
        '    },\n',
    'pokeemerald-expansion': \
        'const struct Trainer gTrainers[] = {\n' + \
        '    [TRAINER_NONE] =\n' + \
        '    {\n' + \
        '        .partyFlags = 0,\n' + \
        '        .trainerClass = TRAINER_CLASS_PKMN_TRAINER_1,\n' + \
        '        .encounterMusic_gender = TRAINER_ENCOUNTER_MUSIC_MALE,\n' + \
        '        .trainerPic = TRAINER_PIC_HIKER,\n' + \
        '        .trainerName = _(""),\n' + \
        '        .items = {},\n' + \
        '        .doubleBattle = FALSE,\n' + \
        '        .aiFlags = 0,\n' + \
        '        .partySize = 0,\n' + \
        '        .party = {.NoItemDefaultMoves = NULL},\n' + \
        '    },\n'
}

CUSTOM_MOVES = 0b01
CUSTOM_ITEMS = 0b10


class TrainerDataFile():
    '''
    Handles the creation and backup of trainer and party data files for different Pokémon project types.
    '''
    def __init__(self, trainers, project_type):
        '''
        Initializes the TrainerDataFile with a list of trainers and the project type.
        '''
        self.trainers_h = ''
        self.trainer_parties_h = ''
        self.project_type = project_type
        self.data = trainers[1:] # Avoid TRAINER_NONE


    def init_file(self):
        '''
        Initializes the trainers_h string with the initial file content for the selected project type.
        '''
        self.trainers_h = INITIAL_FILE_CONTENT[self.project_type]


    def create_files(self, output_paths):
        '''
        Creates and writes the trainer and party data files, making backups if needed.
        Returns 0 on success, 1 if output paths do not exist.
        '''
        PROJECT = 0
        TRAINER_DATA = 1
        TRAINER_PARTIES = 2

        trainers_h_path = os.path.join(output_paths[PROJECT] + output_paths[TRAINER_DATA])
        trainer_parties_h_path = os.path.join(output_paths[PROJECT] + output_paths[TRAINER_PARTIES])

        if not (os.path.exists(trainers_h_path) and os.path.exists(trainer_parties_h_path)):
            return 1

        self.create_backup(trainers_h_path)
        self.create_backup(trainer_parties_h_path)

        for trainer in self.data:
            party_type = self.get_trainer_party_type(trainer)
            self.trainers_h += self.write_trainer(trainer, party_type)
            self.trainer_parties_h += self.write_parties(trainer, party_type)
        
        self.trainers_h = self.trainers_h[:-2]
        self.trainers_h += '\n};\n'

        self.trainer_parties_h = self.trainer_parties_h[:-1]

        with open (trainers_h_path, 'wt') as trainers_h_file:
            trainers_h_file.write(self.trainers_h)
        
        with open (trainer_parties_h_path, 'wt') as trainer_parties_h_file:
            trainer_parties_h_file.write(self.trainer_parties_h)
        
        return 0


    def get_trainer_party_type(self, trainer):
        '''
        Determines the party type for a trainer based on held items and custom moves.
        Returns a string representing the party type.
        '''
        party_type_byte = 0
        party_type = 'NO_ITEM_DEFAULT_MOVES'

        held_item_counter = 0
        for mon in trainer.pokemon:
            if mon.held_item != 'ITEM_NONE':
                held_item_counter += 1
            
        if held_item_counter != 0:
            party_type_byte += CUSTOM_ITEMS
        
        custom_move_counter = 0
        for mon in trainer.pokemon:
            if mon.moves != ["MOVE_NONE", "MOVE_NONE", "MOVE_NONE", "MOVE_NONE"]:
                custom_move_counter += 1
        
        if custom_move_counter != 0:
            party_type_byte += CUSTOM_MOVES
        
        if party_type_byte == CUSTOM_MOVES:
            party_type = 'NO_ITEM_CUSTOM_MOVES'
        elif party_type_byte == CUSTOM_ITEMS:
            party_type = 'ITEM_DEFAULT_MOVES'
        elif party_type_byte == (CUSTOM_ITEMS + CUSTOM_MOVES):
            party_type = 'ITEM_CUSTOM_MOVES'
        
        return party_type


    def write_trainer(self, trainer, party_type='NO_ITEM_DEFAULT_MOVES'):
        '''
        Generates the trainer data string for the trainers.h file.
        '''
        # Trainers.h
        if trainer.items != ['ITEM_NONE', 'ITEM_NONE', 'ITEM_NONE', 'ITEM_NONE']:
            item_list = '{' + str(trainer.items).replace("'", "")[1:-1] + '}'
        else:
            item_list = '{}'
        
        if len(trainer.ai_flags) == 0:
            flag_list = '0'
        else:
            flag_list = str(trainer.ai_flags).replace("'", "")[1:-1].replace(', ', ' | ')

        double_battle = 'FALSE'
        if trainer.double_battle:
            double_battle = 'TRUE'

        gender_flag = ''
        if trainer.gender == 'FEMALE':
            gender_flag = 'F_TRAINER_FEMALE | '
        
        trainer_data = '\n' + \
        '    [' + trainer.id + '] =\n' + \
        '    {\n' + \
        '        .trainerClass = ' + trainer.trainer_class + ',\n' + \
        '        .encounterMusic_gender = ' + gender_flag + trainer.encounter_music + ',\n' + \
        '        .trainerPic = ' + trainer.trainer_pic + ',\n' + \
        '        .trainerName = _("' + trainer.name + '"),\n' + \
        '        .items = ' + item_list + ',\n' + \
        '        .doubleBattle = ' + double_battle + ',\n' + \
        '        .aiFlags = ' + flag_list + ',\n' + \
        '        .party = ' + party_type + '(' + trainer.party_name + '),\n' + \
        '    },\n'
        
        return trainer_data


    def write_parties(self, trainer, party_type='NO_ITEM_DEFAULT_MOVES'):
        '''
        Generates the party data string for the trainer_parties.h file based on the party type.
        '''
        party_struct_name = 'TrainerMonNoItemDefaultMoves'
        if party_type == 'NO_ITEM_CUSTOM_MOVES':
            party_struct_name = 'TrainerMonNoItemCustomMoves'
        elif party_type == 'ITEM_DEFAULT_MOVES':
            party_struct_name = 'TrainerMonItemDefaultMoves'
        elif party_type == 'ITEM_CUSTOM_MOVES':
            party_struct_name = 'TrainerMonItemCustomMoves'
        party_data = \
        'static const struct ' + party_struct_name + ' ' + trainer.party_name + '[] = {\n'
        for mon in trainer.pokemon:
            party_data += \
            '    {\n' + \
            '    .iv = ' + str(mon.iv) + ',\n' + \
            '    .lvl = ' + str(mon.level) + ',\n' + \
            '    .species = ' + mon.species + ','
            if party_type in ['ITEM_DEFAULT_MOVES', 'ITEM_CUSTOM_MOVES']:
                party_data += \
                '\n' + \
                '    .heldItem = ' + mon.held_item

            if party_type in ['NO_ITEM_CUSTOM_MOVES', 'ITEM_CUSTOM_MOVES']:
                move_list = '{' + str(mon.moves).replace("'", "")[1:-1] + '}'
                if party_type == 'ITEM_CUSTOM_MOVES':
                    party_data += ','
                party_data += \
                '\n' + \
                '    .moves = ' + move_list
            party_data += \
            '\n    },\n'
        
        party_data = party_data[:-2]
        party_data += '\n};\n\n'

        return party_data
        

    def create_backup(self, file_path):
        '''
        Creates a timestamped backup of the specified file in the same directory.
        '''
        timestamp = datetime.datetime.now()
        new_file_content = ""

        with open (file_path, 'rt') as file:
            new_file_content = file.read()
        
        new_file_path_split = file_path.split('.')
        new_file_path = os.path.join(new_file_path_split[0] + '_' + str(timestamp.year) + str(timestamp.month) + str(timestamp.day) + '_' + str(timestamp.hour) + str(timestamp.minute) + str(timestamp.second) + '.' + new_file_path_split[1])
        
        with open (new_file_path, 'xt') as new_file:
            new_file.write(new_file_content)

class ShowdownDataFile():
    '''
    Placeholder for handling Showdown data file creation.
    '''
    def __init__(self, trainers, project_type):
        '''
        Not implemented.
        '''
        pass

if __name__ == "__main__":
    print("[!] Please launch main.py")