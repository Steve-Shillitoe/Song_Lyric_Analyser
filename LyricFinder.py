import time
import lyricsgenius
from PyQt5.QtCore import Qt, QObject, QRunnable, pyqtSignal, pyqtSlot
#constants
MUSIC_GENIUS_ACCESS_TOKEN = "Xggm2iesVVTObjSTWDUIVfWoyGhftueOxOowgkCR5LKRyYS8Ml9K8oam4zBM3sR7"

class LyricFinderSignals(QObject):
  """Defines the signal, progress, available from a running LyricFinder thread
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
        super().__init__()
        self.song_list = songs
        self.artist = artist
        self.signals = LyricFinderSignals()
        self.setup_music_genius_lyric_finder() 
    

    def setup_music_genius_lyric_finder(self):
        self.music_genius = lyricsgenius.Genius(MUSIC_GENIUS_ACCESS_TOKEN)
        self.music_genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
        self.music_genius.skip_non_songs = True
        self.music_genius.excluded_terms = ["(Remix)", "(Live)", "(remix)", 
                                            "(live)", "edit", "(demo)" , "(mix)"]


    def word_count(self, lyrics):
        try:
            if lyrics is not None:
                word_list = lyrics.split()
                return len(word_list)
            else:
                return 0
        except Exception as e:
            print('Error in function word_count when lyrics={}: '.format(lyrics) + str(e))


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
            print('Error in function get_number_words_in_one_song: ' + str(e))    
    

    @pyqtSlot()
    def run(self):
        t1 = time.perf_counter()
        for count, song_title in enumerate(self.song_list):
            self.signals.status.emit(song_title)
            number_words= self.get_number_words_in_one_song(song_title)
            self.signals.wordCount.emit(number_words)
            self.signals.progress.emit(count)
        
        t2 = time.perf_counter()
        self.signals.calculationTime.emit(t2-t1)
        self.signals.finished.emit(True)


