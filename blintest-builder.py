#!/usr/bin/env python

import csv
import fnmatch
import glob
import os
import sys
import shutil
import eyed3

# mandatory to handle accents for Python 2
# see https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string # noqa E501
# reload(sys)
# sys.setdefaultencoding("utf-8")
# import unicodedata

# Great code from https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-in-a-python-unicode-string # noqa 501
# def remove_accents(input_str):
#     nkfd_form = unicodedata.normalize('NFKD', unicode(input_str))
#     return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def main():
    # test that we actually have the required commands available
    mp3GainExec = ""
    ret = os.system("mp3gain -v")
    if(ret != 0):
        print("Err(" + str(ret) + "): " +
              "mp3gain does not seem to be installed. Attempting to build it.")
        if not os.path.exists("./bin"):
            os.makedirs("./bin")
        if not os.path.exists("./bin/mp3gain"):
            os.makedirs("./bin/mp3gain")
        if not os.path.exists("./bin/mp3gain/mp3gain"):

            # Check that we have all the dependencies for building mp3gain
            ret = os.system("pkg-config --exists libmpg123")
            if(ret != 0):
                print("Err(" + str(ret) + "): " +
                      "libmpg123-dev does not seem to be installed " +
                      "(needed by mp3gain). " +
                      " Please install the library libmpg123-dev")
                exit(1)

            os.chdir("bin/mp3gain")
            os.system("curl -L " +
                      "https://sourceforge.net/projects/mp3gain/files/" +
                      "mp3gain/1.6.2/mp3gain-1_6_2-src.zip/download " +
                      "-o mp3gain-1_6_2-src.zip")
            ret = os.system("unzip mp3gain-1_6_2-src.zip")
            ret = os.system("make")
            os.chdir("../..")

        # Check that mp3gain has been correctly built
        if not os.path.exists("./bin/mp3gain/mp3gain"):
            print("mp3gain failed to be built. Please install it")
            exit(1)
        else:
            print("Using locally built mp3gain")
            mp3GainExec = os.path.abspath("./bin/mp3gain/mp3gain")
    else:
        mp3GainExec = "mp3gain"

    ret = os.system("ffmpeg -version")
    if(ret != 0):
        print("Err(" + str(ret) + "): " +
              "ffmpeg does not seem to be installed. " +
              "Please install the command-line tool ffmpeg")
        exit(1)

    # ret = os.system("eyeD3 --version")
    # if(ret != 0):
        # print "Err(" + str(ret) + "): eyeD3 does not seem to be installed. Please install the command-line tool eyeD3" # noqa E501
        # exit(1)

    # Download the latest version of youtube-dl
    if not os.path.exists("./bin"):
        os.makedirs("./bin")
    if not os.path.exists("./bin/youtube-dl"):
        os.system("curl -L " +
                  "https://yt-dl.org/downloads/latest/youtube-dl " +
                  "-o ./bin/youtube-dl")
        os.system("chmod u+rx ./bin/youtube-dl")
    else:
        print("youtube-dl is already installed.")

    youtubeDlExec = os.path.abspath("./bin/youtube-dl")

    # Clean previous playlists
    pls = glob.glob('*.m3u')
    for pl in pls:
        os.remove(pl)

    # Check that we have the correct numebr of arguments
    if(len(sys.argv) != 2):
        print("Wrong number of arguments")
        print("Usage: " + sys.argv[0] + " list.csv")
        print("The expected format for the csv file is:")
        print("Playlistname,SongNumber,SongTitle,Artist,Youtube link")
        exit(1)

    playlistID = 0
    playlistName = ""
    playlistPath = ""

    # Move to the directory with the csv file. Output will be here
    outputPath = os.path.dirname(os.path.abspath(sys.argv[1]))
    os.chdir(outputPath)

    # Make a directory for the current blindtest
    blindtestPath, _ = os.path.splitext(sys.argv[1])
    blindtestPath = blindtestPath.replace(" ", "_")
    if(not os.path.exists(blindtestPath)):
        os.mkdir(blindtestPath)

    # Move to the directory of the blindtest
    os.chdir(blindtestPath)

    # Download vlc for windows user
    if(not os.path.exists("vlc-3.0.8-win32.zip")):
        os.system("wget https://get.videolan.org/vlc/3.0.8/win32/" +
                  "vlc-3.0.8-win32.zip")
    if(not os.path.exists("vlc-3.0.8-win64.zip")):
        os.system("wget https://get.videolan.org/vlc/3.0.8/win64/" +
                  "vlc-3.0.8-win64.zip")

    # Copy the blindtest file
    shutil.copyfile(sys.argv[1], "./" + os.path.basename(sys.argv[1]))

    # First download data from youtube
    csvfile = open(os.path.basename(sys.argv[1]), "r")
    csvdata = csv.reader(csvfile, delimiter=',')

    track_num = 1

    for row in csvdata:
        # FIXME This doesn't need to be done at each iteration
        # If we have 5 rows, then the order is:
        # PlaylistName, Order, Artist, Title, Youtube URL
        # If we have 4 rows, then the order is:
        # PlaylistName, Artist, Title, Youtube URL
        c_playlist = 0
        if len(row) == 0:
            exit(1)

        if len(row) == 5:
            c_artist = 2
            c_title = 3
            c_url = 4
        if len(row) == 4:
            c_artist = 1
            c_title = 2
            c_url = 3

        # Find if the current row has a youtube link
        # for a video we can download
        if(row[c_url].find("://www.youtube.com") != -1
           or row[c_url].find("http") != -1):

            print(row)

            # Check if we are attempting to download a playlist
            # if so -> error
            if(row[c_url].find("&list=") != -1):
                print("You are attempting to download a playlist. " +
                      "This might end up with a error.")
                print("Please fix the link.")
                exit(1)

            # When the playlist name changes:
            # Force an id before the playlist name
            # So we get the playlists in the order they have been designed
            if(row[c_playlist] != playlistName):
                playlistName = row[c_playlist]
                playlistID = playlistID + 1
                playlistPath = "./" + str(playlistID) + "." + row[c_playlist]
                # We also reinitialize the playlist m3u file to ensure
                # not appending at each successive execution of the script
                if(os.path.exists(playlistPath + ".m3u")):
                    os.remove(playlistPath + ".m3u")

                # Reset the track number
                track_num = 1

            print(playlistName + " " + str(playlistID))

            # Create a directory for the playlist if it doesn't exist
            if(not os.path.exists(playlistPath)):
                os.mkdir(playlistPath)

            # Manipulate file name so it is ok
            fprefix = str(track_num) + "."
            fprefix = fprefix + row[c_title] + "_-_" + row[c_artist]
            # Remove spaces
            fprefix = fprefix.replace(" ", "_")
            # Remove quotes
            fprefix = fprefix.replace("'", "_")
            # Remove slashes
            fprefix = fprefix.replace("/", "_")
            # Remove interrogation points
            fprefix = fprefix.replace("?", "_")
            # Remove newlines
            fprefix = fprefix.replace("\n", "")

            # Remove accents
            # fprefix = remove_accents(fprefix)

            fprefix = playlistPath + "/" + fprefix

            f = glob.glob(fprefix + ".*")
            if(len(f) > 0):
                print("The file for " + f[0] + " already exists. Skipping")
            else:
                filename = "\"" + fprefix + ".%(ext)s\""
                print(filename)

                # Go into the directory of the current playlist
                cmd = youtubeDlExec + " --restrict-filenames -o " + \
                    filename + " -x \"" + row[c_url] + "\" --audio-format mp3"
                print(cmd)
                os.system(cmd)

            # Add the mp3 to the playlist
            # find it back with the correct extension
            print(fprefix + ".*")
            f = glob.glob(fprefix + ".*")
            print(f)
            if(len(f) > 0):
                # Add the mp3 to the playlist
                playlist = open(playlistPath + ".m3u", "a")
                playlist.write(f[0] + "\n")
                playlist.close()

                # Change the track number to match the correct number
                # Tag through the command line
                # cmd = "eyeD3 -n " + row[1] + " -a \"" + row[2] + "\" -t \"" + row[3] + "\" " + f[0] # noqa E501
                # print cmd
                # os.system(cmd)
                # Tag using the python interface
                audiofile = eyed3.load(f[0])
                audiofile.initTag()
                # audiofile.tag.artist = unicode(row[c_artist])
                # audiofile.tag.title = unicode(row[c_title])
                audiofile.tag.artist = row[c_artist]
                audiofile.tag.title = row[c_title]
                audiofile.tag.track_num = track_num

                audiofile.tag.save()
            else:
                print("Couldn't find downloaded file")
                exit(1)

        # No youtube link
        else:
            print("No Youtube link for entry " +
                  playlistPath + "/" + track_num)

        # Increment the track number
        track_num = track_num + 1

    # Grep all the mp3 files
    # and adjust the gain with mp3gain
    if(mp3GainExec != ""):
        matches = []
        for root, dnames, fnames in os.walk('.'):
            for fname in fnmatch.filter(fnames, '*.mp3'):
                matches.append("\"" + os.path.join(root, fname) + "\"")

        print("matches=" + str(matches))
        os.system(mp3GainExec + " -r " + " ".join(matches))
    else:
        print("The gain has not been corrected as mp3gain is unavailable.")

    # Move to the previous directory
    # And make an archive
    os.chdir("..")
    # if(not os.path.exists(blindtestPath + ".zip")):
    print("Archiving " + blindtestPath + " ...")
    shutil.make_archive(blindtestPath, "zip",
                        base_dir=os.path.basename(blindtestPath))

    return 0


# Trick for reusing the script as a module
if __name__ == '__main__':
    main()
