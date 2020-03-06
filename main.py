
project_path = '/Users/decandia/Dropbox/teresa_stuff/music_loops' #make sure this points to correct location

#   load packages and set directory
import os
import pandas as pd
import xml.etree.ElementTree as ET
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


os.chdir(project_path)

xml_path = os.path.join(project_path, 'Scientist_Testdata/XML-Projects/')
csv_path = os.path.join(project_path, 'Scientist_Testdata/Mix-Packs/')

#   load local packages
import read_functions as rf


###########################
#1. Parse the XML files and extract information
###########################
#read in files
xmls = rf.concatenate_XML(xml_path)
csvs = rf.concatenate_CSV(csv_path)


###########################
#2. Use the data in the CSV files to replace the loop filename with the corresponding features
#(label + d1-d8)
###########################

#remove records where channel is not active
xmls = xmls[xmls['channel_is_active'] == 'true'].drop('channel_is_active', axis=1)

#remove id column from csvs
csvs.drop(['Id'], axis = 1, inplace = True)

#remove from xmls `channel_loop`:
#a) white space
#b) leading 'mmj://styles/id/'
#c) trailing '1'
xmls['channel_loop'] = xmls['channel_loop'].str.replace(" ","")
xmls['channel_loop'] = xmls['channel_loop'].str.lstrip('mmj://styles/id/')
xmls['channel_loop'] = xmls['channel_loop'].str.rstrip('1')


#remove from csvs `Filename`:
#a) white space
#b) leading 'Mix Packs/'
#c) trailing '1'
csvs['Filename'] = csvs['Filename'].str.replace(" ","")
csvs['Filename'] = csvs['Filename'].str.lstrip('Mix Packs/')
csvs['Filename'] = csvs['Filename'].str.rstrip('1')


#test with an left join:
#df = xmls.merge(csvs, how='left', left_on = 'channel_loop', right_on = 'Filename', indicator=True)
#df[df['_merge'] == ['left_only']]['channel_loop']
#only 13 xmls records don't get merged and those seem to be user_loops


#inner merge
df = xmls.merge(csvs, how='inner', left_on = 'channel_loop', right_on = 'Filename')
df.shape #(9945, 21)


#convert where appropriate to numeric
string_cols = ['project_cut_mode','part_name','channel_loop','Filename']
cols = df.columns.drop(string_cols)
df[cols] = df[cols].apply(pd.to_numeric)


#save cleaned data
cleaned_data_name = os.path.join(project_path, 'cleaned_data.csv')
df.to_csv(cleaned_data_name, index = False)
#df = pd.read_csv(cleaned_data_name, index_col=None, header=0)


###########################
#3. Calculate some statistics about a music track.
###########################

#number of parts
number_parts_per_proj = df.groupby('project_number')['part_number'].nunique()
number_parts_per_proj.describe()
'''
count    100.000000
mean      21.380000
std        8.842939
min       16.000000
25%       17.000000
50%       19.000000
75%       24.000000
max       92.000000
'''

#number of loops in parts
number_loops_per_part = df.groupby(['project_number','part_number'])['channel_number'].nunique()
number_loops_per_part.describe()
'''
count    2138.000000
mean        4.651543
std         2.004371
min         1.000000
25%         3.000000
50%         5.000000
75%         6.000000
max         8.000000
'''

#most used loops
most_used_loops = df['channel_loop'].value_counts()
most_used_loops[:5] #top five
'''
ST_Electro_Lite/Chipsounds/JiveGlitch    221
ST_Electro_Lite/Bass/BestSubBass         203
ST_House_Lite/Bass/Absorber              199
ST_House_Lite/DrumsSolo/DrakeE           199
ST_Electro_Lite/Lead/ChefLead            185
'''

#most used Mix Packs within the XML project files
df[['mix_pack','instrument','loop_name']] = pd.DataFrame(df['channel_loop'].str.split('/').tolist())
most_used_packs = df['mix_pack'].value_counts()
most_used_packs
'''
ST_Electro_Lite        2824
ST_House_Lite          2775
ST_Electro_Pop         2500
ST_Loudly_Exclusive    1846
'''

#most informative part index in a XML project file
most_informative_features = df.groupby('project_number').std().mean().sort_values(ascending=False)
most_informative_features[:10] #top ten
'''
channel_volume          18.440584
part_number              5.689702
part_length_in_beats     4.417364
channel_number           2.009779
Label                    0.258563
d1                       0.198980
d2                       0.140180
d6                       0.108406
d3                       0.106989
d8                       0.104792
'''
#not sure what more informative means in this context, but here are the features that show the greatest variation within each project
#within each project, volume tends to vary quite a bit (18.44 is the standard deviation)
#so do the number of parts, the part length in beats, the loop label
#the most variable d values are d1, d2, and d6 in that order


###########################
#4. Find a metric to compute the similarity between the projects
###########################

cols = ['d1','d2','d3','d4','d5','d6','d7','d8']
projects_by_ds = df.groupby('project_number')[cols].mean()


#Are d values correlated
projects_by_d.corr()
#They are quite correlated (some in the same direction and some in opposite directions)
my_model = PCA(2)
pcs_1_2 = my_model.fit_transform(projects_by_ds)
my_model.explained_variance_ratio_
#array([0.32365161, 0.26940772]) #half of variance explained by first two principal components


#How similar are projects to each other according to their d values?
#Not going to bother with object oriented maplotlib plots for here
corr = projects_by_d.T.corr()
plt.matshow(corr)
plt.show()
#From this we see that certain projects tend to have very low correlations to all other projects


similarity_between_projects_d = corr.stack()
off_diag_corrs_d = similarity_between_projects_d[
    similarity_between_projects_d.index.get_level_values(0) <
    similarity_between_projects_d.index.get_level_values(1)
    ]
plt.hist(off_diag_corrs_d)
plt.show()
off_diag_corrs_d.describe()
'''
count    4950.000000
mean        0.803326
std         0.128430
min         0.052625
25%         0.739969
50%         0.830822
75%         0.895910
max         0.999734
'''
#Projects tend to be quite similar by this metric


#What about across all variables
similarity_between_projects = df.groupby('project_number').mean().T.corr().stack()
off_diag_corrs = similarity_between_projects[
    similarity_between_projects.index.get_level_values(0) <
    similarity_between_projects.index.get_level_values(1)
    ]
plt.hist(off_diag_corrs)
plt.show()
off_diag_corrs.describe()
'''
count    4950.000000
mean        0.938143
std         0.062798
min         0.672369
25%         0.921631
50%         0.955701
75%         0.982623
max         0.999975
'''
#Similar results as above
off_diag_corrs.corr(off_diag_corrs_d)
#0.09951639930640456



#PCA is a linear transformation and it doesn't capture non-linear effects
#So something like autoencoders would be good to try to reduce the dimensionality of the data
#for the purposes of clustering projects into some hypothesized number of groups
#and grid searches can be used to figure out the optimal number of groups


