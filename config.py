#%%
import json

def readFile(filename):
  with open(filename, 'r') as outfile:
    return outfile.read()

def updateFile(filename, data):
  with open(filename, 'w') as outfile:
    json.dump(data, outfile)

def readConfig():
  return readFile('config.txt')

def updateConfig(data):
  return updateFile('config.txt', data)

def readDownloaded():
  return readFile('download.txt')

def updateDownloaded(data):
  return updateFile('download.txt', data)

def readNotDownloaded():
  return readFile('not_download.txt')

def updateNotDownloaded(data):
  return updateFile('not_download.txt', data)
# %%
