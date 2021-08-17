import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, \
                        QPushButton, QVBoxLayout, QWidget, \
                        QGridLayout, QLabel, QLineEdit, QPushButton, \
                        QAbstractItemView, QListWidget, QListWidgetItem, \
                        QMessageBox, QPlainTextEdit, QScrollBar

import musicbrainzngs
import lyricsgenius
#import webbrowser
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
        self.search_button = QPushButton("Search")
        self.search_button.setToolTip("Search for artist")
        self.youtube_button = QPushButton("Search for artist on YouTube")
        self.youtube_button.setToolTip("Search for the artist on YouTube")
        self.youtube_button.setEnabled(False)
        self.mainLayout.addWidget(self.artist_label, 0,0)
        self.mainLayout.addWidget(self.artist_name, 0,1)
        self.mainLayout.addWidget(self.search_button, 1,1)
        self.search_button.clicked.connect(self.artist_search)
        self.artist_list = QListWidget()
        self.artist_list.setMaximumHeight=30
        self.artist_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.mainLayout.addWidget(self.artist_list, 2,1)
        self.mainLayout.addWidget(self.youtube_button, 2,2, alignment=Qt.AlignTop)
        self.artist_list.itemClicked.connect(lambda item: self.song_search(item))
        self.artist_list.itemClicked.connect(lambda item: 
                                             self.youtube_button.setEnabled(True))

        self.song_list_widget = QListWidget()
        self.song_list_widget.sortItems(Qt.AscendingOrder)
        self.song_list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.song_list_widget.itemClicked.connect(lambda item: self.lyric_display(item.text()))
        self.song_label = QLabel("Songs")
        self.mainLayout.addWidget(self.song_label, 3,1)
        self.mainLayout.addWidget(self.song_list_widget, 4,1)

        self.lyrics = QPlainTextEdit()
        scroll_bar = QScrollBar()
        # setting style sheet to the scroll bar
        scroll_bar.setStyleSheet("background : lightgreen;")
        self.lyrics.setVerticalScrollBar(scroll_bar)
        self.lyrics_label = QLabel("Lyrics")
        self.lyrics_label.setWordWrap(True)
        self.number_words_label = QLabel("Number of words in the song")
        self.average_button = QPushButton("Calculate song word average")
        self.average_button.setToolTip("Calculates the average number of words in the artists songs")
        self.average_number_words_label = QLabel("Average number of words in a song")

        self.mainLayout.addWidget(self.lyrics_label, 5,1)
        self.mainLayout.addWidget(self.lyrics, 6,1)
        self.mainLayout.addWidget(self.number_words_label, 7,1)
        self.mainLayout.addWidget(self.average_button, 8,1)
        self.mainLayout.addWidget(self.average_number_words_label, 9,1)

     
        self.selected_artist = ""
        #self.selected_song = ""
        self.song_list = []
        self.music_genius = lyricsgenius.Genius(MUSIC_GENIUS_ACCESS_TOKEN)
        self.music_genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
        self.music_genius.skip_non_songs = True
        self.music_genius.excluded_terms = ["(Remix)", "(Live)", "(remix)", "(live)", "edit"] # Exclude songs with these words in their title

            # Search for Artist
    def artist_search(self):
        self.song_list_widget.clear()
        self.artist_list.clear()
        self.song_label.setText("Songs")
        search_string = self.artist_name.text()

        if search_string:
            artist_result = musicbrainzngs.search_artists(
                artist=search_string, limit=100, offset=None, strict=True)
          
            if int(artist_result["artist-count"])> 0 :
                for artist in artist_result["artist-list"]:
                    item = QListWidgetItem(artist["name"])
                    self.artist_list.addItem(item)
            else:
                QMessageBox().information(self, 
                                            "Artist Search", 
                                            "No songs were found for {}.".format(search_string))  
          
        else:
            QMessageBox().critical(self, "Artist Name", "Please enter the name of the artist.") 
          

    def song_search(self, artist):
        self.song_list_widget.clear()
        self.selected_artist = artist.text()

        offset = 0
        limit = 100
        while True:
            song_result = musicbrainzngs.search_recordings(
                artistname=self.selected_artist, 
                limit=limit, offset=offset, strict=True)
            print("While iterated {}".format(len(song_result["recording-list"])))
            for song in song_result["recording-list"]:
                self.song_list.append(song["title"])
            offset += limit
            if len(song_result["recording-list"]) == 0 or offset > 600:
                break

        #Remove duplicates
        self.song_list = list(set(self.song_list))
        self.song_list.sort()
        for song in self.song_list:
            item = QListWidgetItem(song)
            self.song_list_widget.addItem(item)
        self.song_label.setText("{} have {} songs".format(
                        self.selected_artist, len(self.song_list)))


    def lyric_display(self, song_name):
        self.lyrics.clear()
        lyrics = self.lyric_search(song_name)
        self.lyrics.insertPlainText(lyrics)
        self.lyrics_label.setText("Lyrics of {}".format(song_name))
        self.number_words_label.setText("Number of words in the song = {}"
                                        .format(self.word_count(lyrics)))

    def lyric_search(self, song_name):
        try:
            song = self.music_genius.search_song(song_name, self.selected_artist)
            return song.lyrics
        except Exception as e:
            print('Error in function lyric_search: ' + str(e))


    def lyric_search_redundant(self, song_name):
        """This function is redundant because the web service
       'https://api.lyrics.ovh/v1/' is unavailable"""
        try:
            url = 'https://api.lyrics.ovh/v1/' 
            url_query = url + self.selected_artist + '/' + song_name
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
        word_list = lyrics.split()
        return len(word_list)


    def calculate_song_word_average(self):
        list_song_word_count = []
        for item in self.song_list_widget:
            song_title = item.text()
            list_song_word_count.append(word_count(lyrics))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()

