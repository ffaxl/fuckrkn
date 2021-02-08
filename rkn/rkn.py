from datetime import datetime
from multiprocessing.dummy import Pool as ThreadPool
import pickle
import urllib.request

from tools import dns_resolve, get_af


class RKNDump(object):
  ipbase = set()
  names = set()
  updated = None
  content = ''
  resolve_threads = 0
  _statefname = "rkn.state"

  def __init__(self, url = None, resolve_threads = 10):
    self.resolve_threads = resolve_threads
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

    self.ipbase.clear()
    self.names.clear()
    for l in dump.split('\n'):
      if l == '':
        continue
      (ips, name, tmp) = l.split(';', 2)
      for ipstr in ips.split(' | '):
        if ipstr == '':
          continue
        try:
          af = get_af(ipstr)
        except ValueError:
          self.names.add(ips)
          print("%s isn't an ip address, resolve as domain name" % ips)
        else:
          self.ipbase |= set([ipstr])

      if name == '':
        continue
      self.names.add(name)

    pool = ThreadPool(self.resolve_threads)
    for ips in pool.map(dns_resolve, self.names):
      self.ipbase |= set(ips)
    pool.close()
    pool.join()

  def diff(self, old):
    s1 = set(old)
    s2 = self.ipbase
    return s2 - s1, s1 - s2
