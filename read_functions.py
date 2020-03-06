
#   load packages
import os
from glob import glob
import pandas as pd
import xml.etree.ElementTree as ET



def XML_to_df(xml):
    
    tree = ET.parse(xml)
    root=tree.getroot()
    
    df_cols = ['project_volume','project_bpm','project_cut_mode',
#             'used_chords_text',
#             'loop_id','loop_name','loop_bpm','loop_length_in_beats','loop_path',
               'part_number','part_pitch','part_length_in_beats','part_name',
               'channel_number','channel_loop','channel_volume','channel_is_active',
#             'chord_sequence_text'
               ]
    
    df = pd.DataFrame(columns=df_cols)
    
    for project in root.iter('project'):
        project_volume = project.attrib['volume']
        project_bpm = project.attrib['bpm']
        project_cut_mode = project.attrib['cut_mode']   
        root1=ET.Element('root')
        root1=project
#       for used_chords in root1.iter('used_chords'):
#           used_chords_text = used_chords.text
#       for user_loops in root1.iter('user_loops'):
#           root2=ET.Element('root')
#           root2=(user_loops)
#           for loop in root2.iter('loop'):
#               loop_id = loop.attrib['id']
#               loop_id = loop.find('id')        
#               loop_name = loop.attrib['name']
#               loop_bpm = loop.attrib['bpm']
#               loop_length_in_beats = loop.attrib['length_in_beats']
#               loop_path = loop.attrib['path']            
        for parts in root1.iter('parts'):
            parts_selected_index = parts.attrib['selected_index'] 
            root2=ET.Element('root')
            root2=(parts)
            part_count = 0
            for part in root2.iter('part'):
                part_number = part_count+1
                part_pitch = part.attrib['pitch']
                part_length_in_beats = part.attrib['length_in_beats']
                part_name = part.attrib['name']
                part_count+=1
                root3=ET.Element('root')
                root3=(part)
                for channels in root3.iter('channels'):                
                    root4=ET.Element('root')
                    root4=(channels)
                    channel_count = 0
                    for channel in root4.iter('channel'):
                        channel_number = channel_count+1
                        channel_loop = channel.attrib['loop']
                        channel_volume = channel.attrib['volume']
                        channel_is_active = channel.attrib['is_active']
                        channel_count+=1
#               for chord_sequence in root3.iter('chord_sequence'):
#                   chord_sequence_text = chord_sequence.text
                        df = df.append( pd.Series(
                        [project_volume,project_bpm,project_cut_mode,
                         part_number, part_pitch,part_length_in_beats,part_name,
                         channel_number,channel_loop,channel_volume,channel_is_active,
                         ],
                        index=df_cols) ,ignore_index=True)
                        
    return(df)


def read_files_from_dir(PATH, EXT):
    all_files = [file
                 for path, subdir, files in os.walk(PATH)
                 for file in glob(os.path.join(path, EXT))]
    return(all_files)


def concatenate_XML(path):
    all_files = read_files_from_dir(path, EXT='*.xml')
    li = []
    project_number = 0
    for filename in all_files:
        project_number+=1
        print("Reading in",filename)
        df = XML_to_df(filename)
        df['project_number'] = project_number
        li.append(df)
    df = pd.concat(li, axis=0, ignore_index=True)
    return(df)


def concatenate_CSV(path):
    all_files = read_files_from_dir(path, EXT='*.csv')
    li = []
    for filename in all_files:
        print("Reading in",filename)
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)
    df = pd.concat(li, axis=0, ignore_index=True)
    return(df)





