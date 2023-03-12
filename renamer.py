import os

prefix = 'AD'  # The prefix to search for

for filename in os.listdir('./maps'):
    if filename.startswith(prefix):
        new_filename = filename.replace(prefix, 'Year_AD')
        os.rename("./maps/" + filename, "./maps/" + new_filename)