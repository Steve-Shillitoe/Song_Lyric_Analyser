import sys
from PyQt5.QtCore import Qt, QThreadPool
from PyQt5.QtWidgets import QApplication, QMainWindow, \
                        QPushButton,  QWidget, \
                        QHBoxLayout, QLabel, QLineEdit, QPushButton, \
                        QAbstractItemView, QListWidget, QListWidgetItem, \
                        QMessageBox, QProgressBar, \
                        QStatusBar, QVBoxLayout

import musicbrainzngs
import webbrowser
import re
#Uncomment the following 2 lines if the alternative, faster
#form of multithreading is to be used
#import concurrent.futures
#import json
#uncomment the following 2 lines of code if the
#web service 'https://api.lyrics.ovh/v1/' is to 
#be used to find song lyrics 
#import requests
#from requests.exceptions import ConnectionError
import StyleSheet as styleSheet
from LyricFinder import LyricFinder

INSTRUCTIONS = "To find the average number of words in an artist's song, first enter their" + \
            " name in the textbox below. \nThen click the 'Search for artist's song list' button" + \
            " to get the artist's song list. \nFinally click the 'Calculate average number of words in a song by this artist'" + \
            " button to calculate the average number of words in a song"

# Subclass QMainWindow to customize your application's main window  
class MainWindow(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            # Initialize user agent to DB
            musicbrainzngs.set_useragent(
            "Song_Lyric_Analyser", "1.0", contact="s.shillitoe1@ntlworld.com")

            self.threadpool = QThreadPool()
            print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

            self.selected_artist = ""
            self.song_list = []
            self.artist_list = []
            self.list_song_word_count = []

            self.setUpUI()
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.__init__: ' + str(e))


    def setUpUI(self):
        try:
            self.setWindowTitle("Song Lyric Analyser")
            self.setWindowFlags(Qt.CustomizeWindowHint | 
                                        Qt.WindowCloseButtonHint | 
                                        Qt.WindowMinimizeButtonHint |
                                        Qt.WindowMaximizeButtonHint)
        
            self.setStyleSheet(styleSheet.SONG_LYRIC_ANALYSER_STYLE)
            self.mainLayout =  QVBoxLayout()
            self.widget = QWidget()
            self.widget.setLayout(self.mainLayout)
            # Set the central widget of the Window.
            self.setCentralWidget(self.widget)
            self.setGeometry(0, 0, 600, 900)
            #self.showMaximized()
        
            self.instructionsLabel = QLabel(INSTRUCTIONS)
            self.instructionsLabel.setWordWrap(True)
            self.artist_label = QLabel("Type the name of an artist below.")
            self.artist_name = QLineEdit()
            self.artist_name.textEdited.connect(self.enable_search_buttons)
            self.artist_name.textChanged.connect(self.set_artist_name)
            self.artist_name.textChanged.connect(self.update_button_text)
            self.artist_name.returnPressed.connect(self.get_song_list)
            self.artist_name.setToolTip("Type the name of the artist")
            self.mainLayout.addWidget(self.instructionsLabel)
            self.mainLayout.addWidget(self.artist_label)
            self.mainLayout.addWidget(self.artist_name)
        
            self.song_list_search_button = QPushButton("Search for artist's song list")
            self.song_list_search_button.setToolTip("Search for artist's song list")
            self.song_list_search_button.setEnabled(False)
            self.song_list_search_button.clicked.connect(self.get_song_list)
            self.youtube_button = QPushButton("Search for artist on YouTube")
            self.youtube_button.setToolTip("Search for the artist on YouTube")
            self.youtube_button.clicked.connect(self.find_artist_on_YouTube)
            self.youtube_button.setEnabled(False)
            self.horizontalLayout = QHBoxLayout()
            self.horizontalLayout.addWidget(self.song_list_search_button)
            self.horizontalLayout.addWidget(self.youtube_button)
            self.mainLayout.addLayout(self.horizontalLayout)
        
            self.song_list_widget = QListWidget()
            self.song_list_widget.sortItems(Qt.AscendingOrder)
            self.song_list_widget.setSelectionMode(QAbstractItemView.SingleSelection)
            self.song_label = QLabel("Song List")
            self.mainLayout.addWidget(self.song_label)
            self.mainLayout.addWidget(self.song_list_widget)
        
            self.average_button = QPushButton("Calculate average number of words in a song by this artist")
            self.average_button.clicked.connect(self.calculate_song_word_average)
            self.average_button.setEnabled(False)
            self.average_button.setToolTip("Calculates the average number of words in the artists songs")
            self.average_number_words_label = QLabel("Average number of words in a song")
            self.average_number_words_label.hide()
            self.progress = QProgressBar()
            self.statusBar = QStatusBar()
            self.setStatusBar(self.statusBar)
            self.mainLayout.addWidget(self.average_button)
            self.mainLayout.addWidget(self.average_number_words_label)  
            self.mainLayout.addWidget(self.progress)
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.setUpUI: ' + str(e))


    def set_artist_name(self):
        try:
            self.selected_artist = self.artist_name.text()
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.set_artist_name: ' + str(e))

    
    def update_button_text(self):
        try:
            self.song_list_search_button.setText(
                "Search for {}'s song list".format(self.selected_artist))
            self.youtube_button.setText("Search for {} on YouTube".format(self.selected_artist))
            self.average_button.setText("Calculate the average number of words in a song by {}".format(self.selected_artist))
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.update_button_text: ' + str(e))


    def find_artist_on_YouTube(self):
        try:
            search_url = "https://www.youtube.com/results?search_query=" + self.selected_artist
            webbrowser.open(search_url)
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.find_artist_on_YouTube: ' + str(e))


    def enable_search_buttons(self):
        try:
            if len(self.artist_name.text()) == 0:
                self.song_list_search_button.setEnabled(False)
                self.youtube_button.setEnabled(False)
                self.average_button.setEnabled(False)
            else:
                self.song_list_search_button.setEnabled(True)
                self.youtube_button.setEnabled(True)
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.enable_search_buttons: ' + str(e))
            

    def build_song_list_widget(self):
        try:
            #Remove duplicates
            self.song_list = list(set(self.song_list))
            self.song_list.sort()
            #Build list of songs
            for song in self.song_list:
                item = QListWidgetItem(song)
                self.song_list_widget.addItem(item)
            self.song_label.setText("{} have {} song titles".format(
                            self.selected_artist, len(self.song_list)))
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.build_song_list_widget: ' + str(e))
            

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
                
                #Stop the while loop when there are no more songs to retrieve or
                #when after 4 iterations.
                if len(song_result["recording-list"]) == 0 or offset > 400:
                    break
            QApplication.restoreOverrideCursor()

            if len(self.song_list) == 0:
                self.song_label.setText("No song titles found for {}".format(
                                self.selected_artist))
                self.statusBar.showMessage("No song titles found")
            else:
                self.average_button.setEnabled(True)
                self.build_song_list_widget()
                self.statusBar.showMessage("Song list search finished")
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.get_song_list: ' + str(e))


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
            print('Error in function redundant_lyric_search: ' + str(e))
    

    def calculate_list_average(self, listOfNumbers):
        try:
            if listOfNumbers is not None:
                return int(sum(listOfNumbers) / len(listOfNumbers))
            else:
                return 0
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.calculate_list_average: ' + str(e))


    def calculate_song_word_average(self):
        try:
            self.progress.setMaximum(len(self.song_list))
            self.statusBar.showMessage("Calculating the average number of words in a song by the {}".format(self.selected_artist))
            QApplication.processEvents()

            #This is a quicker way to calculate 
            #number of words in a song using multithreading 
            #but it does not allow communication with 
            #the user about calculation progress via the progress bar
            #with concurrent.futures.ThreadPoolExecutor() as executor:
            #     executor.map(self.lyric_search, self.song_list)

            lyricFinder = LyricFinder(self.song_list, self.selected_artist)
            lyricFinder.signals.progress.connect(self.update_progress)
            lyricFinder.signals.status.connect(self.update_status_bar)
            lyricFinder.signals.wordCount.connect(self.update_song_word_list)
            lyricFinder.signals.finished.connect(self.reset_progress_bar)
            lyricFinder.signals.finished.connect(self.calculate_average_number_words_in_a_song)
            lyricFinder.signals.calculationTime.connect(self.finalise_status_bar)

            # Execute
            self.threadpool.start(lyricFinder)
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.calculate_song_word_average: ' + str(e))


    def update_progress(self, progress):
        try:
            self.progress.setValue(progress)
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.update_progress: ' + str(e))


    def update_status_bar(self, song_title):
        try:
            self.statusBar.showMessage("Processing a song called {}".format(song_title))
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.update_status_bar: ' + str(e))


    def update_song_word_list(self, word_count):
        try:
            self.list_song_word_count.append(word_count)
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.update_song_word_list: ' + str(e))


    def reset_progress_bar(self, finished):
        try:
            if finished:
                self.progress.reset()
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.reset_progress_bar: ' + str(e))   


    def finalise_status_bar(self, calculationTime):
        try:
            self.statusBar.showMessage("Calculation time = {}s".format(calculationTime))
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.finalise_status_bar: ' + str(e))


    def calculate_average_number_words_in_a_song(self, finished):
        try:
            if finished:
                averageNumberWords = self.calculate_list_average(self.list_song_word_count)
                self.average_number_words_label.show()
                self.average_number_words_label.setText(
                    "The average number of words in a song by {} is {}".format(self.selected_artist, 
                                                                            averageNumberWords))
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.calculate_average_number_words_in_a_song: ' + str(e))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()

