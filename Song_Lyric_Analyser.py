import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, \
                        QPushButton, QVBoxLayout, QWidget, \
                        QGridLayout, QLabel, QLineEdit, QPushButton, \
                        QAbstractItemView, QListWidget, QListWidgetItem, \
                        QMessageBox, QPlainTextEdit, QScrollBar

import musicbrainzngs
import lyricsgenius
import webbrowser


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
      self.mainLayout.addWidget(self.artist_label, 0,0)
      self.mainLayout.addWidget(self.artist_name, 0,1)
      self.mainLayout.addWidget(self.search_button, 1,1)
      self.search_button.clicked.connect(self.artist_search)
      self.artist_list = QListWidget()
      self.artist_list.setMaximumHeight=30
      self.artist_list.setSelectionMode(QAbstractItemView.SingleSelection)
      self.mainLayout.addWidget(self.artist_list, 2,1)
      self.artist_list.itemClicked.connect(lambda item: self.song_search(item))

      self.song_list = QListWidget()
      self.song_list.sortItems(Qt.AscendingOrder)
      self.song_list.setSelectionMode(QAbstractItemView.SingleSelection)
      self.song_list.itemClicked.connect(lambda item: self.lyric_search(item))
      self.mainLayout.addWidget(self.song_list, 3,1)

      self.lyrics = QPlainTextEdit()
      scroll_bar = QScrollBar()
      # setting style sheet to the scroll bar
      scroll_bar.setStyleSheet("background : lightgreen;")
      self.lyrics.setVerticalScrollBar(scroll_bar)
      self.lyrics_label = QLabel("Lyrics")
      self.lyrics_label.setWordWrap(True)
      self.mainLayout.addWidget(self.lyrics_label, 4,0)
      self.mainLayout.addWidget(self.lyrics, 4,1)

      self.selected_artist = ""
      self.selected_song = ""
      self.music_genius = lyricsgenius.Genius(MUSIC_GENIUS_ACCESS_TOKEN)
      self.music_genius.remove_section_headers = True # Remove section headers (e.g. [Chorus]) from lyrics when searching
      self.music_genius.skip_non_songs = True


    # Search for Artist
  def artist_search(self):
      self.song_list.clear()
      self.artist_list.clear()
      search_string = self.artist_name.text()

      if search_string:
          artist_result = musicbrainzngs.search_artists(
                artist=search_string, limit=5, strict=True)
          
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
          
        # Update Results
        #update_artist(artist_result)
        # Update YouTube Query
        #update_yt()

    # Update table with artist
    #def update_artist(res):
    #trv.delete(*trv.get_children())
    #for artist in res["artist-list"]:
    #    trv.insert('', 'end', values=("", artist["name"], "", ""))

  def song_search(self, artist):
    #song_result = musicbrainzngs.search_recordings(
    #    recording=song_query.get(), artistname=artist_query.get(), 
    #    release=album_query.get(), limit=100)
    self.song_list.clear()
    self.selected_artist = artist.text()
    song_result = musicbrainzngs.search_recordings(
       artistname=self.selected_artist, 
         limit=100, strict=True)
    for song in song_result["recording-list"]:
        item = QListWidgetItem(song["title"])
        self.song_list.addItem(item)


  def lyric_search(self, song_name):
      self.lyrics.clear()
      self.selected_song = song_name.text()
      song = self.music_genius.search_song(self.selected_song, self.selected_artist)

      self.lyrics.insertPlainText(song.lyrics)
      self.lyrics_label.setText("Lyrics of {}".format(self.selected_song))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()

