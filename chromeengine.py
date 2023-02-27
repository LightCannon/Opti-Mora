import logging 
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC    
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv

from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor

import time
from numpy import random
import json
import csv
import cv2
import os
import numpy as np
import base64
import pytesseract

pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD')


class ChomeDriver:
    def __init__(self,headless=False):
        self.headless=headless
        self.timeout = 10
        self.FIRST = True
        self.LATCHED = None
        self.HEADERS_SAVED = False
        
    def highlight(self, element, effect_time, color, border):
        """Highlights (blinks) a Selenium Webdriver element"""
        def apply_style(s):
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                element, s)
        original_style = element.get_attribute('style')
        apply_style("border: {0}px solid {1};".format(border, color))
        time.sleep(effect_time)
        apply_style(original_style)
    
    def quit(self):
        self.driver.quit()
        self.FIRST = True
        self.LATCHED = None
 
    def execute(self, form_data, combinations):
        if self.FIRST:
            self.navigate_to_strategy(False)
            while self.LATCHED is None:
                self.capture_label()
                time.sleep(1)
            
        # populating values      
        for j, combination in enumerate(combinations):
            i= 0
            index  = 0
            self.click_settings_button()
            self.click_input_tab()
            print(f"Working on combination no. {j}")
            content = self.driver.find_element_by_class_name('content-mTbR5jYu')
            rows = content.find_elements_by_css_selector('.cell-mTbR5jYu')
            ok_button = self.driver.find_elements_by_css_selector('[data-name="submit-button"]')[0]
            names = '--'
            while i < len(rows):
                is_checkbox = 'fill' in rows[i].get_attribute('class')
                if combination[index] is not None:
                    if form_data[index]['is_input']:
                        input_element = rows[i+1].find_elements_by_css_selector('.container-Mtq7m9Yl')[0]
                        input = input_element.find_elements_by_css_selector('.input-oiYdY6I4')[0]
                        # self.driver.execute_script("arguments[0].value = '';", input)
                        self.fill_element(input, str(combination[index]))
                        # self.driver.execute_script("arguments[0].value = arguments[1];", input, str(combination[index]))
                        
                    elif form_data[index]['is_dropbox']:
                        input_element = rows[i+1].find_elements_by_css_selector('.container-Mtq7m9Yl')[0]
                        self.click(input_element)
                        options = self.driver.find_element_by_class_name('menuBox-biWYdsXC').find_elements_by_css_selector('[role="option"]')
                        target_option = [o for o in options if o.text == combination[index]][0]
                        self.click(target_option)

                    elif form_data[index]['is_checkbox']:
                        input_element = rows[i].find_elements_by_css_selector('[type="checkbox"]')[0]
                        state = input_element.is_selected()
                        if state ^ combination[index]:
                            self.click(input_element)
                    
                index += 1
                i = i+1 if is_checkbox else i+2
        
            self.click(ok_button)
        
            # capturing
            data = None
            timeout_c = 0
            while data is None:
                data = self.capture_label()
                time.sleep(1)
                timeout_c += 1
                if timeout_c > 10:
                    break
                
            if timeout_c > 10:   
                print(f"Timeout for this combination, moving to the next")
                continue
            
            # write to csv
            print(f"Captured label data = {data}")
            data.insert(0, names)
            self.append_to_csv(data, os.getenv('CSV_PATH'))
            time.sleep(random.uniform(200, 1500)/1000)
          
    def prepare_driver(self):
        print('Opening Chrome')
        options = webdriver.ChromeOptions()
        options.headless = self.headless
        options.add_argument("user-data-dir="+os.getenv('CHROME_PROFILE'))
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--start-maximized")

        # start chrome
        self.driver = webdriver.Chrome(executable_path='chromedriver.exe', options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, 60)
        return self.driver
    
    def delay(self,delay):
        time.sleep(delay)
    
    def fill_element(self,element,data):
        for i in range(4):
            element.send_keys(Keys.BACKSPACE)
            
        for char in data:
            element.send_keys(char)
            self.delay(0.1)

    def click(self, element):
        self.driver.execute_script("arguments[0].click();",element)

    def click_settings_button(self):
        """click settings button."""
        print('Click settings')
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "light-button-msfP1I4t"))
            )

            settings_button = self.driver.find_element(
                By.CLASS_NAME, "light-button-msfP1I4t"
            )
            self.click(settings_button)
            return True
        except Exception as e:
            print ("Cannot find settings")
            return False

    def click_input_tab(self):
        """click the input tab."""
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "tab-Rf5MOAG5"))
            )
            
            input_tab = self.driver.find_element(By.CLASS_NAME, "tab-Rf5MOAG5")
            if input_tab.get_attribute("data-value") == "inputs":
                # input_tab.click()
                self.click(input_tab)
                return True
            return False
        except IndexError:
            print("Could not input tab button. Please check web_element's in commands.py file.")
            return False
        
    def navigate_to_strategy(self, capture=True):
        if not self.FIRST:
            return None
        try:
            self.prepare_driver()
            print('Navigating to strategy link')
            self.driver.get(os.getenv('STRATEGY')) 
            
            time.sleep(2)
            if not capture:
                return
            
            # extract strategy parameters
            self.click_settings_button()
            self.click_input_tab()
            time.sleep(2)
            print('Capturing parameters')
            content = self.driver.find_element_by_class_name('content-mTbR5jYu')
            rows = content.find_elements_by_css_selector('.cell-mTbR5jYu')
            fields = []
            
            i = 0
            while i < len(rows):
                label = rows[i].text
                
                is_checkbox = 'fill' in rows[i].get_attribute('class')
                options = []
                
                if not is_checkbox:    
                    input_element = rows[i+1].find_elements_by_css_selector('.container-Mtq7m9Yl')[0]
                    is_input = len(input_element.find_elements_by_css_selector('.input-oiYdY6I4')) > 0
                    is_dropbox = len(input_element.find_elements_by_class_name('button-allnSfnt')) > 0
                    # is_checkbox = len(input_element.find_elements_by_class_name('checkbox-dV7I8XN5')) > 0
                    
                    # input_element = input_element.find_elements_by_css_selector('.container-Mtq7m9Yl')[0].find_element_by_class_name('inner-slot-yJbunXPO').find_elements_by_css_selector('*')[0]
                    if is_dropbox:
                        element = input_element.find_elements_by_class_name('button-allnSfnt')[0]
                        self.click(element)
                        options = [o.text for o in self.driver.find_element_by_class_name('menuBox-biWYdsXC').find_elements_by_css_selector('[role="option"]')]
                        self.click(element)
                else:
                    is_input = False
                    is_dropbox = False
                
                field = {'label': label, 
                            'is_input':is_input, 
                            'is_dropbox':is_dropbox, 
                            'is_checkbox':is_checkbox, 
                            'value':options}
                fields.append(field)
                print(field)
                i = i+1 if is_checkbox else i+2


            self.click(self.driver.find_element_by_class_name('close-HS2PTQRJ'))
            
            print('Saving Captured parameters')
            with open('strategy_params.json', 'w') as fout:
                json.dump(fields , fout)
            
            print('Capturing default label')
            self.capture_label()
            return fields

        except Exception as e:
            print(str(e))
            return None
        
    def capture_label(self):
        try:  
            canvas = self.wait.until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, '[class="chart-gui-wrapper"]')))
            
            canvas = [c for c in canvas.find_elements_by_css_selector("*") if c.tag_name == 'canvas']
            if len(canvas) == 0:
                return None
            canvas = canvas[0]
                
            img = self.driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
            # decode
            canvas_png = base64.b64decode(img)
            image = cv2.imdecode(np.frombuffer(canvas_png, dtype=np.uint8), cv2.IMREAD_COLOR)
            image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            # extract
            lower_yellow = np.array([20, 100, 100])
            upper_yellow = np.array([30, 255, 255])
            
            mask = cv2.inRange(image_hsv, lower_yellow, upper_yellow)
            yellow_elements = cv2.bitwise_and(image, image, mask=mask)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) == 0:
                return None
            
            biggest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(biggest_contour)
            
            # Crop the image to the biggest contour
            cropped_img = yellow_elements[y:y+h, x:x+w]
            
            # Get the text using OCR
            cropped_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(cropped_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            if self.FIRST:
                self.FIRST = False
                self.LATCHED = thresh
                return None
            else:
                # compare
                diff = np.abs(self.LATCHED - cv2.resize(thresh, self.LATCHED.shape[::-1])) 
                # print(diff.std())
                if diff.std() < 5:
                    return None
            
            print("Captured label change.. executing OCR")
            basewidth = 300
            wpercent = (basewidth/float(thresh.shape[1]))
            hsize = int((float(thresh.shape[0])*float(wpercent)))
            thresh_resized = cv2.resize(thresh, (basewidth, hsize))
            
            text = pytesseract.image_to_string(thresh_resized, lang='eng', config='--psm 3 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz=-.')
            text = text.splitlines()
            values = []
            names = []
            for line in text:
                if '=' not in line:
                    continue
                name, number = line.split('=')[0], line.split('=')[-1]
                test = number.lstrip("-").replace('.', '')
                if not test.isdigit() and not test.isdecimal():
                    continue
                values.append(float(number))
                names.append(name)   
            
            if len(values) == 0:
                print("Cannot execut OCR")
                return None
            
            self.LATCHED = thresh
            if not self.HEADERS_SAVED:
                names.insert(0, 'Parameters')
                self.append_to_csv(names, os.getenv('CSV_PATH'))
                self.HEADERS_SAVED = True
            return values
        except Exception as e:
            print(str(e))
            return None

    def append_to_csv(self, data_list, filename):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data_list)