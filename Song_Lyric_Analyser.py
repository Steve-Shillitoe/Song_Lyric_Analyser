import sys
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, \
                        QPushButton, QVBoxLayout, QWidget, \
                        QGridLayout, QLabel, QLineEdit, QPushButton, \
                        QAbstractItemView, QListWidget, QListWidgetItem

import musicbrainzngs
import webbrowser

# Subclass QMainWindow to customize your application's main window

class MainWindow(QMainWindow):
  def __init__(self):
      super().__init__()
      # Initialize user agent to DB
      musicbrainzngs.set_useragent(
        "MusicAnalyser", "1.0", contact="s.shillitoe1@ntlworld.com")
      self.setWindowTitle("Music Analyser")
      self.setWindowFlags(Qt.CustomizeWindowHint | 
                                          Qt.WindowCloseButtonHint | 
                                          Qt.WindowMinimizeButtonHint |
                                          Qt.WindowMaximizeButtonHint)
      #self.showFullScreen()
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
      self.song_list.setSelectionMode(QAbstractItemView.SingleSelection)
      #self.song_list.itemClicked.connect(lambda item: self.getLyrics(item))
      self.mainLayout.addWidget(self.song_list, 3,1)


    # Search for Artist
  def artist_search(self):
      self.song_list.clear()
      self.artist_list.clear()
      search_string = self.artist_name.text()
      artist_result = musicbrainzngs.search_artists(
            artist=search_string, limit=5, strict=True)
      for artist in artist_result["artist-list"]:
        item = QListWidgetItem(artist["name"])
        #item.setToolTip("Tick the check box to create a subset of images based on {}".format(imageType))
        #item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        #item.setCheckState(Qt.Unchecked)
        self.artist_list.addItem(item)
             
          
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
    song_result = musicbrainzngs.search_recordings(
       artistname=artist.text(), 
         limit=100, strict=True)
    for song in song_result["recording-list"]:
        item = QListWidgetItem(song["title"])
        self.song_list.addItem(item)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()

