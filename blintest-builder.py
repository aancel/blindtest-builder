#!/usr/bin/python

import csv
import glob
import os
import sys

# TODO check that needed executables are installed

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

    csvfile = open(sys.argv[1], "r")
    csvdata = csv.reader(csvfile, delimiter=',')
    for row in csvdata:
        # Find if the current row has a youtube link for a video we can download
        if(row[4].find("youtube") != -1):
            print row
            # Create a directory for the playlist if it doesn't exist
            if( not os.path.exists(row[0]) ):
                os.mkdir(row[0])

            # Manipulate file name so it is ok
            fprefix = "./" + row[0] + "/" + row[1] + "." + row[3] + "_-_" + row[2]
            fprefix = fprefix.replace(" ", "_")
            fprefix = fprefix.replace("'", "_")
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
                playlist = open(row[0] + ".m3u", "a")
                playlist.write(f[0] + "\n")
                playlist.close()
            else:
                print "Couldn't find downloaded file"
                exit(1)

        # No youtube link
        else:
            print "No Youtube link for entry " + row[0] + "/" + row[1]
    return 0

# Trick for reusing the script as a module
if __name__ == '__main__':
    main()
