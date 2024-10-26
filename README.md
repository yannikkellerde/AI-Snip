# Bring clippy back to windows (As an AI snip tool)
https://github.com/user-attachments/assets/b3ebcbc1-7010-4f44-bdaa-0c7998e655f6

## Installation
### Windows installation
The most easy way to run AI-Snip is by downloading the binary from the releases page and running it.

If you are python-savy, you may instead:
1. Clone this repo
2. `pip install pyqt6 pyperclip keyboard`
3. `python aisnip.py` from the root of this repo

### Linux installation
There is no uniform system tray in Linux. So in Linux you will only be able to do one snip each time you run this program.

There are no binaries provided for Linux.

* Tested with python 3.11, but other versions should work.
* For pyqt6 you will need libxcb-cursor0. So on Ubuntu, run `sudo apt install libxcb-cursor0`.
* `pip install pyqt6 pyperclip`.
* `python aisnip.py` when you are ready to go snipping.

### Adding your API key
You will need an *OpenAI* or *AzureOpenAI* API key to run AI-Snip

There are two methods to add you api key.
1. The simplest way to add your keys is to start the program and enter your OpenAI API key in the popup window. This will create an openai_api_key.txt file in your folder to remember the key for the next startup.
2. A somewhat more clean way is to add your key to the environment variables. If *OPENAI_API_KEY* or *AZURE_OPENAI_API_KEY* is set, then aisnip will use them automatically.

## Usage
When you start AI-Snip, it will minize itself to the system tray.

To start snipping, you can  
a) right-click on clippy in your system tray and then click `AI Snip`  
b) Press `CTRL+SHIFT+A`

During snipping, you are by default in explaination mode. When you snip a region, clippy will pop up after a few seconds and explain whatever you snipped.

There are various hotkeys available while snipping:
* **D**: Toggles clippy (always starts on)
* **C**: Toggles if AI response is copied to clipboard (always starts off)
* **E**: Go into translation into english mode. Will also set clipboard on.
* **L**: Go into Latex mode. Toggles clippy off and clipboard on.
* **T**: Free prompt mode. Write your own prompt for the AI to answer.
* **Q** or **Esc**: Cancel your ongoing snip or close clippy (you may have to re-select the clippy window if you de-selected it).

## Adding to startup
If you want to use AI-Snip as an everyday tool, you may want to always have it in your system tray.

The easiest way to accomplish this is to donwload the binary, create a Shortcut for it, then go `win + r` and type `shell:startup` and press Enter. Then move your shortcut in the folder that opened.