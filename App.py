#!/usr/bin/python3

import os, rumps, csv, rumps, spotipy, config, json, requests, random, tinytag, threading
from difflib import SequenceMatcher
from glob import glob
from spotipy.oauth2 import SpotifyClientCredentials
from subprocess import Popen, PIPE
from ApiService import ApiService
from datetime import date
from dotenv import load_dotenv
load_dotenv()
configjson = json.loads(config.readConfig())

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SERVER_URI = os.getenv("SERVER_URI")

CONDIDENCE_PERCENTAGE = 65

print("STARTING UP")
rumps.debug_mode(True)

def bigPrint(string):
    print("=====================")
    print(string)
    print("=====================")
    return

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

class SpotifyApp(rumps.App):
    def __init__(self):
        super(SpotifyApp, self).__init__(type(self).__name__, icon="icon.png", quit_button=None)
        rumps.debug_mode(True)
        self.menu = ['Offline', 'Start server', 'Make playlists', 'Download missing files', None, 'About', 'Setup', None, 'Clean Quit']
        self.username = configjson["username"]
        self.password = configjson["password"]
        self.userid = configjson["userid"]
        self.location = configjson["location"]
        self.endpath = os.path.expanduser(configjson["endpath"] + '/duck/' + str(date.today()))
        self.downloaded = []
        self.notdownloaded = []
        self.pls = []
        self.tracksData = []
        self.server = None
        self.online = False

    def makeTrackingFiles(self):
        try:     
            for playlist in self.pls:
                for trackObject in playlist.tracks:
                    trackname = trackObject['track']['name']
                    album = trackObject['track']['album']['name']
                    trackartists = self.getAllArtistsFromTrack(trackObject['track']['artists'])
                    duration = trackObject['track']['duration_ms']
                    res = self.find(trackname, trackartists, album, '/Volumes/SHARED/music/')
                    data = {
                        'Playlist': playlist.name,
                        'Track': trackname,
                        'Album': album,
                        'Artists': trackartists,
                        'Duration': duration / 100,
                        'Most Likely': res['path'] if res else None,
                        "Confidence": res['ratio'] if res else None,
                    }
                    self.tracksData.append(data)

                    if res:
                        self.downloaded.append(data)
                    else:
                        self.notdownloaded.append(data)

            print(len(self.tracksData))
            print(len(self.downloaded), len(self.notdownloaded))
        
            try:
                print("STARTING UPDATE OF TXT FILES")
                config.updateDownloaded(self.downloaded.encode('utf-8').strip())
                config.updateNotDownloaded(self.notdownloaded.encode('utf-8').strip())
            except Exception as exc:
                print("HERE!", exc)

    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()

    def getAllArtistsFromTrack(self, artistList):
        s = ', '
        artists = []

        for artist in artistList:
            artists.append(artist['name'])

        return s.join(artists)

    def find(self, trackname, trackartists, album, path):
        result = []
        extensions = ['*.flac', '*.mp3']
        files = []

        for ext in extensions:
            findthis = path + '/' + ext
            looseglob = glob(findthis)
            files.extend(looseglob)
            
        for ext in extensions:
            findthis = path + '/**/' + ext
            nestedglob = glob(findthis)
            files.extend(nestedglob)

        for fp in files:
            meta = tinytag.TinyTag.get(fp)
            if (meta):
                similarName = self.similar(str(meta.title), trackname) * 100
                similarAlbum = self.similar(str(meta.album), album) * 100
                similarArtists = self.similar(str(meta.artist), trackartists) * 100
                total = (similarName + similarAlbum + similarArtists) / 3
                result.append({ 'track': trackname + ' - ' + trackartists + ' - ' + album, 'path': fp, 'total': total })

        try:
            sort = sorted(result, key=lambda k: k['total'], reverse=True)
            best = None

            if (len(sort) > 0):
                best = sort[0]

                if (best and best['total'] > CONDIDENCE_PERCENTAGE):
                    [rint(best)]
                    return { 'path': best['path'], 'ratio': best['total'] }

            return False
        except Exception as exc:
            print(exc)

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
        rumps.notification(title="Starting server", subtitle="Local server is staring up",  message="Attempting to start: " + SERVER_URI, icon="icon.png", data=None, sound=True)
        try:
            self.server = Popen(["node", "start.js"], stdin=PIPE, stdout=PIPE)
            rumps.notification(title="Server started!", subtitle="You can now download new files",  message="Enjoy!", data=None, sound=True)
        except:
            rumps.notification(title="Server error", subtitle="Error",  message="Sorry!", data=None, sound=True)

    @rumps.clicked("Run analysis")
    def analysis():
        print("FUN RUN")

    @rumps.clicked("Make playlists")
    def makePlaylists(self, _):
        rumps.notification(title="Analysis started", subtitle="Please be patient!", message="Quack quack", data=None, sound=True)

        try:
            client_credentials_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
            sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
            playlists = sp.user_playlists(self.userid)
        except Exception as exc:
            print(exc)

        try:
            while playlists:
                for i, playlist in enumerate(playlists['items']):
                    results = sp.playlist(playlist['id'], fields="tracks,next")
                    tracks = results['tracks']
                    self.pls.append(Playlist(playlist['name'], playlist['uri'], tracks['items']))
                    while tracks['next']:
                        tracks = sp.next(tracks)
                if playlists['next']:
                    playlists = sp.next(playlists)
                else:
                    playlists = None
        except Exception as exc:
            print(exc)

        

        try:
            print("STARTING UPDATE OF ANALYSIS CSV")
            analysisPath = self.endpath + '/analysis/'
            exists = os.path.exists(analysisPath)
            if not exists:
                try:
                    
                    os.makedirs(analysisPath)
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise

            with open(analysisPath + 'playlists.csv', mode='w') as csv_file:
                fieldnames = ['Playlist', 'Track', 'Album', 'Artists', 'Duration', 'Most Likely', 'Confidence']
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()

                for track in self.tracksData:
                    writer.writerow(track)

                playlistpath = os.path.expanduser(self.endpath + '/playlists/')
                exists = os.path.exists(playlistpath)
                if not exists:
                    try:
                        os.makedirs(playlistpath)
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                for playlist in self.pls:
                    f = open(playlistpath + playlist.name + '.m3u', "w+")
                    f.write('#EXTM3U\n')

                    for track in playlist.tracks:
                        path = track["Most Likely"]
                        if (path):
                            f.write("#EXTINF:" + str(track["Duration"]) + "," + track["Artists"] + " - " + track["Track"] + "\n")
                            f.write(path + "\n")
                            f.write("\n")
        except Exception as exc:
            print(exc)

        bigPrint("FINISHING UP")
        print(len(self.downloaded), len(self.notdownloaded))
        downloadedLength = len(self.downloaded)
        notDownloadedLength = len(self.notdownloaded)
        percentageDownloaded = downloadedLength / (downloadedLength + notDownloadedLength)
        print(percentageDownloaded)
        rumps.notification(title="Analysis finished!", subtitle="Enjoy your playlists!", message="You have " + str(percentageDownloaded) + "%" + " of all playlist files downloaded.", data=None, sound=True)

        except Exception as exc:
            rumps.notification(title="Oops.", subtitle="Looks like your creds are wrong.", message="Quack quack", data=None, sound=True)
            print('Something went wrong', exc)
            return

    @rumps.clicked('Clean Quit')
    def clean_up_before_quit(self, _):
        if (self.server):
            bigPrint('Quitting server')
            self.server.terminate()
        bigPrint('Quitting application')
        rumps.quit_application()

if __name__ == "__main__":
    SpotifyApp().run()
