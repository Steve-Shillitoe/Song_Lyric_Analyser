import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, \
                        QPushButton,  QWidget, \
                        QGridLayout, QLabel, QLineEdit, QPushButton, \
                        QAbstractItemView, QListWidget, QListWidgetItem, \
                        QMessageBox, QPlainTextEdit, QScrollBar, QProgressBar, \
                        QStatusBar

import musicbrainzngs
import lyricsgenius
import webbrowser
import re
import time
import concurrent.futures
#import json
#import requests
#from requests.exceptions import ConnectionError
import StyleSheet as styleSheet

MUSIC_GENIUS_ACCESS_TOKEN = "Xggm2iesVVTObjSTWDUIVfWoyGhftueOxOowgkCR5LKRyYS8Ml9K8oam4zBM3sR7"

# Subclass QMainWindow to customize your application's main window  
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Initialize user agent to DB
        musicbrainzngs.set_useragent(
        "Song_Lyric_Analyser", "1.0", contact="s.shillitoe1@ntlworld.com")

        self.setup_music_genius_lyric_finder() 

        self.selected_artist = ""
        self.song_list = []
        self.artist_list = []
        self.list_song_word_count = []

        self.setWindowTitle("Song Lyric Analyser")
        self.setWindowFlags(Qt.CustomizeWindowHint | 
                                    Qt.WindowCloseButtonHint | 
                                    Qt.WindowMinimizeButtonHint |
                                    Qt.WindowMaximizeButtonHint)
     
        self.setStyleSheet(styleSheet.SONG_LYRIC_ANALYSER_STYLE)
        self.mainLayout = QGridLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.mainLayout)
        # Set the central widget of the Window.
        self.setCentralWidget(self.widget)
        self.setGeometry(0, 0, 600, 900)
        #self.showMaximized()

        self.artist_label = QLabel("Artist")
        self.artist_name = QLineEdit()
        self.artist_name.textEdited.connect(self.enable_search_buttons)
        self.artist_name.textChanged.connect(self.set_artist_name)
        self.artist_name.textChanged.connect(self.updateButtonText)
        self.artist_name.returnPressed.connect(self.get_song_list)
        self.artist_name.setToolTip("Enter the name of the artist")
        self.mainLayout.addWidget(self.artist_label, 0,0)
        self.mainLayout.addWidget(self.artist_name, 0,1)

        self.song_list_search_button = QPushButton("Search for artist's song list")
        self.song_list_search_button.setToolTip("Search for artist's song list")
        self.song_list_search_button.setEnabled(False)
        self.song_list_search_button.clicked.connect(self.get_song_list)
        self.youtube_button = QPushButton("Search for artist on YouTube")
        self.youtube_button.setToolTip("Search for the artist on YouTube")
        self.youtube_button.clicked.connect(self.find_artist_on_YouTube)
        self.youtube_button.setEnabled(False)
        self.mainLayout.addWidget(self.song_list_search_button, 1,1)
        self.mainLayout.addWidget(self.youtube_button, 1,2)

        self.song_list_widget = QListWidget()
        self.song_list_widget.sortItems(Qt.AscendingOrder)
        self.song_list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.song_list_widget.itemClicked.connect(lambda item: self.lyric_display(item.text()))
        self.song_label = QLabel("Songs List")
        
        self.mainLayout.addWidget(self.song_label, 2,1)
        self.mainLayout.addWidget(self.song_list_widget, 3,1)

        self.lyrics = QPlainTextEdit()
        scroll_bar = QScrollBar()
        self.lyrics.setVerticalScrollBar(scroll_bar)
        self.lyrics_label = QLabel("Lyrics")
        self.lyrics_label.setWordWrap(True)
        self.number_words_label = QLabel("Number of words in the song")
        self.average_button = QPushButton("Calculate average number of words in a song by this artist")
        self.average_button.clicked.connect(self.calculate_song_word_average)
        self.average_button.setEnabled(False)
        self.average_button.setToolTip("Calculates the average number of words in the artists songs")
        self.average_number_words_label = QLabel("Average number of words in a song")
        self.average_number_words_label.hide()
        self.progress = QProgressBar()
        self.progress.hide()
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        self.mainLayout.addWidget(self.lyrics_label, 4,1)
        self.mainLayout.addWidget(self.lyrics, 5,1)
        self.mainLayout.addWidget(self.number_words_label, 6,1)
        self.mainLayout.addWidget(self.average_button, 7,1)
        self.mainLayout.addWidget(self.average_number_words_label, 8,1)  
        self.mainLayout.addWidget(self.progress, 9,1)
    
    
    def set_artist_name(self):
        self.selected_artist = self.artist_name.text()
        
    
    def updateButtonText(self):
        self.song_list_search_button.setText(
            "Search for {}'s song list".format(self.selected_artist))
        self.youtube_button.setText("Search for {} on YouTube".format(self.selected_artist))
        self.average_button.setText("Calculate the average number of words in a song by {}".format(self.selected_artist))


    def find_artist_on_YouTube(self):
        search_url = "https://www.youtube.com/results?search_query=" + self.selected_artist
        # Open URL in browser
        webbrowser.open(search_url)


    def enable_search_buttons(self):
        if len(self.artist_name.text()) == 0:
            self.song_list_search_button.setEnabled(False)
            self.youtube_button.setEnabled(False)
            self.average_button.setEnabled(False)
        else:
            self.song_list_search_button.setEnabled(True)
            self.youtube_button.setEnabled(True)
            


    def setup_music_genius_lyric_finder(self):
        self.music_genius = lyricsgenius.Genius(MUSIC_GENIUS_ACCESS_TOKEN)
        self.music_genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
        self.music_genius.skip_non_songs = True
        # Exclude songs with these words in their title
        #This does not seem to work, so use a regular expression 
        #at the point of need instead
        self.music_genius.excluded_terms = ["(Remix)", "(Live)", "(remix)", 
                                            "(live)", "edit", "(demo)"]


    def get_song_list(self):
        try:
            self.average_button.setEnabled(False)
            self.song_list_widget.clear()

            offset = 0
            limit = 100
            QApplication.setOverrideCursor(Qt.WaitCursor)
            while True:
                song_result = musicbrainzngs.search_recordings(
                    artistname=self.selected_artist, 
                    limit=limit, offset=offset, strict=True)
            
                if song_result:
                    for song in song_result["recording-list"]:
                        song_title = song["title"]
                        #remove [] and () and their enclosed text from song title
                        song_title = re.sub("[\(\[].*?[\)\]]", "", song_title)
                        song_title = song_title.strip().lower()
                        self.song_list.append(song_title)
                    #increment the offset to get the next 100 song titles
                    offset += limit

                if len(song_result["recording-list"]) == 0 or offset > 400:
                    break
            QApplication.restoreOverrideCursor()

            if len(self.song_list) == 0:
                self.song_label.setText("No song titles found for {}".format(
                                self.selected_artist))
                self.statusBar.showMessage("No song titles found")
            else:
                self.average_button.setEnabled(True)
                #Remove duplicates
                self.song_list = list(set(self.song_list))
                self.song_list.sort()
                #Build list of songs
                for song in self.song_list:
                    item = QListWidgetItem(song)
                    self.song_list_widget.addItem(item)
                self.song_label.setText("{} have {} song titles".format(
                                self.selected_artist, len(self.song_list)))
                self.statusBar.showMessage("Song title search finished")
        except Exception as e:
            print('Error in function get_song_list: ' + str(e))


    def lyric_display(self, song_title):
        self.lyrics.clear()
        lyrics = self.lyric_search(song_title)
        if lyrics is None:
            lyrics = "No lyrics were found for this song"
        else:
            self.lyrics_label.setText("Lyrics of {}".format(song_title))
            self.number_words_label.setText("Number of words in {} = {}"
                                        .format(song_title, self.word_count(lyrics)))
        self.lyrics.insertPlainText(lyrics)


    def lyric_search(self, song_title):
        try:
            QApplication.setOverrideCursor(Qt.WaitCursor)
            song = self.music_genius.search_song(song_title, self.selected_artist)
            QApplication.restoreOverrideCursor()
            if song:
                self.statusBar.showMessage("Lyrics found for {}".format(song_title))
                if song.lyrics is not None:
                    self.list_song_word_count.append(self.word_count(song.lyrics))
                    return song.lyrics
            else:
                return None
                self.statusBar.showMessage("No lyrics found")
                
        except Exception as e:
            print('Error in function lyric_search: ' + str(e))


    def redundant_lyric_search(self, song_title):
        """This function is redundant because the web service
       'https://api.lyrics.ovh/v1/' is unavailable"""
        try:
            url = 'https://api.lyrics.ovh/v1/' 
            url_query = url + self.selected_artist + '/' + song_title
            response = requests.get(url_query)
            lyrics = ""
            if response.status_code == 200:
                json_data = json.loads(response.content)
                lyrics = json_data['lyrics']
            elif response.status_code == 503:
                lyrics =  "service unavailable"
            
            return lyrics
        except ConnectionError:
            QMessageBox().critical(self, "The server does not exist", "{} server does not exist".format(url))
        except Exception as e:
            print('Error in function lyric_search: ' + str(e))
    

    def word_count(self, lyrics):
        try:
            word_list = lyrics.split()
            return len(word_list)
        except Exception as e:
            print('Error in function word_count when lyrics={}: '.format(lyrics) + str(e))


    def average(self,lst):
        if lst is not None:
            return int(sum(lst) / len(lst))
        else:
            return 0


    def calculate_song_word_average(self):
        try:
            self.statusBar.showMessage("Calculating the average number of words in a song by the {}".format(self.selected_artist))
            QApplication.processEvents()

            t1 = time.perf_counter()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                executor.map(self.lyric_search, self.song_list)
            t2 = time.perf_counter()
            
            self.statusBar.showMessage(f'Calculation finished in {t2-t1} seconds')
            averageNumberWords = self.average(self.list_song_word_count)
            self.average_number_words_label.show()
            self.average_number_words_label.setText(
                "The average number of words in a song by {} is {}".format(self.selected_artist, 
                                                                            averageNumberWords))
        except Exception as e:
            print(list_song_word_count)
            QApplication.restoreOverrideCursor()
            print('Error in function calculate_song_word_average: ' + str(e))

#with concurrent.futures.ThreadPoolExecutor() as executor:
 #   executor.map(download_image, img_urls)
def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()

