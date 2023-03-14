import logging 
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC    
from selenium.common.exceptions import NoAlertPresentException
from selenium.common.exceptions import TimeoutException
from dotenv import load_dotenv
import dotenv
from pathlib import Path
from shutil import rmtree

from selenium.webdriver.common.keys import Keys
from concurrent.futures import ThreadPoolExecutor
from PyQt5.QtCore import *

import time
from numpy import random
import json
import csv
import os
import glob


class ChomeDriver(QObject):
    done = pyqtSignal()
    
    def __init__(self,parent=None, headless=False):
        super().__init__(parent=parent)
        self.headless=headless
        self.timeout = 10
        self.FIRST = True
        self.LATCHED = None
        self.HEADERS_SAVED = False
        self.running = False
        

    def highlight(self, element, effect_time, color, border):
        """Highlights (blinks) a Selenium Webdriver element"""
        def apply_style(s):
            self.driver.execute_script("arguments[0].setAttribute('style', arguments[1]);",
                                element, s)
        original_style = element.get_attribute('style')
        apply_style("border: {0}px solid {1};".format(border, color))
        time.sleep(effect_time)
        apply_style(original_style)
    
    def stop_interupt(self):
        # self.quit()
        self.running = False
        print("Stopping soon")
    
    def quit(self):
        self.driver.quit()
        self.FIRST = True
        self.LATCHED = None
        self.running = False
 
    def execute(self, form_data, combinations, **kwargs):
        download_path = os.getenv('DOWNLOAD_PATH')
        
        if download_path is None:
            dotenv_file = dotenv.find_dotenv()
            if len(dotenv_file) == 0:
                with open('.env', 'w') as env: pass
                dotenv_file = dotenv.find_dotenv()
                
            os.environ["DOWNLOAD_PATH"] = 'run'
            dotenv.set_key(dotenv_file, "DOWNLOAD_PATH", os.environ["DOWNLOAD_PATH"])
        
        
        download_path = os.path.join(os.getenv('DOWNLOAD_PATH'))
        self.running = True
        print("Download path = ", os.path.abspath(download_path))
                   
        if self.FIRST:
            for path in Path(download_path).glob("**"+os.sep+"*"):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    rmtree(path)
            
            self.navigate_to_strategy(False)
            
        summary_data = [['values', 'file']]
        
            
        if all(v is None for v in combinations[0]):
            self.quit()
            self.done.emit()
            return
        
        
        # making sure tickers are active
        self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "symbolName-FeemEKQq")))
        tickers = self.driver.find_elements_by_class_name('symbolName-FeemEKQq')
        activeTicker = kwargs.get('activeTicker')
        
        idx = 0
        for ti in range(len(tickers)): 
            if not activeTicker:
                # self.click(ticker)
                tickers[ti].click()
                self.delay(4)

            # populating values    
            for j, combination in enumerate(combinations):
                if not self.running:
                    break
                
                i= 0
                index  = 0
                self.click_settings_button()
                self.click_input_tab()
                print(f"Working on combination no. {j}")
                content = self.driver.find_element_by_class_name('content-mTbR5jYu')
                rows = content.find_elements_by_css_selector('.cell-mTbR5jYu')
                ok_button = self.driver.find_elements_by_css_selector('[data-name="submit-button"]')[0]
                # Filling data
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
                self.delay(1)

                # capturing
                self.driver.find_element(By.XPATH, '//button[text()="List of Trades"]').click()
                try:
                    self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ka-table ")))
                except TimeoutException as e:
                    idx += 1
                    print("Cannot read output out of this combination")
                    continue
                
                download_btn = self.driver.find_elements_by_css_selector('.no-content-msfP1I4t')[-1]
                # print(download_btn)
                self.click(download_btn)
                # download_btn.click()
                # Wait for download
                self.delay(2)
                
                
                
                # rename it
                files = glob.glob(os.path.join(os.getenv('DOWNLOAD_PATH') , '*'))
                max_file = max(files, key=os.path.getctime)
                filename = max_file.split(os.sep)[-1].split(".")[0]
                new_path = max_file.replace(filename, f'A{str(idx+1).zfill(5)}')
                os.rename(max_file, new_path)
                idx += 1
                summary_data.append([';'.join(str(c) for c in combination), new_path])
                
                
                download_path = os.getenv('DOWNLOAD_PATH')
        

                dmin = os.getenv('DELAY_MIN')
                dmax = os.getenv('DELAY_MAX')
                
                if dmin is None or dmax is None:
                    dotenv_file = dotenv.find_dotenv()
                    os.environ["DELAY_MIN"] = '2500'
                    os.environ["DELAY_MAX"] = '15000'
                    dotenv.set_key(dotenv_file, "DELAY_MIN", os.environ["DELAY_MIN"])
                    dotenv.set_key(dotenv_file, "DELAY_MAX", os.environ["DELAY_MAX"])
                    dmin = os.getenv('DELAY_MIN')
                    dmax = os.getenv('DELAY_MAX')
                    
                time.sleep(random.uniform(int(dmin), int(dmax))/1000)

            if activeTicker:
                break
            
            # just updating again
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "symbolName-FeemEKQq")))
            tickers = self.driver.find_elements_by_class_name('symbolName-FeemEKQq')


        for i in summary_data:
            self.append_to_csv(i, os.path.join(download_path, os.getenv("CSV_PATH")))
        
        if self.running:
            self.done.emit()
        
        self.quit()
        
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
        options.add_experimental_option("prefs", {
                "download.default_directory": os.path.join(os.getcwd(), 'run'),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
                })

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
            
            return fields

        except Exception as e:
            print(str(e))
            return None
        
    def append_to_csv(self, data_list, filename):
        with open(filename, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data_list)