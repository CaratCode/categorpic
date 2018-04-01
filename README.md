# Categorpic

Too lazy to organize your pictures? Let Categorpic sort them out for you! Categorpic will sort through your folder of pictures from who knows when and categorize them into related groups so you don't have to.

This was built at LA Hacks 2018.

# How to use

Categorpic is a native application/command line utility, currently you can open it via the terminal.

You will need to set up authentication since this app uses the google cloud vision api. Simply set the environment variable GOOGLE_APPLICATION_CREDENTIALS to the path to the JSON file with your service account key. Click [here](https://console.cloud.google.com/apis/credentials/serviceaccountkey?_ga=2.37699107.-2090575020.1522524367) to create one if you don't already have one.

Then, run the program in the terminal and the GUI will pop up (you will need python installed), as shown.

`$ python categorpic.py`

