# Trading View Optimizer

## Prequsites
	0. Clone this repository
    1.**Python 3.7+** (download it from here https://www.python.org/downloads/release/python-370/ then install it)
    2.**Chrome browser** installed
    3.**Chrome driver**: dowload the chrome driver corresponding to chrome browser version  from here (https://chromedriver.chromium.org/downloads). To know  chrome browser version, click on the three dots and select help->About Google Chrome (version number we need is the first 3 numbers, i,e,:110.x). Download it and extract it inside the cloned repository
    4.**The path of your Chrome profile**. Note that you need to be logged in automatically in Trading view in the profile, otherwise codewon't work. To get the profile path, write chrome://version/ in the browser address bar and press enter . You will long list of configurations, and "Profile Path" is one of them. the value of "Profile Path" (after removing "\Default" from its end) is what u need. It should look like this C:\Users\<USERNAME>\AppData\Local\Google\Chrome\User Data
    5.**Install tesseract (used for OCR)**. The guide here (https://linuxhint.com/install-tesseract-windows/) explains how to install it properly. Note that we need the exe path, it will be something like C:\Program Files\Tesseract-OCR\tesseract.exe


## Installing:
    open terminal in the folder having the code and run: 
    python -m pip install requirements.txt

## Configuring the code:
    open the .env file near the code and edit the following configs:
        1- STRATEGY: link to the strategy where optimizations will be done

        2- TESSERACT_CMD: path to tesseract.exe (Prequsites step no.5)

        3- CHROME_PROFILE: path to google chrome profile having trading view auto logged-in (Prequsites step np.4)

        4- CSV_PATH: path to which the code will add values from the yellow label
        

## Running the code:
	in cmd terminal in the folder having the cloned code,
    run: python app.py

## Operation:
    1.**Strategy paramters**:
    for the first time for a strategy, the app needs to know the strategy parameters. To do so, click on "Capture" button. It will open the strategy then figures its parameters by looping over them

    for next times using same strategy, you only click "load parameters" and the app will load the saved parameters.

    2.**Parameters values**:
    The app shows the available parameters for strategy. To include some parameter in the optimization process, tick its use check. For numeric values you have to specify maximum value, minimum value and step size for the values

    3.**Optimization**:
    click "execute". The browser window will open and navigates to the strategy, then starts doing optimization process saving the result into CSV.


