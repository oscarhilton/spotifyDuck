# %%
import requests
import json

class ApiService:
  def __init__(self):
    print("Hello")

  def downloadFile(self, outputPath, url, user, password, files):
    print(files)
    data = {
      'outputPath': outputPath,
      'user': user,
      'pass': password,
      'files': files,
    }
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r
# %%
