import time
import subprocess
import shlex

def gettime():
    return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + " %s" % time.tzname[0]

class IPRoute2(object):

  def __init__(self, scope, target):
    self.scope = scope
    self.target = target
    self.read()


  def read(self):
    self.addresses = set()
    with subprocess.Popen(['/sbin/ip', 'route', 'list', 'scope', self.scope], stdout=subprocess.PIPE) as proc:
      for l in proc.stdout:
        self.addresses.add(l.decode("utf-8").split(' ', 1)[0])


  def change(self, to_add, to_rm):
    for ip in to_rm:
      subprocess.run(['/sbin/ip', 'route', 'del', ip, 'scope', self.scope])
      print("%s: %s removed" % (gettime(), ip))
    for ip in to_add:
      subprocess.run(['/sbin/ip', 'route', 'add', ip] + shlex.split(self.target) + ['scope', self.scope])
      print("%s: %s added" % (gettime(), ip))
    subprocess.run(['/sbin/ip', 'route', 'flush', 'cache'])
