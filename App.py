#!/usr/bin/python
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os, rumps, csv

from glob import glob

import rumps
from difflib import SequenceMatcher

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from subprocess import Popen, PIPE

from ApiService import ApiService

import config, json

configjson = json.loads(config.readConfig())

from dotenv import load_dotenv
load_dotenv()

from datetime import date

import requests

import random

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SERVER_URI = os.getenv("SERVER_URI")

CONDIDENCE_PERCENTAGE = 45

print("STARTING UP")

class Playlist:
    def __init__(self, name, uri, tracks):
        self.name = name
        self.uri = uri
        self.tracks = tracks

class User:
    def __init__(self, username, password, userid, location, endpath):
        self.username = username
        self.password = password
        self.userid = userid
        self.location = location
        self.endpath = endpath

    def format(self):
        data = {
            'username': self.username,
            'password': self.password,
            'userid': self.userid,
            'location': self.location,
            'endpath': self.endpath,
        }
        return data

def bigPrint(string):
    print("=====================")
    print(string)
    print("=====================")
    return

class SpotifyApp(rumps.App):
    def __init__(self):
        super(SpotifyApp, self).__init__(type(self).__name__, icon="icon.png", quit_button=None)
        rumps.debug_mode(True)
        self.menu = ['Start server', 'Make playlists', 'Download missing files', None, 'About', 'Setup', None, 'Clean Quit']
        self.username = configjson["username"]
        self.password = configjson["password"]
        self.userid = configjson["userid"]
        self.location = configjson["location"]
        self.endpath = os.path.expanduser(configjson["endpath"] + '/duck/' + str(date.today()))
        self.downloaded = []
        self.notdownloaded = []
        self.server = None
        self.online = False

    @rumps.timer(5)
    def loop(self, sender):
        print(self)
        print(sender)
        print(self.online)
        print(self.menu)
    
    @rumps.clicked('Start server')
    def startServer(self, sender):
        sender.title = 'Server running' if sender.title == 'Start server' else 'Start server'
        print(sender)
        rumps.notification(title="Starting server", subtitle="Local server is staring up",  message="Attempting to start: " + SERVER_URI, icon="icon.png", data=None, sound=True)
        print("Starting server . . . ")
        try:
            self.server = Popen(["node", "start.js"], stdin=PIPE, stdout=PIPE)
            rumps.notification(title="Server started!", subtitle="You can now download new files",  message="Enjoy!", data=None, sound=True)
        except:
            rumps.notification(title="Server error", subtitle="Error",  message="Sorry!", data=None, sound=True)
        
        self.online = self.server.poll() == 1
        print(self.online)

            

    @rumps.clicked('Setup')
    def runSetup(self, _):
        # if (self.username and self.password and self.userid and self.endpath and self.location):
        #     rumps.notification(title="Current setup", message=[self.username, self.password, self.userid, self.endpath], data=None, sound=True)

        soulseekuser = rumps.Window(message='Please provide your SoulSeek username', title='SoulSeek User', default_text='username', ok=None, cancel=None, dimensions=(320, 20)).run()
        soulseekpass = rumps.Window(message='What is your SoulSeek password?', title='SoulSeek Password', default_text='password', ok=None, cancel=None, dimensions=(320, 20)).run()
        userid = rumps.Window(message='What is your spotify user ID?', title='Set your user ID', default_text='##########', ok=None, cancel=None, dimensions=(320, 20)).run()
        location = rumps.Window(message='Where are your music files located?', title='Locate files', default_text='~/Music', ok=None, cancel=None, dimensions=(320, 20)).run()
        endpath = rumps.Window(message='Where do you want me to put the playlist files?', title='Output path', default_text='~/Desktop', ok=None, cancel=None, dimensions=(320, 20)).run()

        self.cuttentuser = User(soulseekuser.text, soulseekpass.text, userid.text, location.text, endpath.text)
        config.updateConfig(self.cuttentuser.format())

    @rumps.clicked('Download missing files')
    def downloadMissingFiles(self, _):
        notDownloadedFiles = json.loads(config.readNotDownloaded())
        
        api = ApiService()
        random.shuffle(notDownloadedFiles)

        print(notDownloadedFiles)

        def format(track):
            if isinstance(track, list):
                return
            else:
                return track['Track'] + ' - ' + track['Album']

        filesToSend = map(format, notDownloadedFiles)

        try:
            res = api.downloadFile(self.location, SERVER_URI + '/download', self.username, self.password, filesToSend)
            bigPrint('RESULTS FROM SERVER')
            bigPrint(res.status_code)
            responsetext = json.loads(res.text)
            bigPrint(res.text)

            if responsetext["error"]:
                rumps.notification(title="Download aborted.", subtitle=responsetext["error"],  message="Soulseek doesn't like something. Check your firewall for blocked ports.", data=None, sound=True)
            else:
                rumps.notification(title="Success!", subtitle="Didn't encounter any errors",  message="Looking good!", icon="icon.png", data=None, sound=True)

        except requests.exceptions.Timeout:
            # Maybe set up for a retry, or continue in a retry loop
            bigPrint('Timeout from server')
            rumps.notification(title="Server timeout", subtitle="The server timed out",  message="Looks like the server is asleep. Try again.", icon="icon.png", data=None, sound=True)
        except requests.exceptions.TooManyRedirects:
            # Tell the user their URL was bad and try a different one
            bigPrint('Too many redirects')
            rumps.notification(title="Redirection overflow", subtitle="The server encountered too many redirects",  message="Looks like the server got overloaded. Try again.", icon="icon.png", data=None, sound=True)
        except requests.exceptions.RequestException as e:
            # catastrophic error. bail.
            bigPrint('Catastrophic error. Bail.')
            rumps.notification(title="Oh dear", subtitle="No response from server port",  message="There was an error when communicating to the server. Make sure the server is turned on!", icon="icon.png", data=None, sound=True)
            raise SystemExit(e)

    @rumps.clicked("Make playlists")
    def makePlaylists(self, _):
        rumps.notification(title="Analysis started", subtitle="Please be patient!", message="Quack quack", data=None, sound=True)
        try:
            client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            playlists = sp.user_playlists(self.userid)
            pls = []
        except: 
            rumps.notification(title="Oops.", subtitle="Looks like your creds are wrong.", message="Quack quack", data=None, sound=True)
            return

        def similar(a, b):
            return SequenceMatcher(None, a, b).ratio()

        def find(trackname, trackartists, album, path):
            result = []

            extensions = ['*.flac', '*.mp3']

            loose = []
            files = []

            for ext in extensions:
                findthis = path + '/' + ext
                looseglob = glob(findthis)
                loose.extend(looseglob)
                
            for ext in extensions:
                findthis = path = '/**/' + ext
                nestedglob = glob(findthis)
                files.extend(nestedglob)

            for name in loose:
                tracknameratio = similar(name, trackname) * 100
                result.append({ 'track': trackname + ' - ' + trackartists + ' - ' + album, 'path': name, 'total': tracknameratio })

            for name in files:
                split = name.rsplit('/',2)
                tracknameratio = similar(split[2], trackname)
                artistnameratio = similar(split[1], trackartists)
                albumnameratio = similar(split[1], album)

                total = (tracknameratio + artistnameratio + albumnameratio) * 100 / 3

                result.append({ 'track': trackname + ' - ' + trackartists + ' - ' + album, 'path': name, 'total': total })

            sort = sorted(result, key=lambda k: k['total'], reverse=True)

            best = None

            if (len(sort) > 0):
                best = sort[0]

            if (best and best['total'] > CONDIDENCE_PERCENTAGE):
                return { 'path': best['path'], 'ratio': best['total'] }

            return False

        def getAllArtistsFromTrack(artistList):
            s = ', '
            artists = []

            for artist in artistList:
                artists.append(artist['name'])

            return s.join(artists)

        while playlists:
            for i, playlist in enumerate(playlists['items']):
                results = sp.playlist(playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                pls.append(Playlist(playlist['name'], playlist['uri'], tracks['items']))
                while tracks['next']:
                    tracks = sp.next(tracks)
            if playlists['next']:
                playlists = sp.next(playlists)
            else:
                playlists = None


        csvfilepath = self.endpath + '/analysis/'
        exists = os.path.exists(csvfilepath)
        if not exists:
            try:
                os.makedirs(csvfilepath)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise

        with open(csvfilepath + 'playlists.csv', mode='w') as csv_file:
            fieldnames = ['Playlist', 'Track', 'Album', 'Artists', 'Duration', 'Most Likely', 'Confidence']
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

            writer.writeheader()

            for playlist in pls:
                tracksData = []
                for trackObject in playlist.tracks:
                    trackname = trackObject['track']['name']
                    album = trackObject['track']['album']['name']
                    trackartists = getAllArtistsFromTrack(trackObject['track']['artists'])
                    duration = trackObject['track']['duration_ms']
                    res = find(trackname, trackartists, album, '/Volumes/SHARED/music/')
                    data = {
                        'Playlist': playlist.name,
                        'Track': trackname,
                        'Album': album,
                        'Artists': trackartists,
                        'Duration': duration / 100,
                        'Most Likely': res['path'] if res else None,
                        "Confidence": res['ratio'] if res else None,
                    }
                    writer.writerow(data)
                    tracksData.append(data)

                    if res:
                        self.downloaded.append(data)
                    else:
                        self.notdownloaded.append(data)
            
                playlistpath = os.path.expanduser(self.endpath + '/playlists/')
                exists = os.path.exists(playlistpath)
                if not exists:
                    try:
                        os.makedirs(playlistpath)
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                f = open(playlistpath + playlist.name + '.m3u', "w+")
                f.write('#EXTM3U\n')

                if (len(tracksData) == len(pls)):
                    for track in tracksData:
                        path = track["Most Likely"]
                        if (path):
                            f.write("#EXTINF:" + str(track["Duration"]) + "," + track["Artists"] + " - " + track["Track"] + "\n")
                            f.write(path + "\n")
                            f.write("\n")
    
        config.updateDownloaded(self.downloaded)
        config.updateNotDownloaded(self.notdownloaded)

        totalNumberOfFiles = len(self.downloaded) + len(self.notdownloaded)
        percentageDownloaded = 100 * (self.downloaded / totalNumberOfFiles)

        rumps.notification(title="Analysis finished!", subtitle="Enjoy your playlists!", message="You have " + percentageDownloaded + "%" + " of all playlist files downloaded.", data=None, sound=True)

    @rumps.clicked('Clean Quit')
    def clean_up_before_quit(self, _):
        if (self.server):
            bigPrint('Quitting server')
            self.server.terminate()
        bigPrint('Quitting application')
        rumps.quit_application()

if __name__ == "__main__":
    SpotifyApp().run()
