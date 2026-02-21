# cara-oque
Very simple karaoque manager to download and play mp4 videos

The interface and messages are currently in Brazilian Portuguese. Contributions and translations into other languages are welcome.

## How to install

You need to have the VLC and python 3.10+ installed in your machine, Im using brew on MacOS to install them:

```
brew install vlc
brew install python@3.13
``` 

For Windows, you can use `winget` to install Python 3.13 and VLC:

```powershell
winget install Python.Python.3.13
winget install VideoLAN.VLC
```


Create the python virtual environment executing the following scripts depending on your OS:

MacOS:
```
source setup_venv.sh
```

Windows:
```
.\setup_venv.ps1
```

## Run the app

```
source setup_venv.sh
python oque.py
```

    
## How to use

Copy your karaoque music videos (.mp4) to musicas folder and run the oque.py python script.

## How to manage the download channels

The program is checking specific youtube channels for the videos, add new channels to channels.yaml as needed.