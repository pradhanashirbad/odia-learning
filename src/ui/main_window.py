from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QFrame, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

class WordSection(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        
        layout = QGridLayout()
        self.english_label = QLabel("English: ")
        self.odia_label = QLabel("Odia: ")
        self.romanized_label = QLabel("Romanized: ")
        
        layout.addWidget(QLabel("English:"), 0, 0)
        layout.addWidget(QLabel("Odia:"), 1, 0)
        layout.addWidget(QLabel("Romanized:"), 2, 0)
        
        layout.addWidget(self.english_label, 0, 1)
        layout.addWidget(self.odia_label, 1, 1)
        layout.addWidget(self.romanized_label, 2, 1)
        
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self, word_service, translation_service, speech_service):
        super().__init__()
        self.word_service = word_service
        self.translation_service = translation_service
        self.speech_service = speech_service
        
        self.setWindowTitle("Odia Learning App")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create UI components
        self.generate_button = QPushButton("Generate New Words")
        self.word_sections = [WordSection() for _ in range(5)]
        
        # Add components to layout
        layout.addWidget(self.generate_button)
        for section in self.word_sections:
            layout.addWidget(section)
        
        # Add stretch at the end
        layout.addStretch()
        
        # Connect signals
        self.generate_button.clicked.connect(self.generate_words)

    def generate_words(self):
        try:
            # Generate words
            words = self.word_service.generate_words()
            print("Generated words:", words)  # Show generated words
            
            # Clear previous display
            for section in self.word_sections:
                section.english_label.setText("")
                section.odia_label.setText("")
                section.romanized_label.setText("")
            
            # First display English words
            for section, word in zip(self.word_sections, words):
                section.english_label.setText(word)
                # Force UI update
                QApplication.processEvents()
            
            # Get translations
            translations = self.translation_service.translate_words(words)
            print("Got translations")  # Show translation step
            
            # Then update with full translations
            for section, translation in zip(self.word_sections, translations):
                section.odia_label.setText(translation['odia'])
                section.romanized_label.setText(translation['romanized_odia'])
                # Force UI update
                QApplication.processEvents()
            
            print("Starting audio playback...")  # Show audio step
            # Play audio at the end
            for translation in translations:
                self.speech_service.speak_odia(translation['odia'])
                
        except Exception as e:
            print(f"Error: {e}") 