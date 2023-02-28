# Trading View Optimizer

## Perquisites
1.**Python 3.7+**
Download it from here https://www.python.org/downloads/release/python-370/ then install it
2.**Google Chrome browser** 
3.**Chrome driver**:
Download the chrome driver corresponding to chrome browser version from here (https://chromedriver.chromium.org/downloads). 
To know  chrome browser version, click on the three dots and select help->About Google Chrome (version number We need is the first 3 numbers, i,e,:110.x).
Download chrome driver and extract it inside the cloned repository

![enter image description here](https://raw.githubusercontent.com/LightCannon/Opti-Mora/main/images/2.jpg)

4.**The path of your Chrome profile**. 
To get the profile path, write chrome://version/ in the browser address bar and press enter . 
You will long list of configurations, and "Profile Path" is one of them. the value of "Profile Path" (after removing "\Default" from its end) is what u need. 
It should look like this C:\Users\<USERNAME>\AppData\Local\Google\Chrome\User Data
![enter image description here](https://raw.githubusercontent.com/LightCannon/Opti-Mora/main/images/3.jpg)
Note that you need to be logged in automatically in Trading view in this profile, otherwise the app won't work

5.**Install tesseract (used for OCR)**. 
The guide [here](https://linuxhint.com/install-tesseract-windows/) explains how to install it properly. Note that we need the exe path, it will be something like C:\Program Files\Tesseract-OCR\tesseract.exe


## Installing:

open terminal in the folder having the code and run:

    python -m pip install requirements.txt

## Configuring the code:
Open the .env file near the code and edit the following:

 - **TESSERACT_CMD**: path to tesseract.exe (Perquisites step no.5)


## Running the code:
In a cmd terminal in the folder having the cloned code run
```
python app.py
```
## Operation:

 1. Fill the following data in the UI:
	a.	**Strategy Chart URL**:  The share link of the chat (example: https://www.tradingview.com/chart/XYZABC/)
	b.	**Google Chrome profile path**: Path to google chrome profile having trading view auto logged-in (Perquisites step no.4)
	c.	**Output CSV**: name of the output csv file
	![enter image description here](https://raw.githubusercontent.com/LightCannon/Opti-Mora/main/images/1.jpg)
	
 2. **Strategy paramters**:
	For the first time for a strategy, the app needs to know the strategy parameters. 
	To do so, click on "**Capture**" button. It will open the strategy and figures its parameters by looping over them. 
	Next times, you do not need to re-capture (unless the strategy is changed). Just click "**Load parameters**" and the previously captured parameters will be auto loaded

 3. **Parameters values**:
The app shows the available parameters for strategy. 
To include some parameter in the optimization process, tick its **use checkbox**. For numeric values you have to specify maximum value, minimum value and step size for the values
![enter image description here](https://raw.githubusercontent.com/LightCannon/Opti-Mora/main/images/4.jpg)

3. **Optimization**
To start optimization, click "**Execute**. Google chrome will start and will navigate to the chart doing scan over the selected parameters (while keeping the rest on their default value). It waits for a yellow label to change its data then parses its content (using OCR). Finally, it saves the parsed data into a csv and continues till all selected parameters and their combinations are scanned.

