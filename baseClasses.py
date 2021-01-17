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