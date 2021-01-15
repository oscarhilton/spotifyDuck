#%%
from setuptools import setup

APP = ['App.py']
DATA_FILES = [
    'start.js',
    'config.txt',
    'downloaded.txt',
    'not_download.txt',
    'icon.png'
]
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'LSUIElement': True,
    },
    'packages': [
        'rumps',
        'spotipy',
        'requests',
        'dotenv',
        'csv',
        'json',
        'random'
    ],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    dependency_links=['https://github.com/supermihi/pytaglib.git']
)
# %%