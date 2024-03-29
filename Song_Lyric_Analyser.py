"""
Song Lyric Analyser is a desk top application that allows the user to 
calculate the average number of words in a song by a particular artist.

This class module uses PyQt5 to create the GUI for the Song Lyric Analyser
application.  After the user inputs the name of an artist, it uses 
the MusicBrainzngs API (https://pypi.org/project/musicbrainzngs/)
to retrieve the song list for that artist. It then
uses the LyricsGenius API to retrieve the lyrics for each song in the 
song list.  The number of words in each song is counted and used to 
calculate the word average for a song by the artist.

After entering the name of the artist, the user may search for videos of 
them on YouTube.

This is the start-up file for this application. """
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


class MainWindow(QMainWindow):
    """This class subclasses PyQt's QMainWindow to create the application's main window"""
    def __init__(self):
        try:
            super().__init__()
            # Each request sent to MusicBrainz needs to include a User-Agent header
            musicbrainzngs.set_useragent(
            "Song_Lyric_Analyser", "1.0", contact="s.shillitoe1@ntlworld.com")

            #Set up thread pool
            self.threadpool = QThreadPool()
            print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

            self.artist_name = ""
            self.song_list = []
            self.list_song_word_count = []

            self.setUpUI()
            self.connectSignalsToSlots()
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.__init__: ' + str(e))


    def setUpUI(self):
        """This function creates the GUI using PyQt5"""
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
            self.artist_name_widget = QLineEdit()
            self.artist_name_widget.setToolTip("Type the name of the artist")
            self.mainLayout.addWidget(self.instructionsLabel)
            self.mainLayout.addWidget(self.artist_label)
            self.mainLayout.addWidget(self.artist_name_widget)
        
            self.song_list_search_button = QPushButton("Search for artist's song list")
            self.song_list_search_button.setToolTip("Search for artist's song list")
            self.song_list_search_button.setEnabled(False)
           
            self.youtube_button = QPushButton("Search for artist on YouTube")
            self.youtube_button.setToolTip("Search for the artist on YouTube")
            
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


    def connectSignalsToSlots(self):
        self.artist_name_widget.textEdited.connect(self.enable_search_buttons)
        self.artist_name_widget.textChanged.connect(self.set_artist_name)
        self.artist_name_widget.textChanged.connect(self.update_button_text)
        self.artist_name_widget.returnPressed.connect(self.get_song_list)
        self.song_list_search_button.clicked.connect(self.get_song_list)
        self.youtube_button.clicked.connect(self.find_artist_on_YouTube)
        self.average_button.clicked.connect(self.calculate_song_word_average)


    def set_artist_name(self):
        try:
            self.artist_name = self.artist_name_widget.text()
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.set_artist_name: ' + str(e))

    
    def update_button_text(self):
        """Updates button text with the artist's name as the user types the artist's name"""
        try:
            self.song_list_search_button.setText(
                "Search for {}'s song list".format(self.artist_name))
            self.youtube_button.setText("Search for {} on YouTube".format(self.artist_name))
            self.average_button.setText("Calculate the average number of words in a song by {}".format(self.artist_name))
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.update_button_text: ' + str(e))


    def find_artist_on_YouTube(self):
        """Opens a browser showing youtube search results for the artist"""
        try:
            search_url = "https://www.youtube.com/results?search_query=" + self.artist_name
            webbrowser.open(search_url)
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.find_artist_on_YouTube: ' + str(e))


    def enable_search_buttons(self):
        """Enables search buttons when the user enters an artist's name"""
        try:
            if len(self.artist_name_widget.text()) == 0:
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
                            self.artist_name, len(self.song_list)))
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
                    artistname=self.artist_name, 
                    limit=limit, offset=offset, strict=True)
            
                if song_result:
                    for song in song_result["recording-list"]:
                        song_title = song["title"]
                        #use a regular expression to 'clean up' the song titles
                        #remove [] and () and their enclosed text from song title
                        #using a regular expression
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
                                self.artist_name))
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
            url_query = url + self.artist_name + '/' + song_title
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
    

    def calculate_list_average(self, listOfNumbers=None):
        """Calculates the average value of a list of numbers"""
        try:
            if listOfNumbers is not None:
                return int(sum(listOfNumbers) / len(listOfNumbers))
            else:
                return 0
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.calculate_list_average: ' + str(e))


    def calculate_song_word_average(self):
        """This function uses multithreading to calculate the average number of words in an artist's song.
        Multithreading prevents the appearance of the application freezing by updating a 
        progress bar as the artist's song list is iterated over, the number of words in
        each song is determined and appended to a list. The average is calculated from this list."""
        try:
            self.progress.setMaximum(len(self.song_list))
            self.statusBar.showMessage("Calculating the average number of words in a song by the {}".format(self.artist_name))
            QApplication.processEvents()

            #This is a quicker way to calculate 
            #number of words in a song using multithreading 
            #but it does not allow communication with 
            #the user about calculation progress via the progress bar
            #with concurrent.futures.ThreadPoolExecutor() as executor:
            #     executor.map(self.lyric_search, self.song_list)

            lyricFinder = LyricFinder(self.song_list, self.artist_name)
            lyricFinder.signals.progress.connect(self.update_progress_bar)
            #show the user which song is being processed
            lyricFinder.signals.status.connect(self.update_status_bar)
            #add the number of words in each song to the list
            lyricFinder.signals.wordCount.connect(self.update_song_word_list)
            #calculation finished, so reset the progress bar
            lyricFinder.signals.finished.connect(self.reset_progress_bar)
            #calculation finished, so calculate the average number of words in an artist's song
            lyricFinder.signals.finished.connect(self.calculate_average_number_words_in_a_song)
            lyricFinder.signals.calculationTime.connect(self.finalise_status_bar)

            # Execute
            self.threadpool.start(lyricFinder)
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.calculate_song_word_average: ' + str(e))

            
    def update_progress_bar(self, song_number):
        try:
            self.progress.setValue(song_number)
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.update_progress_bar: ' + str(e))


    def update_status_bar(self, song_title):
        try:
            self.statusBar.showMessage("Processing a song called {}".format(song_title))
        except Exception as e:
            print('Error in function Song_Lyric_Analyser.update_status_bar: ' + str(e))


    def update_song_word_list(self, word_count):
        """word_count - Number of words in a song"""
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
                    "The average number of words in a song by {} is {}".format(self.artist_name, 
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

