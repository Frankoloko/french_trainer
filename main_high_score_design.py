import sys
from PySide2 import QtCore, QtGui, QtWidgets
from jsonc_parser.parser import JsoncParser
import random
from tkinter import messagebox
from datetime import datetime
from threading import Timer

class FrenchTrainer():
    def __init__(self):
        '''
            Collect the data to start working with
        '''
        self.json_data = self.UTILITY_read_json('/Users/francois/Myne/Persoonlik/french_trainer/database.jsonc')

        for key in self.json_data['1000_most_common_words']:
            self.json_data['1000_most_common_words'][key]['correct_counter'] = 0

    def RUN(self):
        '''
            The main command to start the class and the QT screen with. Mostly in charge of setting up the QT app.
        '''
        app = QtWidgets.QApplication.instance()

        if not app:
            app = QtWidgets.QApplication(sys.argv)

        window = QtWidgets.QWidget()
        # window.resize(800, 600) # If you want this

        window.setWindowTitle('French Trainer')
        window.setLayout(self.BUILD_main_layout())
        window.show()

        self.UTILITY_reset_game()

        sys.exit(app.exec_()) # IF YOU ARE NOT IN MAYA OR SOME OTHER DCC, USE THIS

    def BUILD_main_layout(self):
        '''
            Build the main layout and return the result
        '''
        self.CBX_supply_words = QtWidgets.QComboBox()
        self.CBX_supply_words.addItems(['Supply French words', 'Supply English words'])

        self.LBL_question = QtWidgets.QLabel()
        self.LBL_answer = QtWidgets.QLabel()
        self.LBL_current_score = QtWidgets.QLabel()
        self.LED_guess = QtWidgets.QLineEdit()

        self.LED_guess.returnPressed.connect(self.CONNECT_enter_pressed)

        self.BTN_start = QtWidgets.QPushButton("Start")
        self.BTN_next = QtWidgets.QPushButton("Next")
        self.BTN_start.clicked.connect(self.CONNECT_button_start)
        self.BTN_next.clicked.connect(self.CONNECT_button_next)

        # Line spacer
        FRM_line = QtWidgets.QFrame()
        FRM_line.setFrameShape(QtWidgets.QFrame.HLine)
        FRM_line.setFrameShadow(QtWidgets.QFrame.Sunken)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.CBX_supply_words)
        layout.addWidget(self.BTN_start)
        layout.addWidget(FRM_line)
        layout.addWidget(self.LBL_question)
        layout.addWidget(self.LED_guess)
        layout.addWidget(self.LBL_answer)
        layout.addWidget(self.BTN_next)
        layout.addWidget(self.LBL_current_score)

        return layout

    def CONNECT_enter_pressed(self):
        '''
            This is triggered when the Enter keyboard button is pressed
        '''
        self.CONNECT_button_next()

    def CONNECT_button_start(self):
        '''
            The Start/Restart button's logic
        '''
        if self.BTN_start.text() == 'Start':
            # START LOGIC
            self.BTN_start.setText('Restart')
        else:
            # RESTART LOGIC
            pass

        # Set the min and max values
        self.highest_added_word = 5
        self.LBL_current_score.setText('Score: ' + str(self.highest_added_word))
        
        # Copy the first X items of the 1000_most_common_words
        self.current_words = {k: self.json_data['1000_most_common_words'][k] for k in list(self.json_data['1000_most_common_words'].keys())[:self.highest_added_word]}

        self.UTILITY_reset_game()
        self.LED_guess.setFocus()

        self.CONNECT_button_next()

        r = Timer(3.0, self.UTILITY_timer)
        r.start()


    def CONNECT_button_next(self):
        '''
            The function that is run when the next button is pressed
        '''
        if 'SCORE' in self.BTN_next.text():
            return

        if 'Next' in self.BTN_next.text():
            # DISPLAY NEXT WORD

            # Get a random word from the list
            self.current_word_key = random.choice(list(self.current_words.keys()))
            self.current_word = self.current_words[self.current_word_key]
            
            # Set a new question label
            supply_words = self.CBX_supply_words.currentText()
            if supply_words == 'Supply French words':
                self.LBL_question.setText(self.current_word['french'])
            else:
                self.LBL_question.setText(self.current_word['english'])

            # Set the button's next text
            self.BTN_next.setText('Reveal')

            # Clear the previous reveal
            self.LBL_answer.clear()
            self.LED_guess.clear()
        else:
            # REVEAL THE ANSWER
            supply_words = self.CBX_supply_words.currentText()
            if supply_words == 'Supply French words':
                correct_answer = self.current_word['english'].lower()
                self.LBL_answer.setText(f"{self.current_word['english']} ({self.current_word['pronunciation']})")
            else:
                correct_answer = self.current_word['french'].lower()
                self.LBL_answer.setText(f"{self.current_word['french']} ({self.current_word['pronunciation']})")

            # Check if the person guessed correctly
            if self.LED_guess.text().lower() == correct_answer:
                button_text = 'Correct...Next'
                self.current_words[self.current_word_key]['correct_counter'] += 1
                if self.current_words[self.current_word_key]['correct_counter'] == 3:
                    self.current_words.pop(self.current_word_key)
                    self.highest_added_word += 1
                    self.current_words.update({str(self.highest_added_word): self.json_data['1000_most_common_words'][str(self.highest_added_word)]})
                    self.LBL_current_score.setText('Score: ' + str(self.highest_added_word))
            else:
                button_text = 'Wrong...Next'
                self.total_errors += 1
                self.current_words[self.current_word_key]['correct_counter'] -= 0
                if self.current_words[self.current_word_key]['correct_counter'] < 0:
                    self.current_words[self.current_word_key]['correct_counter'] = 0

            print('-----------')
            for key, value in self.current_words.items():
                print(value['french'], value['correct_counter'])

            # Set the button's next text
            self.BTN_next.setText(button_text)

    def UTILITY_read_json(self, file):
        '''
            Reads a json file and return the result
        '''
        data = JsoncParser.parse_file(file)
        return data

    def UTILITY_reset_game(self):
        '''
            This "Resets" the game, as in, clears all fields and so on.
        '''
        self.LBL_question.clear()
        self.LBL_answer.clear()
        self.LED_guess.clear()
        self.BTN_next.setText('Next')
        self.total_errors = 0

    def UTILITY_timer(self):
        '''
            This is a timer that will run for 10 minutes
        '''
        ###############################################################
        # Timer finished
        print("Timer is done.")

        # # Get the current date and time
        now = datetime.now()
        date_time = now.strftime("%m/%d/%Y %H:%M:%S")

        new_line = f"\n{date_time} \t Errors: {self.total_errors} \t Highest Word: {self.highest_added_word}"

        # # Write the new values to a text file
        with open("/Users/francois/Myne/Persoonlik/french_trainer/score.txt", "a") as file:
            file.write(new_line)

instannce = FrenchTrainer()
instannce.RUN()