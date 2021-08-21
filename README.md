# Song_Lyric_Analyser
# Introduction
Song Lyric Analyser is a desk top application that allows the user to 
calculate the average number of words in a song by a particular artist.

It uses PyQt5 to create the GUI for the Song Lyric Analyser
application.  After the user inputs the name of an artist, it uses 
the MusicBrainzngs API to retrieve the song list for that artist. It then
uses the LyricsGenius API to retrieve the lyrics for each song in the 
song list using multithreading.  The number of words in each song is counted and used to 
calculate the word average for a song by the artist.

Instructions on how to use this application are displayed at the top of the
start-up screen. 

After entering the name of the artist, the user may also search for videos of 
them on YouTube.

# Installation.
You may run this application in your favourite Python development environment.
In order to do this you will need to install the following packages:
    PyQt5
    LyricsGenius
    MusicBrainzngs
   
on Windows you may use PIP install; e.g.,
    pip install pyqt5 \n
    pip install lyricsgenius \n
    pip install musicbrainzngs\n
    
# Running the application
The start-up file for this application is 
    Song_Lyric_Analyser.py
    
The files Song_Lyric_Analyser.sln and Song_Lyric_Analyser.pyproj are only
needed if you wish to view the source code in MS Visual Studio.
Otherwise they can be ignored or even deleted with no deleterious side-effects!


