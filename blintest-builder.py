#!/usr/bin/python

import csv
import glob
import os
import sys
# mandatory to handle accents
# see https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
reload(sys)
sys.setdefaultencoding("utf-8")
import unicodedata

# TODO check that needed executables are installed

# Great code from https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string
def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

def main():

    # Clean previous playlists
    pls = glob.glob('*.m3u')
    for pl in pls:
        os.remove(pl)

    # Check that we have the correct numebr of arguments
    if(len(sys.argv) != 2):
        print "Wrong number of arguments"
        print "Usage: " + sys.argv[0] + " list.csv"
        print "The expected format for the csv file is:"
        print "Playlistname,SongNumber,SongTitle,Artist,Youtube link"
        exit(1)

    playlistID =0
    playlistName = ""
    playlistPath = ""

    csvfile = open(sys.argv[1], "r")
    csvdata = csv.reader(csvfile, delimiter=',')
    for row in csvdata:
        # Find if the current row has a youtube link for a video we can download
        if(row[4].find("://www.youtube.com") != -1 or row[4].find("http") != -1):

            print row

            # Force an id before the playlist name
            # So we get the playlists in the ordre they have been designed
            if(row[0] != playlistName):
                playlistName = row[0]
                playlistID = playlistID + 1
                playlistPath = "./" + str(playlistID) + "." + row[0]

            print playlistName + " " + str(playlistID)

            # Create a directory for the playlist if it doesn't exist
            if( not os.path.exists(playlistPath) ):
                os.mkdir(playlistPath)

            # Manipulate file name so it is ok
            fprefix = playlistPath + "/" + row[1] + "." + row[3] + "_-_" + row[2]
            fprefix = fprefix.replace(" ", "_")
            fprefix = fprefix.replace("'", "_")

            fprefix = remove_accents(fprefix)

            f = glob.glob(fprefix + ".*")
            if(len(f) > 0):
                print "The file for " + f[0] + " already exists. Skipping"
            else:
                filename = "\"" + fprefix + ".%(ext)s\""
                print filename

                # Go into the directory of the current playlist
                cmd = "youtube-dl --restrict-filenames -o " + filename + " -x \"" + row[4] + "\""
                print cmd
                os.system(cmd)

            # Add the mp3 to the playlist
            # find it back with the correct extension
            print fprefix + ".*"
            f = glob.glob(fprefix + ".*")
            print f
            if( len(f) > 0):
                playlist = open(playlistPath + ".m3u", "a")
                playlist.write(f[0] + "\n")
                playlist.close()
            else:
                print "Couldn't find downloaded file"
                exit(1)

        # No youtube link
        else:
            print "No Youtube link for entry " + playlistPath + "/" + row[1]
    return 0

# Trick for reusing the script as a module
if __name__ == '__main__':
    main()
