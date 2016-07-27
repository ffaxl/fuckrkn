from datetime import datetime
import pickle
import urllib.request

class RKNDump(object):
  ipbase = set()
  updated = None
  content = ''
  _statefname = "rkn.state"

  def __init__(self, url = None):
    if url:
      response = urllib.request.urlopen(url)
      content = response.read().decode('cp1251')
      self.parse(content)

  def stateLoad(self):
    try:
      with open(self._statefname, "rb") as state:
        content = pickle.load(state)
        self.parse(content)
    except IOError:
      return False
    return True

  def stateSave(self):
    with open(self._statefname, "wb") as state:
      pickle.dump(self.content, state)

  def parse(self, content):
    self.content = content
    updated, dump = self.content.split('\n', 1)
    updated = updated.split(' ', 1)[1]
    self.updated = datetime.strptime(updated, "%Y-%m-%d %H:%M:%S %z")

    content = []
    for l in dump.split('\n'):
      if l == '':
        continue
      content.extend(l.split(';')[0].split(' | '))
    self.ipbase = set(content)

  def diff(self, old):
    s1 = set(old)
    s2 = self.ipbase
    return s2 - s1, s1 - s2
