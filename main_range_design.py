import sys
from PySide2 import QtCore, QtGui, QtWidgets
from jsonc_parser.parser import JsoncParser
import random

class FrenchTrainer():
    def __init__(self):
        '''
            Collect the data to start working with
        '''
        self.json_data = self.UTILITY_read_json('/Users/francois/Myne/Persoonlik/french_trainer/database.jsonc')

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

        # Test range
        LBL_test_range = QtWidgets.QLabel("Test range")
        self.SBX_from = QtWidgets.QSpinBox()
        self.SBX_to = QtWidgets.QSpinBox()
        self.SBX_from.setValue(1)
        self.SBX_to.setValue(10)

        self.LBL_question = QtWidgets.QLabel()
        self.LBL_answer = QtWidgets.QLabel()
        self.LED_guess = QtWidgets.QLineEdit()

        self.LED_guess.returnPressed.connect(self.CONNECT_enter_pressed)

        self.BTN_start = QtWidgets.QPushButton("Start")
        self.BTN_next = QtWidgets.QPushButton("Next")
        self.BTN_start.clicked.connect(self.CONNECT_button_start)
        self.BTN_next.clicked.connect(self.CONNECT_button_next)

        self.LBL_correct = QtWidgets.QLabel()
        self.LBL_wrong = QtWidgets.QLabel()

        # Line spacer
        FRM_line = QtWidgets.QFrame()
        FRM_line.setFrameShape(QtWidgets.QFrame.HLine)
        FRM_line.setFrameShadow(QtWidgets.QFrame.Sunken)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.CBX_supply_words)
        layout.addWidget(LBL_test_range)
        layout.addWidget(self.SBX_from)
        layout.addWidget(self.SBX_to)
        layout.addWidget(self.BTN_start)
        layout.addWidget(FRM_line)
        layout.addWidget(self.LBL_question)
        layout.addWidget(self.LED_guess)
        layout.addWidget(self.LBL_answer)
        layout.addWidget(self.BTN_next)
        layout.addWidget(self.LBL_correct)
        layout.addWidget(self.LBL_wrong)

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
        min = int(self.SBX_from.value())
        max = int(self.SBX_to.value()) + 1
        self.indexes_remaining = list(range(min, max))

        self.UTILITY_reset_game()
        self.LED_guess.setFocus()

        self.CONNECT_button_next()

    def CONNECT_button_next(self):
        '''
            The function that is run when the next button is pressed
        '''
        if 'SCORE' in self.BTN_next.text():
            return

        if 'Next' in self.BTN_next.text():
            # DISPLAY NEXT WORD

            # If we are done with all the guesses, post the result
            if not self.indexes_remaining:
                correct = int(self.LBL_correct.text().replace('Correct: ', ''))
                wrong = int(self.LBL_wrong.text().replace('Wrong: ', ''))
                total = correct + wrong
                score = round(correct/total*100, 2)
                self.BTN_next.setText(f'SCORE: {score}%')
                self.LBL_question.clear()
                self.LBL_answer.clear()
                self.LED_guess.clear()
                self.BTN_start.setFocus()
                return
            
            # Remove the next item from the list
            next_words_index = self.indexes_remaining.pop(random.randrange(len(self.indexes_remaining)))

            # Get a random number in the range
            self.current_word = self.json_data['1000_most_common_words'][str(next_words_index)]
            
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
                current_value = int(self.LBL_correct.text().replace('Correct: ', ''))
                self.LBL_correct.setText('Correct: ' + str(current_value + 1))
            else:
                button_text = 'Wrong...Next'
                current_value = int(self.LBL_wrong.text().replace('Wrong: ', ''))
                self.LBL_wrong.setText('Wrong: ' + str(current_value + 1))

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
        self.LBL_correct.setText('Correct: 0')
        self.LBL_wrong.setText('Wrong: 0')

instannce = FrenchTrainer()
instannce.RUN()