
SONG_LYRIC_ANALYSER_STYLE = """
                QPushButton {
                             background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #CCCCBB, stop: 1 #FFFFFF);
                             border-width: 3px;
                             margin: 1px;
                             border-style: solid;
                             border-color: rgb(10, 10, 10);
                             border-radius: 5px;
                             text-align: centre;
                             color: black;
                             font-weight: bold;
                             font-size: 9pt;
                             padding: 3px;} 

                QPushButton:disabled {
                        background-color:#FFFFFF;
                        color: lightblue;
                        }

                QPushButton:hover {
                                   background-color: rgb(175, 175, 175);
                                   border: 1px solid red;
                                   }
                                   
                QPushButton:pressed {background-color: rgb(112, 112, 112);}


                QLabel{ padding: 4px;
                        min-height: 1em;
                        text-align: centre;
                        font-weight: bold;
                        font-size: 9pt;
                        background: transparent;
                        margin: 0.25em;
                        }

                
    QPlainTextEdit{
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                                stop: 0 #CCCCBB, stop: 1 #FFFFFF);
        }
    QPlainTextEdit:hover { background-color: rgb(175, 175, 175);
                                   border: 1px solid red;
                                   }
    QLineEdit{
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                                stop: 0 #CCCCBB, stop: 1 #FFFFFF);
        }
    QLineEdit:hover { background-color: rgb(175, 175, 175);
                                   border: 1px solid red;
                                   }


    QListWidget {
        background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, 
                                                stop: 0 #CCCCBB, stop: 1 #FFFFFF);
        }

    QListWidget {
    alternate-background-color: yellow;
    }

    QListWidget {
        show-decoration-selected: 1; /* make the selection span the entire width of the view */
    }

    QListWidget::item:alternate {
        background: #EEEEEE;
    }


    QListWidget::item:selected:hover {
                        background: darkblue;
                        color: white;
                        }

    QListWidget::item:hover {
                        background: #cce5ff;
    }
    
                
    QListWidget:hover {
        background-color: rgb(175, 175, 175);
        border-color: rgb(200, 51, 255);}
                """
