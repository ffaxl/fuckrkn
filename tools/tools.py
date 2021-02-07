import time
import ipaddress
import dns.resolver


def gettime():
    return time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime()) + " %s" % time.tzname[0]


def get_af(ip):
  try:
    net = ipaddress.IPv6Network(ip)
  except ipaddress.AddressValueError:
    pass
  else:
    return 6

  try:
    net = ipaddress.IPv4Network(ip)
  except ipaddress.AddressValueError:
    pass
  else:
    return 4

  raise ValueError("Wrong address: %s" % ip)


def dns_resolve(name):
  if name.startswith("*."):
      name = name[2:]
  try:
    resolved = dns.resolver.query(name, "a")
  except (dns.resolver.NoAnswer, dns.exception.Timeout, dns.resolver.NoNameservers, dns.resolver.NXDOMAIN):
#    print("Unresolved: %s" % name)
    return []
  else:
    ips = [ip.to_text() for ip in resolved]
#    print("Resolved %s to %s" % (name, ','.join(ips)))
    return ips
