from modules.classes import Trainer, Pokemon
import os

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
    def __init__(self, trainers, project_type):
        self.trainers_h = ''
        self.trainer_parties_h = ''
        self.project_type = project_type
        self.data = trainers[1:] # Avoid TRAINER_NONE


    def init_file(self):
        self.trainers_h = INITIAL_FILE_CONTENT[self.project_type]


    def create_files(self, output_path):
        for trainer in self.data:
            party_type = self.get_trainer_party_type(trainer)
            self.trainers_h += self.write_trainer(trainer, party_type)
            self.trainer_parties_h += self.write_parties(trainer, party_type)
        
        self.trainers_h = self.trainers_h[:-2]
        self.trainers_h += '\n};\n'

        self.trainer_parties_h = self.trainer_parties_h[:-1]

        with open (os.path.join(output_path, 'trainers.h'), 'wt') as trainers_h:
            trainers_h.write(self.trainers_h)
        
        with open (os.path.join(output_path, 'trainer_parties.h'), 'wt') as trainer_parties_h:
            trainer_parties_h.write(self.trainer_parties_h)


    def get_trainer_party_type(self, trainer):
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
        

if __name__ == "__main__":
    file = TrainerDataFile(None, 'pokefirered')
    file.init_file()
    print(file.trainers_h)