#%%
from setuptools import setup

APP = ['App.py']
DATA_FILES = [
    'start.js',
    'config.txt',
    'downloaded.txt',
    'not-downloaded.txt',
    'icon.png',
    'temp'
]
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': ['rumps', 'spotipy', 'requests', 'dotenv'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
# %%