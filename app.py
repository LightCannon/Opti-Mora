import json
from dotenv import load_dotenv
import numpy as np
import itertools

from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QMainWindow,
    QDoubleSpinBox,
    QVBoxLayout,
    QWidget, 
    QMessageBox,
    QStatusBar
)
from PyQt5.QtWidgets import QApplication, QCheckBox, QComboBox, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QDoubleSpinBox, QVBoxLayout, QWidget
from chromeengine import *

class Form(QMainWindow):
    def __init__(self, form_data=[]):
        super().__init__()
        self.form_data = form_data
        self.widget = QWidget()
        self.layout_ = QVBoxLayout(self.widget)
        self.footer = QStatusBar()
        self.footer.addPermanentWidget(QLabel("By Camilo Mora and LightCannon"))
        self.engine = ChomeDriver()  
        
        self.base_init()
        
    def load_params(self):  
        with open(r"strategy_params.json", "r") as read_file:
            self.form_data = json.load(read_file)
        self.initUI()
    
    def clear_layout(self, layout):
        while layout.count() > 1:
            item = layout.takeAt(1)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                self.clear_layout(item.layout())
    
    def capture(self):
        ret = self.engine.navigate_to_strategy(True)  
        self.engine.quit()
        
        done = ret is not None
        if done:
            self.load_params()
            self.initUI()
            # Show success message
            QMessageBox.information(QWidget(), "Success", "Form data captured successfully!")
        else:
            # Show error message
            QMessageBox.critical(QWidget(), "Error", "Failed to capture form data.")
    
    def execute(self):
        # Initialize an empty dictionary to hold the form data
        # self.form_data['']
        for i, row in enumerate(self.form_data):
            if row["is_input"]:
                use = self.form_data[i]['useW'].isChecked()
                # value = self.form_data[i]['valW'].text()
                max = float(self.form_data[i]['maxW'].text())
                min = float(self.form_data[i]['minW'].text())
                step = float(self.form_data[i]['stepW'].text())
                
                if use:
                    value = np.arange(min, max+step, step).round(2).tolist()
                else:
                    value = [None]
                      
                self.form_data[i]['data'] = {'use': use,'value': value}
                
            elif row["is_dropbox"]:
                use = self.form_data[i]['useW'].isChecked()
                if use:
                    value = row["value"]
                else:
                    value = [None]
                
                self.form_data[i]['data'] = {'value': value, 'use': use}
            
            elif row["is_checkbox"]:
                use = self.form_data[i]['useW'].isChecked()
                if use:
                    value = [True, False]
                else:
                    value = [None]
                    
                self.form_data[i]['data'] = {'value': value, 'use': use}  


        # generating combinations
        possible_values = [row['data']['value'] for row in self.form_data]
        combinations = list(itertools.product(*possible_values))              

        self.engine.execute(self.form_data, combinations)
        self.engine.quit()
        QMessageBox.information(QWidget(), "Success", "Simulation finished successfully!")
    
    def base_init(self):
        # Load parameters button
        group_box = QGroupBox()
        load_params_btn = QPushButton('Load parameters')
        load_params_btn.clicked.connect(self.load_params)

        # Capture button
        capture_btn = QPushButton('Capture')
        capture_btn.clicked.connect(self.capture)

        # Execute button
        execute_btn = QPushButton('Execute')
        execute_btn.clicked.connect(self.execute)

        group_box_layout = QHBoxLayout()
        group_box_layout.addWidget(load_params_btn)
        group_box_layout.addWidget(capture_btn)
        group_box_layout.addWidget(execute_btn)
        group_box.setLayout(group_box_layout)
        self.layout_.addWidget(group_box)
        
        self.setCentralWidget(self.widget)
        # self.setLayout(self.layout_)
        self.setStatusBar(self.footer)
        self.setWindowTitle("OptiMora")
        
        
    def initUI(self):
        # Clear the current UI
        self.clear_layout(self.layout_)
            
        for i, row in enumerate(self.form_data):
            group_box = QGroupBox()
            group_box_layout = QHBoxLayout()
            check_use = QCheckBox("Use")
            label = row["label"]
            main_widget = None
            
            if row["is_input"]:
                main_widget = QLineEdit()
                min_widget = QDoubleSpinBox()
                min_widget.setMaximum(99999)
                min_widget.setMinimum(0.1)
                # min_widget.setSpecialValueText("-Infinity")
                max_widget = QDoubleSpinBox()
                max_widget.setMaximum(99999)
                
                step_widget = QDoubleSpinBox()
                step_widget.setMaximum(99999)
                step_widget.setMinimum(0.1)

                # max_widget.setSpecialValueText("Infinity")
                input_layout = QHBoxLayout()
                input_layout.addWidget(main_widget)
                input_layout.addWidget(QLabel('Min'))
                input_layout.addWidget(min_widget)
                input_layout.addWidget(QLabel('Max'))
                input_layout.addWidget(max_widget)
                
                input_layout.addWidget(QLabel('Step'))
                input_layout.addWidget(step_widget)
                group_box_layout.addLayout(input_layout)
                
                self.form_data[i]['useW'] = check_use
                self.form_data[i]['valW'] = main_widget
                self.form_data[i]['maxW'] = max_widget
                self.form_data[i]['minW'] = min_widget
                self.form_data[i]['stepW'] = step_widget
                
            elif row["is_dropbox"]:
                main_widget = QComboBox()
                main_widget.addItems(row["value"])
                group_box_layout.addWidget(main_widget)
                
                self.form_data[i]['useW'] = check_use
                self.form_data[i]['dropW'] = main_widget
                
            elif row["is_checkbox"]:
                main_widget = QCheckBox()
                group_box_layout.addWidget(main_widget)
                
                self.form_data[i]['useW'] = check_use
                self.form_data[i]['checkW'] = main_widget
                
            if main_widget:
                main_widget.setVisible(False)
                group_box.setTitle(label)
                group_box_layout.addWidget(check_use)
                
                if row["is_input"]:    
                    min_widget.setEnabled(False)
                    max_widget.setEnabled(False)
                    step_widget.setEnabled(False)
                    check_use.stateChanged.connect(lambda state, w=main_widget, m=min_widget, M=max_widget, Z=step_widget: self.enable_disable_widgets(state, w, m, M, Z))
                    
                group_box_layout.addWidget(main_widget)
                group_box.setLayout(group_box_layout)
                self.layout_.addWidget(group_box)

    def enable_disable_widgets(self, state, widget, min_edit, max_edit, step_edit):
        if state == 2:
            widget.setEnabled(False)
            min_edit.setEnabled(True)
            max_edit.setEnabled(True)
            step_edit.setEnabled(True)
        else:
            widget.setEnabled(True)
            min_edit.setEnabled(False)
            max_edit.setEnabled(False)
            step_edit.setEnabled(False)

if __name__ == "__main__":
    import sys
    load_dotenv()
    app = QApplication(sys.argv)
    ex = Form()
    ex.show()
    sys.exit(app.exec_())