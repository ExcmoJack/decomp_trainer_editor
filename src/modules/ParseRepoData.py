import os
from modules.classes import Trainer, Pokemon, AiFlagList

class ParseRepoDataVanilla():
    ''' This class defines all the functions needed to get all the data needed from the project_files for each version
        only for vanilla pret projects. '''
    def __init__(self, project_path, project_files, project_type):
        self.project_path = project_path
        self.project_files = project_files
        self.project_type = project_type


    def parse_opponents_file(self):
        ''' Read and store in a list the trainer IDs from 'opponents' file. '''
        trainer_id_list = []

        with open(os.path.join(self.project_path, self.project_files['opponents'].lstrip('/')), 'r') as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith('#define TRAINER_'):
                trainer_name = line.split()[1]
                trainer_id_list.append(trainer_name)

        return trainer_id_list[1:] # Remove TRAINER_NONE
    

    def parse_trainer_info_file(self):
        ''' Read and store in a dict list the trainer info from 'trainer_info' file. '''
        trainer_pic_id_list = []
        trainer_class_id_list = []
        trainer_encounter_music_id_list = []

        with open(os.path.join(self.project_path, self.project_files['trainer_info'].lstrip('/')), 'r') as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith('#define TRAINER_PIC_'):
                trainer_pic_id = line.split()[1]
                trainer_pic_id_list.append(trainer_pic_id)
            elif line.startswith('#define TRAINER_CLASS_'):
                trainer_class_id = line.split()[1]
                trainer_class_id_list.append(trainer_class_id)
            elif line.startswith('#define TRAINER_ENCOUNTER_MUSIC_'):
                trainer_encounter_music_id = line.split()[1]
                trainer_encounter_music_id_list.append(trainer_encounter_music_id)
        
        return {
            'TRAINER_PIC': trainer_class_id_list,
            'TRAINER_CLASS': trainer_class_id_list,
            'TRAINER_ENCOUNTER_MUSIC': trainer_encounter_music_id_list
        }
    

    def parse_items_file(self):
        ''' Read and store in a list the item IDs from 'items' file.'''
        item_id_list = []

        with open(os.path.join(self.project_path, self.project_files["items"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        for line in full_content:
            if line.startswith("#define ITEM_"):
                item_id = line.split()[1]
                item_id_list.append(item_id)
            
        for line in full_content:
            if line.startswith("#define ITEMS_COUNT"):
                item_count = int(line.split()[2])
                item_id_list = item_id_list[:item_count]
        
        return item_id_list
    

    def parse_battle_ai_file(self):
        ''' Read and store in a list the AI flags from 'battle_ai' file. '''
        ai_flag_id_list = []

        with open(os.path.join(self.project_path, self.project_files["battle_ai"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        for line in full_content:
            if line.startswith("#define AI_SCRIPT_"):
                ai_flag_id_list.append(line.split()[1])
        
        return ai_flag_id_list
    

    def parse_species_file(self):
        ''' Read and store in a list the species IDs from 'species' file. 
            Avoids SPECIES_EGG and old UNOWN slots.'''
        species_id_list = []

        with open(os.path.join(self.project_path, self.project_files["species"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define SPECIES_EGG"):
                return species_id_list
            if line.startswith("#define SPECIES_OLD_"):
                pass
            elif line.startswith("#define SPECIES_"):
                species_id = line.split()[1]
                species_id_list.append(species_id)
    

    def parse_moves_file(self):
        ''' Read and store in a list the moves IDs from 'moves' file. Limited to MOVES_COUNT. '''
        move_id_list = []

        with open(os.path.join(self.project_path, self.project_files["moves"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define MOVE_"):
                move_id = line.split()[1]
                move_id_list.append(move_id)
        
        for line in full_content:
            if line.startswith("#define MOVES_COUNT"):
                moves_count = int(line.split()[2])
                move_id_list = move_id_list[:moves_count]

        return move_id_list
    

    def parse_trainer_pic_files(self):
        ''' Read and store in a dict list the TRAINER_PIC IDs, pointers and paths from trainer pic files.
            Returns a dict list {'id': 'TRAINER_PIC_XXX' , 'pointer': gTrainerFrontPic_Xxx, 'path': 'xxx.png'}'''
        trainer_pics_dict_list = []

        trainer_pics_ptr_content = self._parse_trainer_pics_ptr_file()
        trainer_pics_dir_content = self._parse_trainer_pics_dir_file()

        PIC_ID = 0
        PIC_POINTER = 1
        PIC_PATH = 2

        for pic_pointer_data in trainer_pics_ptr_content:
            new_pic = {'id': 'TRAINER_PIC_' + pic_pointer_data[PIC_ID], 'pointer': pic_pointer_data[PIC_POINTER], 'path': ''}
            trainer_pics_dict_list.append(new_pic)
        
        for pic_path_data in trainer_pics_dir_content:
            for pic in trainer_pics_dict_list:
                if pic['pointer'] == pic_path_data[PIC_POINTER]:
                    pic['path'] = pic_path_data[PIC_PATH]

        return trainer_pics_dict_list


    def _parse_trainer_pics_ptr_file(self):
        ''' Read and store in a list the TRAINER_PIC IDs and pointers from trainer_pics_ptr file. Returns a tuple list (ID, Pointer).'''
        trainer_pics_ptr_content = []
        with open(os.path.join(self.project_path, self.project_files["trainer_pics_ptr"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        PIC_ID = 0
        PIC_POINTER = 1
    
        for line in full_content:
            if line.strip().startswith('TRAINER_SPRITE'):
                data = line.strip()[15:-2]
                entry = data.split(', ')
                new_pic = (entry[PIC_ID], entry[PIC_POINTER])
                trainer_pics_ptr_content.append(new_pic)
        
        return trainer_pics_ptr_content
    

    def _parse_trainer_pics_dir_file(self):
        ''' Read and store in a list the TRAINER_PIC IDs and pointers from trainer_pics_dir file. Returns a tuple list (None, Pointer, Path).'''
        trainer_pics_dir_content = []
        with open(os.path.join(self.project_path, self.project_files["trainer_pics_dir"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        PIC_POINTER = 0
        PIC_PATH = 1

        for line in full_content:
            if line.strip().startswith('const u32 gTrainerFrontPic_'):
                pic_data = line.strip()[10:-3].replace('[]', '').replace('INCBIN_U32("', '').replace('.4bpp.lz', '.png').split(' = ')
                trainer_pics_dir_content.append((None, pic_data[PIC_POINTER], pic_data[PIC_PATH]))

        return trainer_pics_dir_content
    

    def parse_mon_pic_files(self):
        ''' Read and store in a dict list the SPECIES IDs, pointers and paths from trainer pic files.
            Returns a dict list {'id': 'SPECIES_XXX' , 'pointer': gMonFrontPic_Xxx, 'path': 'xxx.png'}'''
        mon_pics_dict_list = []

        mon_pics_ptr_content = self._parse_mon_pics_ptr_file()
        mon_pics_dir_content = self._parse_mon_pics_dir_file()

        PIC_ID = 0
        PIC_POINTER = 1
        PIC_PATH = 2

        for pic_pointer_data in mon_pics_ptr_content:
            new_pic = {'species': 'SPECIES_' + pic_pointer_data[PIC_ID], 'pointer': pic_pointer_data[PIC_POINTER], 'path': ''}
            mon_pics_dict_list.append(new_pic)
        
        for pic_path_data in mon_pics_dir_content:
            for pic in mon_pics_dict_list:
                if pic['pointer'] == pic_path_data[PIC_POINTER]:
                    if pic['species'] == 'SPECIES_CASTFORM':
                        pic['path'] = ''
                        path_list = pic_path_data[PIC_PATH].split('/')
                        path_list.insert(-1, 'normal')
                        for item in path_list:
                            if item == path_list[0]:
                                pic['path'] += item
                            else:
                                pic['path'] += '/' + item
                    else:
                        pic['path'] = pic_path_data[PIC_PATH]
        
        return mon_pics_dict_list
    

    def _parse_mon_pics_ptr_file(self):
        ''' Read and store in a list the SPECIES_SPRITE IDs and pointers from mon_pics_ptr file. Returns a tuple list (ID, Pointer).'''
        mon_pics_ptr_content = []
        with open(os.path.join(self.project_path, self.project_files["mon_pics_ptr"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        PIC_ID = 0
        PIC_POINTER = 1

        for line in full_content:
            if line.strip().startswith('SPECIES_SPRITE('):
                data = line.strip()[15:-2].replace(' ', '')
                entry = data.split(',')
                new_pic = (entry[PIC_ID], entry[PIC_POINTER])
                mon_pics_ptr_content.append(new_pic)
        
        return mon_pics_ptr_content


    def _parse_mon_pics_dir_file(self):
        ''' Read and store in a list the SPECIES IDs and pointers from mon_pics_dir file. Returns a tuple list (None, Pointer, Path).'''
        mon_pics_dir_content = []
        with open(os.path.join(self.project_path, self.project_files["mon_pics_dir"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        PIC_POINTER = 0
        PIC_PATH = 1

        for line in full_content:
            if line.strip().startswith('const u32 gMonFrontPic_'):
                pic_data = line.strip()[10:-3].replace('[]', '').replace('INCBIN_U32("', '').replace('.4bpp.lz', '.png').split(' = ')
                mon_pics_dir_content.append((None, pic_data[PIC_POINTER], pic_data[PIC_PATH]))
        
        return mon_pics_dir_content


    def parse_trainer_data_file(self, ai_flags, gender_options):
        ''' Parse the trainer info from 'trainer_data' file and process it to self.project_data. 
        
            * .partyFlags - It will be adquired from party macros
            * .trainerClass
            * .encounterMusic_gender - For some reason the gender is put here as a flag... Only if the trainer is female!
            * .trainerPic
            * .trainerName
            * .items
            * .doubleBattle
            * .aiFlags - The list of flags available is taken from the main object. I guess at this point we must debate if ProjectData and RepoData are kinda equivalent classes.
            * .partySize - It will be adquired from party macros
            * .party
        '''

        MALE = 0
        FEMALE = 1

        trainer_list = []

        with open(os.path.join(self.project_path, self.project_files["trainer_data"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        new_trainer = None
        for line in full_content:
            data = line.strip().split(" ")
            field = data[0]
            if field[:9] == '[TRAINER_':
                new_trainer = Trainer(line.strip().split(" ")[0][1:-1])
                uses_party_macro = True
            elif field == '.trainerClass':
                new_trainer.trainer_class = data[2].strip('",')
            elif field == '.encounterMusic_gender':
                new_trainer.gender = gender_options[MALE]
                for stuff in data[2:]:
                    if stuff.startswith("TRAINER_ENCOUNTER_MUSIC_"):
                        new_trainer.encounter_music = stuff.strip('",')
                    elif stuff == "F_TRAINER_FEMALE":
                        new_trainer.gender = gender_options[FEMALE]
            elif field == '.trainerPic':
                new_trainer.trainer_pic = data[2].strip('",')
            elif field == '.trainerName':
                new_trainer.name = line.split('"')[1]
            elif field == '.items':
                for item in data[2:]:
                    if item.strip('",{}') != '':
                        new_trainer.items.append(item.strip('",{}'))
                while len(new_trainer.items) < 4:
                    new_trainer.items.append('ITEM_NONE')
            elif field == '.doubleBattle':
                if data[2] == 'TRUE,':
                    new_trainer.double_battle = True
                else:
                    new_trainer.double_battle = False
            elif field == '.aiFlags':
                for flag in data[2:]:
                    if ai_flags.is_flag(flag.strip('",{}')):
                        new_trainer.ai_flags.append(flag.strip('",'))
            elif field == '.partyFlags':
                uses_party_macro = False
            elif field == '.partySize':
                uses_party_macro = False
            elif field == '.party':
                if uses_party_macro:
                    party_pointer = data[2].split('(')[1].strip('),')
                    new_trainer.party_name = party_pointer
                    new_trainer.pokemon = self._parse_trainer_parties_file(party_pointer)
            elif field == '},':
                trainer_list.append(new_trainer)
                new_trainer = None
        
        return trainer_list


    def _parse_trainer_parties_file(self, pointer):
        ''' Parse the party Pokémon data from 'trainer_parties' file and process it to return as a Pokémon list. '''

        with open(os.path.join(self.project_path, self.project_files["trainer_parties"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        party = []
        new_mon = None
        
        party_pointer_found = False
        for line in full_content:
            data = line.strip().split(" ")
            field = data[0]
            if line.strip().startswith('static const struct') and (pointer + '[]') in line.split(" "):
                party_pointer_found = True
            if party_pointer_found:
                if field == '}' or field == '},':
                    new_mon = Pokemon(mon_struct['species'])
                    new_mon.level = int(mon_struct['lvl'])
                    new_mon.held_item = mon_struct['heldItem']
                    new_mon.iv = int(mon_struct['iv'])
                    new_mon.moves = mon_struct['moves']
                    party.append(new_mon)
                    new_mon = None
                    mon_struct = None
                if field == '{':
                    mon_struct = {
                        'iv': '', # Somehow up to 255
                        'lvl': '',
                        'species': '',
                        'heldItem': 'ITEM_NONE',
                        'moves': ['MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE']
                    }
                if field == '.iv':
                    mon_struct['iv'] = int(data[2].strip(','))
                if field == '.lvl':
                    mon_struct['lvl'] = int(data[2].strip(','))
                if field == '.species':
                    mon_struct['species'] = data[2].strip('",')
                if field == '.heldItem':
                    mon_struct['heldItem'] = data[2].strip('",')
                if field == '.moves':
                    moves = []
                    for move in data[2:]:
                        if move.strip('",{}') != '':
                            moves.append(move.strip('",{}'))
                    while len(moves) < 4:
                        moves.append('MOVE_NONE')
                    mon_struct['moves'] = moves
                if line.strip().startswith('};'):
                    party_pointer_found = False
    
        return party


    def parse_data_inc_files_for_trainerbattle(self, trainer_id):
        maps_root_folder = os.path.join(self.project_path + self.project_files['scripts_folder'], 'maps')
        scripts_root_folder = os.path.join(self.project_path + self.project_files['scripts_folder'], 'scripts')
        trainerbattle_folders = []

        for map_name in os.listdir(maps_root_folder):
            map_folder_path = os.path.join(maps_root_folder, map_name)
            map_scripts_path = os.path.join(map_folder_path, 'scripts.inc')
            if os.path.isfile(map_scripts_path):
                with open(map_scripts_path, 'rt') as f:
                    script_file = f.readlines()
                
                for line in script_file:
                    if line.strip().startswith('trainerbattle'):
                        if (trainer_id + ',') in line:
                            if map_name not in trainerbattle_folders:
                                trainerbattle_folders.append(map_name)
        
        for file in os.listdir(scripts_root_folder):
            special_scripts_path = os.path.join(scripts_root_folder, file)
            if os.path.isfile(special_scripts_path):
                with open(special_scripts_path, 'rt') as f:
                    script_file = f.readlines()
                
                for line in script_file:
                    if line.strip().startswith('trainerbattle'):
                        if (trainer_id + ',') in line:
                            if ('File: ' + file) not in trainerbattle_folders:
                                trainerbattle_folders.append('File: ' + file)

        if len(trainerbattle_folders) == 0:
            trainerbattle_folders.append('Probably rematch or in src. Check manually.')

        return trainerbattle_folders
        

class ParseRepoDataExpansion():
    ''' This class defines all the functions needed to get all the data needed from the project_files for each version
        only for pokeemerald-expansion projects. '''
    def __init__(self, project_path, project_files, project_type):
        self.project_path = project_path
        self.project_files = project_files
        self.project_type = project_type


    def parse_opponents_file(self):
        ''' Read and store in a list the trainer IDs from constants/opponents.h file. '''
        trainer_id_list = []

        with open(os.path.join(self.project_path, self.project_files['opponents'].lstrip('/')), 'r') as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith('#define TRAINER_'):
                trainer_name = line.split()[1]
                trainer_id_list.append(trainer_name)

        return trainer_id_list[1:] # Remove TRAINER_NONE
    

    def parse_trainer_info_file(self):
        ''' Read and store in a dict list the trainer info from constants/trainers.h file. '''
        trainer_pic_id_list = []
        trainer_class_id_list = []
        trainer_encounter_music_id_list = []

        with open(os.path.join(self.project_path, self.project_files['trainer_info'].lstrip('/')), 'r') as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith('#define TRAINER_PIC_'):
                trainer_pic_id = line.split()[1]
                trainer_pic_id_list.append(trainer_pic_id)
            elif line.startswith('#define TRAINER_CLASS_'):
                trainer_class_id = line.split()[1]
                trainer_class_id_list.append(trainer_class_id)
            elif line.startswith('#define TRAINER_ENCOUNTER_MUSIC_'):
                trainer_encounter_music_id = line.split()[1]
                trainer_encounter_music_id_list.append(trainer_encounter_music_id)
        
        return {
            'TRAINER_PIC': trainer_class_id_list,
            'TRAINER_CLASS': trainer_class_id_list,
            'TRAINER_ENCOUNTER_MUSIC': trainer_encounter_music_id_list
        }
    

    def parse_items_file(self):
        ''' Read and store in a list the item IDs from constants/items.h file.'''
        item_id_list = []

        with open(os.path.join(self.project_path, self.project_files["items"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        for line in full_content:
            if line.startswith("#define ITEM_"):
                item_id = line.split()[1]
                item_id_list.append(item_id)
            
        for line in full_content:
            if line.startswith("#define ITEMS_COUNT"):
                item_count = int(line.split()[2])
                item_id_list = item_id_list[:item_count]
        
        return item_id_list
    

    def parse_battle_ai_file(self):
        ''' Read and store in a list the AI flags from constants/battle_ai.h file. '''
        ai_flag_id_list = []

        with open(os.path.join(self.project_path, self.project_files["battle_ai"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        for line in full_content:
            if line.startswith("#define AI_SCRIPT_"):
                ai_flag_id_list.append(line.split()[1])
        
        return ai_flag_id_list
    

    def parse_species_file(self):
        ''' Read and store in a list the species IDs from constants/species.h file. 
            Avoids SPECIES_EGG and old UNOWN slots.'''
        species_id_list = []

        with open(os.path.join(self.project_path, self.project_files["species"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define SPECIES_EGG"):
                return species_id_list
            if line.startswith("#define SPECIES_OLD_"):
                pass
            elif line.startswith("#define SPECIES_"):
                species_id = line.split()[1]
                species_id_list.append(species_id)
    

    def parse_moves_file(self):
        ''' Read and store in a list the moves IDs from constants/moves.h file. Limited to MOVES_COUNT. '''
        move_id_list = []

        with open(os.path.join(self.project_path, self.project_files["moves"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        for line in full_content:
            if line.startswith("#define MOVE_"):
                move_id = line.split()[1]
                move_id_list.append(move_id)
        
        for line in full_content:
            last_gen_count = 0
            if line.startswith("#define MOVES_COUNT_GEN"):
                last_gen_count = int(line.split()[2])
            elif line.startswith("#define MOVES_COUNT"):
                if line.split()[2].isdecimal():
                    moves_count = int(line.split()[2])
                else:
                    moves_count = last_gen_count
                move_id_list = move_id_list[:moves_count]

        return move_id_list
    

    def parse_trainer_pic_files(self):
        ''' Read and store in a dict list the TRAINER_PIC IDs, pointers and paths from trainer pic files.
            Returns a dict list {'id': 'TRAINER_PIC_XXX' , 'pointer': gTrainerFrontPic_Xxx, 'path': 'xxx.png'}'''
        trainer_pics_dict_list = []

        trainer_pics_ptr_content = self._parse_trainer_pics_ptr_file()
        trainer_pics_dir_content = self._parse_trainer_pics_dir_file()

        PIC_ID = 0
        PIC_POINTER = 1
        PIC_PATH = 2

        for pic_pointer_data in trainer_pics_ptr_content:
            new_pic = {'id': 'TRAINER_PIC_' + pic_pointer_data[PIC_ID], 'pointer': pic_pointer_data[PIC_POINTER], 'path': ''}
            trainer_pics_dict_list.append(new_pic)
        
        for pic_path_data in trainer_pics_dir_content:
            for pic in trainer_pics_dict_list:
                if pic['pointer'] == pic_path_data[PIC_POINTER]:
                    pic['path'] = pic_path_data[PIC_PATH]

        return trainer_pics_dict_list


    def _parse_trainer_pics_ptr_file(self):
        ''' Read and store in a list the TRAINER_PIC IDs and pointers from trainer_pics_ptr file. Returns a tuple list (ID, Pointer).'''
        trainer_pics_ptr_content = []
        with open(os.path.join(self.project_path, self.project_files["trainer_pics_ptr"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        PIC_ID = 0
        PIC_POINTER = 1
    
        for line in full_content:
            if line.strip().startswith('TRAINER_SPRITE'):
                data = line.strip()[15:-2]
                entry = data.split(', ')
                new_pic = (entry[PIC_ID], entry[PIC_POINTER])
                trainer_pics_ptr_content.append(new_pic)
        
        return trainer_pics_ptr_content
    

    def _parse_trainer_pics_dir_file(self):
        ''' Read and store in a list the TRAINER_PIC IDs and pointers from trainer_pics_dir file. Returns a tuple list (None, Pointer, Path).'''
        trainer_pics_dir_content = []
        with open(os.path.join(self.project_path, self.project_files["trainer_pics_dir"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        PIC_POINTER = 0
        PIC_PATH = 1

        for line in full_content:
            if line.strip().startswith('const u32 gTrainerFrontPic_'):
                pic_data = line.strip()[10:-3].replace('[]', '').replace('INCBIN_U32("', '').replace('.4bpp.lz', '.png').split(' = ')
                trainer_pics_dir_content.append((None, pic_data[PIC_POINTER], pic_data[PIC_PATH]))

        return trainer_pics_dir_content
    

    def parse_mon_pic_files(self):
        ''' Read and store in a dict list the SPECIES IDs, pointers and paths from trainer pic files.
            Returns a dict list {'id': 'SPECIES_XXX' , 'pointer': gMonFrontPic_Xxx, 'path': 'xxx.png'}'''
        mon_pics_dict_list = []

        mon_pics_ptr_content = self._parse_mon_pics_ptr_file()
        mon_pics_dir_content = self._parse_mon_pics_dir_file()

        PIC_ID = 0
        PIC_POINTER = 1
        PIC_PATH = 2

        for pic_pointer_data in mon_pics_ptr_content:
            new_pic = {'species': 'SPECIES_' + pic_pointer_data[PIC_ID], 'pointer': pic_pointer_data[PIC_POINTER], 'path': ''}
            mon_pics_dict_list.append(new_pic)
        
        for pic_path_data in mon_pics_dir_content:
            for pic in mon_pics_dict_list:
                if pic['pointer'] == pic_path_data[PIC_POINTER]:
                    if pic['species'] == 'SPECIES_CASTFORM':
                        pic['path'] = ''
                        path_list = pic_path_data[PIC_PATH].split('/')
                        path_list.insert(-1, 'normal')
                        for item in path_list:
                            if item == path_list[0]:
                                pic['path'] += item
                            else:
                                pic['path'] += '/' + item
                    else:
                        pic['path'] = pic_path_data[PIC_PATH]
        
        return mon_pics_dict_list
    

    def _parse_mon_pics_ptr_file(self):
        ''' Read and store in a list the SPECIES_SPRITE IDs and pointers from mon_pics_ptr file. Returns a tuple list (ID, Pointer).'''
        mon_pics_ptr_content = []
        with open(os.path.join(self.project_path, self.project_files["mon_pics_ptr"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        PIC_ID = 0
        PIC_POINTER = 1

        for line in full_content:
            if line.strip().startswith('SPECIES_SPRITE('):
                data = line.strip()[15:-2].replace(' ', '')
                entry = data.split(',')
                new_pic = (entry[PIC_ID], entry[PIC_POINTER])
                mon_pics_ptr_content.append(new_pic)
        
        return mon_pics_ptr_content


    def _parse_mon_pics_dir_file(self):
        ''' Read and store in a list the SPECIES IDs and pointers from mon_pics_dir file. Returns a tuple list (None, Pointer, Path).'''
        mon_pics_dir_content = []
        with open(os.path.join(self.project_path, self.project_files["mon_pics_dir"].lstrip("/")), "r") as f:
            full_content = f.readlines()
        
        PIC_POINTER = 0
        PIC_PATH = 1

        for line in full_content:
            if line.strip().startswith('const u32 gMonFrontPic_'):
                pic_data = line.strip()[10:-3].replace('[]', '').replace('INCBIN_U32("', '').replace('.4bpp.lz', '.png').split(' = ')
                mon_pics_dir_content.append((None, pic_data[PIC_POINTER], pic_data[PIC_PATH]))
        
        return mon_pics_dir_content


    def parse_trainer_data_file(self, ai_flags, gender_options):
        ''' Parse the trainer info from data/trainers.h file and process it to self.project_data. 
        
            * .partyFlags - It will be adquired from party macros
            * .trainerClass
            * .encounterMusic_gender - For some reason the gender is put here as a flag... Only if the trainer is female!
            * .trainerPic
            * .trainerName
            * .items
            * .doubleBattle
            * .aiFlags - The list of flags available is taken from the main object. I guess at this point we must debate if ProjectData and RepoData are kinda equivalent classes.
            * .partySize - It will be adquired from party macros
            * .party
        '''

        MALE = 0
        FEMALE = 1

        trainer_list = []

        with open(os.path.join(self.project_path, self.project_files["trainer_data"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        new_trainer = None
        for line in full_content:
            data = line.strip().split(" ")
            field = data[0]
            if field[:9] == '[TRAINER_':
                new_trainer = Trainer(line.strip().split(" ")[0][1:-1])
                uses_party_macro = True
            elif field == '.trainerClass':
                new_trainer.trainer_class = data[2].strip('",')
            elif field == '.encounterMusic_gender':
                new_trainer.gender = gender_options[MALE]
                for stuff in data[2:]:
                    if stuff.startswith("TRAINER_ENCOUNTER_MUSIC_"):
                        new_trainer.encounter_music = stuff.strip('",')
                    elif stuff == "F_TRAINER_FEMALE":
                        new_trainer.gender = gender_options[FEMALE]
            elif field == '.trainerPic':
                new_trainer.trainer_pic = data[2].strip('",')
            elif field == '.trainerName':
                new_trainer.name = line.split('"')[1]
            elif field == '.items':
                for item in data[2:]:
                    if item.strip('",{}') != '':
                        new_trainer.items.append(item.strip('",{}'))
                while len(new_trainer.items) < 4:
                    new_trainer.items.append('ITEM_NONE')
            elif field == '.doubleBattle':
                if data[2] == 'TRUE,':
                    new_trainer.double_battle = True
                else:
                    new_trainer.double_battle = False
            elif field == '.aiFlags':
                for flag in data[2:]:
                    if ai_flags.is_flag(flag.strip('",{}')):
                        new_trainer.ai_flags.append(flag.strip('",'))
            elif field == '.partyFlags':
                uses_party_macro = False
            elif field == '.partySize':
                uses_party_macro = False
            elif field == '.party':
                if uses_party_macro:
                    party_pointer = data[2].split('(')[1].strip('),')
                    new_trainer.party_name = party_pointer
                    new_trainer.pokemon = self._parse_trainer_parties_file(party_pointer)
            elif field == '},':
                trainer_list.append(new_trainer)
                new_trainer = None
        
        return trainer_list


    def _parse_trainer_parties_file(self, pointer):
        ''' Parse the party Pokémon data from data/trainer_parties.h file and process it to return as a Pokémon list. '''

        with open(os.path.join(self.project_path, self.project_files["trainer_parties"].lstrip("/")), "r") as f:
            full_content = f.readlines()

        party = []
        new_mon = None
        
        party_pointer_found = False
        for line in full_content:
            data = line.strip().split(" ")
            field = data[0]
            if line.strip().startswith('static const struct') and (pointer + '[]') in line.split(" "):
                party_pointer_found = True
            if party_pointer_found:
                if field == '}' or field == '},':
                    new_mon = Pokemon(mon_struct['species'])
                    new_mon.level = int(mon_struct['lvl'])
                    new_mon.held_item = mon_struct['heldItem']
                    new_mon.iv = int(mon_struct['iv'])
                    new_mon.moves = mon_struct['moves']
                    party.append(new_mon)
                    new_mon = None
                    mon_struct = None
                if field == '{':
                    mon_struct = {
                        'iv': '', # Somehow up to 255
                        'lvl': '',
                        'species': '',
                        'heldItem': 'ITEM_NONE',
                        'moves': ['MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE', 'MOVE_NONE']
                    }
                if field == '.iv':
                    mon_struct['iv'] = int(data[2].strip(','))
                if field == '.lvl':
                    mon_struct['lvl'] = int(data[2].strip(','))
                if field == '.species':
                    mon_struct['species'] = data[2].strip('",')
                if field == '.heldItem':
                    mon_struct['heldItem'] = data[2].strip('",')
                if field == '.moves':
                    moves = []
                    for move in data[2:]:
                        if move.strip('",{}') != '':
                            moves.append(move.strip('",{}'))
                    while len(moves) < 4:
                        moves.append('MOVE_NONE')
                    mon_struct['moves'] = moves
                if line.strip().startswith('};'):
                    party_pointer_found = False
    
        return party


if __name__ == "__main__":
    print("[!] Please launch main.py")