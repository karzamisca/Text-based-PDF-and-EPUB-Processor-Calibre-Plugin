import os #Built-in for Python 3.12.6
from qt.core import QDialog, QLabel, QPushButton, QVBoxLayout, QLineEdit, QFileDialog, QComboBox, QSpinBox, QMessageBox, QCheckBox, QTextEdit #Built-in for Calibre 7.17

class TextBasedPDFandEpubProcessorDialog(QDialog):
    def __init__(self, gui, icon, do_user_config):
        QDialog.__init__(self, gui)
        self.gui = gui
        self.do_user_config = do_user_config

        self.l = QVBoxLayout()
        self.setLayout(self.l)

        self.label = QLabel('Text-based PDF and EPUB Processor Calibre Plugin')
        self.l.addWidget(self.label)

        self.keyword_input = QLineEdit(self)
        self.keyword_input.setPlaceholderText('Enter keyword to search for')
        self.l.addWidget(self.keyword_input)

        # Dropdown for choosing between file and folder
        self.input_type_combo = QComboBox(self)
        self.input_type_combo.addItems(["File", "Folder"])
        self.input_type_combo.currentIndexChanged.connect(self.update_input_button)
        self.l.addWidget(self.input_type_combo)

        self.input_button = QPushButton('Select Input', self)
        self.input_button.clicked.connect(self.select_input_file_or_folder)
        self.l.addWidget(self.input_button)

        self.output_button = QPushButton('Select Output Directory', self)
        self.output_button.clicked.connect(self.select_output_dir)
        self.l.addWidget(self.output_button)

        self.num_sentences_spinner = QSpinBox(self)
        self.num_sentences_spinner.setMinimum(1)
        self.num_sentences_spinner.setValue(5)
        self.l.addWidget(QLabel('Number of Sentences to Extract'))
        self.l.addWidget(self.num_sentences_spinner)

        self.direction_combo = QComboBox(self)
        self.direction_combo.addItems(["Forward", "Backward"])
        self.l.addWidget(QLabel('Direction of Extraction'))
        self.l.addWidget(self.direction_combo)

        self.extract_text_check = QCheckBox('Extract Text', self)
        self.extract_text_check.setChecked(True)
        self.l.addWidget(self.extract_text_check)

        self.extract_images_check = QCheckBox('Extract Images', self)
        self.l.addWidget(self.extract_images_check)

        self.extract_button = QPushButton('Extract', self)
        self.extract_button.clicked.connect(self.extract_text)
        self.l.addWidget(self.extract_button)

        self.search_button = QPushButton('Search and Display', self)
        self.search_button.clicked.connect(self.search_and_display_text)
        self.l.addWidget(self.search_button)

        self.result_display = QTextEdit(self)
        self.result_display.setReadOnly(True)
        self.l.addWidget(self.result_display)

        self.conf_button = QPushButton('Configure this plugin (not implemented yet)', self)
        self.conf_button.clicked.connect(self.config)
        self.l.addWidget(self.conf_button)

        self.input_paths = []
        self.output_dir = ''

        self.resize(self.sizeHint())

    def update_input_button(self):
        # Update the button text based on the dropdown selection
        selected_option = self.input_type_combo.currentText()
        self.input_button.setText(f'Select {selected_option}')

    def select_input_file_or_folder(self):
        # Determine whether to open a file dialog or a folder dialog based on dropdown selection
        selected_option = self.input_type_combo.currentText()
        if selected_option == "File":
            option = QFileDialog.getOpenFileName(self, 'Select Input File', '', 'PDF Files (*.pdf);;EPUB Files (*.epub)')[0]
            if option:
                self.input_paths = [option]
                self.input_button.setText(f'Selected: {os.path.basename(option)}')
        elif selected_option == "Folder":
            folder = QFileDialog.getExistingDirectory(self, 'Select Input Folder')
            if folder:
                self.input_paths = [os.path.join(folder, file) for file in os.listdir(folder) if file.endswith(('.pdf', '.epub'))]
                self.input_button.setText(f'Selected: {len(self.input_paths)} files from folder')

    def select_output_dir(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if self.output_dir:
            self.output_button.setText(f'Selected: {self.output_dir}')

    def extract_text(self):
        keyword = self.keyword_input.text()
        num_sentences = self.num_sentences_spinner.value()
        direction = self.direction_combo.currentText()
        extract_text = self.extract_text_check.isChecked()
        extract_images = self.extract_images_check.isChecked()

        if extract_text and not keyword:
            QMessageBox.warning(self, 'No Keyword', 'Please enter a keyword to search for.')
            return

        if not self.input_paths:
            QMessageBox.warning(self, 'No File(s) Selected', 'Please select an input file or folder.')
        elif not self.output_dir:
            QMessageBox.warning(self, 'No Output Directory', 'Please select an output directory.')
        elif not (extract_text or extract_images):
            QMessageBox.warning(self, 'No Extraction Option Selected', 'Please select at least one extraction option (Text or Images).')
        else:
            pdf_text_extractor = self.gui.iactions['Text-based PDF and EPUB Processor Calibre Plugin']
            for input_path in self.input_paths:
                pdf_text_extractor.extract_text(input_path, self.output_dir, keyword, num_sentences, direction, extract_text, extract_images)

            QMessageBox.information(self, 'Extraction Complete', 'The text and/or images have been successfully extracted.')

    def search_and_display_text(self):
        keyword = self.keyword_input.text()
        num_sentences = self.num_sentences_spinner.value()
        direction = self.direction_combo.currentText()

        if not self.input_paths:
            QMessageBox.warning(self, 'No File(s) Selected', 'Please select an input file or folder.')
        elif not keyword:
            QMessageBox.warning(self, 'No Keyword', 'Please enter a keyword to search for.')
        else:
            pdf_text_extractor = self.gui.iactions['Text-based PDF and EPUB Processor Calibre Plugin']
            results = []
            for input_path in self.input_paths:
                result = pdf_text_extractor.search_text(input_path, keyword, num_sentences, direction)
                results.append(f"RESULT FOR {os.path.basename(input_path)}:\n{result}\n")

            self.result_display.setPlainText("\n\n".join(results))

    def config(self):
        self.do_user_config(parent=self)
