import time
import subprocess
import re

def gettime():
    return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + " %s" % time.tzname[0]

class IPSet(object):

  def __init__(self, ipset):
    self.ipset = ipset
    self.hdr_re = re.compile('Header: family (\w+?) hashsize (\d+) maxelem (\d+)')
    self.read()

  def read(self):
    with subprocess.Popen(['/sbin/ipset', 'list', self.ipset], stdout=subprocess.PIPE) as proc:
      self.addresses = set()
      found = False

      for l in proc.stdout:
        l = l.decode("utf-8").rstrip()
        if found:
          self.addresses.add(l)
        elif l == 'Members:':
          found = True
        else:
          hm = self.hdr_re.match(l)
          if hm:
            (self.family, self.hashsize, self.maxelem) = hm.groups()

  def change(self, to_add, to_rm):
    with subprocess.Popen(['/sbin/ipset', 'restore'], stdin=subprocess.PIPE) as proc:
      for ip in to_rm:
        cmd = 'del %s %s\n' % (self.ipset, ip)
        proc.stdin.write(cmd.encode("utf-8"))
        print("%s: %s removed" % (gettime(), ip))
      for ip in to_add:
        cmd = 'add %s %s\n' % (self.ipset, ip)
        proc.stdin.write(cmd.encode("utf-8"))
        print("%s: %s added" % (gettime(), ip))
