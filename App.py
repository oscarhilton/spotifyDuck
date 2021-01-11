#%%
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import os, glob, rumps, csv

import rumps
from difflib import SequenceMatcher

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyApp(rumps.App):
    def __init__(self):
        super(SpotifyApp, self).__init__(type(self).__name__, icon="icon.png")
        rumps.debug_mode(True)
        self.menu = ['Make playlists', None, 'About', 'Setup', None]

    @rumps.clicked('Setup')
    def runSetup(self, _):
        userid = rumps.Window(message='What is your spotify user ID?', title='Set your user ID', default_text='##########', ok=None, cancel=None, dimensions=(320, 20)).run()
        location = rumps.Window(message='Where are your music files located?', title='Locate files', default_text='~/Music', ok=None, cancel=None, dimensions=(320, 20)).run()
        endparth = rumps.Window(message='Where do you want me to put the playlist files?', title='Output path', default_text='~/Desktop', ok=None, cancel=None, dimensions=(320, 20)).run()

        print(userid, location, endparth)

    @rumps.clicked("Make playlists")
    def makePlaylists(self, _):
        client_credentials_manager = SpotifyClientCredentials(client_id="cf537c9f470b481d8a63374a0d3a5e3c", client_secret="78e4743a067145aa8d1d37f621e1b98a")
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        playlists = sp.user_playlists('1111207361')
        pls = []
        rumps.notification(title="Analysis started", subtitle="Please be patient!", message="Quack quack", data=None, sound=True)

        def similar(a, b):
            return SequenceMatcher(None, a, b).ratio()

        def find(trackname, trackartists, album, path):
            result = []
            loose = glob.glob(path + '/*.mp3')
            files = glob.glob(path + '/**/*.mp3')

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

            best = sorted(result, key=lambda k: k['total'], reverse=True)[0]
            if (best['total'] > 45):
                return { 'path': best['path'], 'ratio': best['total'] }

            return False

        def getAllArtistsFromTrack(artistList):
            s = ', '
            artists = []

            for artist in artistList:
                artists.append(artist['name'])

            return s.join(artists)

        class Playlist:
            def __init__(self, name, uri, tracks):
                self.name = name
                self.uri = uri
                self.tracks = tracks

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


        with open(os.path.expanduser('~/Desktop/playlists.csv'), mode='w') as csv_file:
            print(csv_file)
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
            
                f = open(os.path.expanduser('~/Desktop/' + playlist.name + '.m3u'),"w+")
                f.write('#EXTM3U\n')

                if (len(tracksData) == len(pls)):
                    for track in tracksData:
                        path = track["Most Likely"]
                        if (path):
                            f.write("#EXTINF:" + str(track["Duration"]) + "," + track["Artists"] + " - " + track["Track"] + "\n")
                            f.write(path + "\n")
                            f.write("\n")
    
        rumps.notification(title="Analysis finished!", subtitle="Enjoy your files!", message="Consider buying me a beer?", data=None, sound=True)

if __name__ == "__main__":
    SpotifyApp().run()
# %%
