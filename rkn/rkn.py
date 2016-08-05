from datetime import datetime
import pickle
import urllib.request
import ipaddress
import dns.resolver

class RKNDump(object):
  ipbase = set()
  names = set()
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

    self.ipbase.clear()
    self.names.clear()
    for l in dump.split('\n'):
      if l == '':
        continue
      (ips, name, tmp) = l.split(';', 2)
      try:
        ip = ipaddress.IPv4Address(ips.split(' | ', 1)[0])
      except ipaddress.AddressValueError:
        self.names.add(ips)
#        print("%s isn't an ip address, resolve as domain name" % ips)
      else:
        self.ipbase |= set(ips.split(' | '))
      if name == '':
        continue
      self.names.add(name)
    for name in self.names:
      try:
        resolved = dns.resolver.query(name, "a")
      except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.resolver.NXDOMAIN):
#        print("Unresolved: %s" % name)
        pass
      else:
        ips = [ip.to_text() for ip in resolved]
#        print("Resolved %s to %s" % (name, ','.join(ips)))
        self.ipbase |= set(ips)

  def diff(self, old):
    s1 = set(old)
    s2 = self.ipbase
    return s2 - s1, s1 - s2
