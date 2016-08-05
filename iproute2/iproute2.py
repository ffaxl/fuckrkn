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
      r = subprocess.run(['/sbin/ip', 'route', 'del', ip, 'scope', self.scope], stderr=subprocess.PIPE)
      if r.returncode == 0:
        print("%s: %s removed" % (gettime(), ip))
      else:
        print("%s: remove failed: %s" % (gettime(), r.stderr.decode('utf8')))
    for ip in to_add:
      r = subprocess.run(['/sbin/ip', 'route', 'add', ip] + shlex.split(self.target) + ['scope', self.scope], stderr=subprocess.PIPE)
      if r.returncode == 0:
        print("%s: %s added" % (gettime(), ip))
      else:
        print("%s: add failed: %s" % (gettime(), r.stderr.decode('utf8')))
    subprocess.run(['/sbin/ip', 'route', 'flush', 'cache'])
