"""
This class module handles the retrieval of song lyrics and counting the number of words
they contain using multithreading.  The LyricsGenius API, https://pypi.org/project/lyricsgenius/
is used to retrieve the song lyrics for an artist/song title pair.
"""

import time
#LyricsGenius: a Python client for the Genius.com API
import lyricsgenius
#import PyQt5 multithreading support
from PyQt5.QtCore import Qt, QObject, QRunnable, pyqtSignal, pyqtSlot
#constant
LYRICS_GENIUS_ACCESS_TOKEN = "Xggm2iesVVTObjSTWDUIVfWoyGhftueOxOowgkCR5LKRyYS8Ml9K8oam4zBM3sR7"

class LyricFinderSignals(QObject):
  """Defines the signals available from a running LyricFinder thread that
  allow the threads running the song lyric searches to communicate with the 
  main thread running the application GUI.
  """
  progress = pyqtSignal(int)
  status = pyqtSignal(str)
  wordCount = pyqtSignal(int)
  finished = pyqtSignal(bool)
  calculationTime = pyqtSignal(float)
  

class LyricFinder(QRunnable):
    """
    This class inherits from QRunnable to handle LyricFinder thread setup, signals
    and wrap-up in the calculation of the average number of words in a song by
    a particular artist."""
    def __init__(self, songs, artist):
        """
        Input parameters:
        *****************
        songs - a list of song titles
        artist - the name of artist whose songs are the above song list.
        """
        try:
            super().__init__()
            self.song_list = songs
            self.artist = artist
            self.signals = LyricFinderSignals()
            self.setup_music_genius_lyric_finder() 
        except Exception as e:
            print('Error in function LyricFinder.__init__: ' + str(e))    
    

    def setup_music_genius_lyric_finder(self):
        try:
            self.music_genius = lyricsgenius.Genius(LYRICS_GENIUS_ACCESS_TOKEN)
            self.music_genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
            self.music_genius.skip_non_songs = True
            self.music_genius.excluded_terms = ["(Remix)", "(Live)", "(remix)", 
                                                "(live)", "edit", "(demo)" , "(mix)"]
        except Exception as e:
            print('Error in function LyricFinder.setup_music_genius_lyric_finder: '.format(lyrics) + str(e))


    def word_count(self, lyrics=None):
        """Returns the number of words in a song."""
        try:
            if lyrics is not None:
                word_list = lyrics.split()
                return len(word_list)
            else:
                return 0
        except Exception as e:
            print('Error in function LyricFinder.word_count when lyrics={}: '.format(lyrics) + str(e))


    def get_number_words_in_one_song(self, song_title):
        try:
            #search for the song
            song = self.music_genius.search_song(song_title, self.artist)
            if song:
                if song.lyrics is not None:
                    return self.word_count(song.lyrics)
            else:
                return 0  
        except Exception as e:
            print('Error in function LyricFinder.get_number_words_in_one_song with song title {}: '.format(song_title) + str(e))    
    

    @pyqtSlot()
    def run(self):
        """Reimplementation of the run() virtual function"""
        try:
            start_time = time.perf_counter()
            for count, song_title in enumerate(self.song_list):
                self.signals.status.emit(song_title)
                number_words= self.get_number_words_in_one_song(song_title)
                self.signals.wordCount.emit(number_words)
                self.signals.progress.emit(count)
        
            end_time = time.perf_counter()
            self.signals.calculationTime.emit(round((end_time-start_time),3))
            self.signals.finished.emit(True)
        except Exception as e:
            print('Error in function LyricFinder.run: ' + str(e))   

