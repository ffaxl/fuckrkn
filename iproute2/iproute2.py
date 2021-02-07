import subprocess
import shlex

from tools import get_af


class IPRoute2(object):

  def __init__(self, proto, target4, target6):
    self.proto = proto
    self.target4 = target4
    self.target6 = target6
    self.read()


  def read(self):
    self.addresses = set()
    with subprocess.Popen(['/sbin/ip', 'route', 'list', 'proto', self.proto], stdout=subprocess.PIPE) as proc:
      for l in proc.stdout:
        self.addresses.add(l.decode("utf-8").split(' ', 1)[0])

    with subprocess.Popen(['/sbin/ip', '-6', 'route', 'list', 'proto', self.proto], stdout=subprocess.PIPE) as proc:
      for l in proc.stdout:
        self.addresses.add(l.decode("utf-8").split(' ', 1)[0])


  def route_add(self, ip):
      try:
        af = get_af(ip)
      except ValueError as e:
        print(e)
        return

      if af == 4:
        target = self.target4
      else:
        target = self.target6
      r = subprocess.run(['/sbin/ip', 'route', 'add', ip] + shlex.split(target) + ['proto', self.proto], stderr=subprocess.PIPE)
      if r.returncode == 0:
        print("%s added" % ip)
      else:
        print("%s add failed: %s" % ip, r.stderr.decode('utf8'))

  def route_del(self, ip):
      try:
        af = get_af(ip)
      except ValueError as e:
        print(e)
        return

      if af == 4:
        target = self.target4
      else:
        target = self.target6
      r = subprocess.run(['/sbin/ip', 'route', 'del', ip, 'proto', self.proto], stderr=subprocess.PIPE)
      if r.returncode == 0:
        print("%s removed" % ip)
      else:
        print("%s remove failed: %s" % ip, r.stderr.decode('utf8'))


  def change(self, to_add, to_del):
    for ip in to_del:
        self.route_del(ip)
    for ip in to_add:
        self.route_add(ip)
    subprocess.run(['/sbin/ip', 'route', 'flush', 'cache'])
