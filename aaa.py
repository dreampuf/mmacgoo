val = open("aaa.txt").read()
'''
function(p, a, c, k, e, d) {
    e = function(c) {
        return (c < a ? "": e(parseInt(c / a))) + ((c = c % a) > 35 ? String.fromCharCode(c + 29) : c.toString(36))
    };
    if (!''.replace(/^/, String)) {
        while (c--) d[e(c)] = k[c] || e(c);
        c = 1;
    };
    while (c--) if (k[c]) p = p.replace(new RegExp('\\b' + e(c) + '\\b', 'g'), k[c]);
    return p;
}
'''
import string, re
def baseN(num,b):
  return ((num == 0) and  "0" ) or ( baseN(num // b, b).lstrip("0") + "0123456789abcdefghijklmnopqrstuvwxyz"[num % b])
def unpacked(p, a, c, k, e, d):
    def e(c):
        t = c%a
        return ("" if c < a else e(int(c/a))) + (chr(c+29) if t>35 else baseN(c, 36))
    if True:
        while c:
            d[e(c-1)] = k[c-1] or e(c)
            c = c-1
        c = 1
    r = re.compile('\\b\d\\b')
    return r.sub(lambda x: d[x.group()], p)
    return p

#match = re.match("eval\(function\(p,a,c,k,e,d\).+return p;}\((.+?)\)\)", val)
#c = unpacked(match.group())
#print c
#print unpacked(*eval(match.group(1)))

import datetime

ZERO_TIME_DELTA = datetime.timedelta(0)
class LocalTimezone(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=8)

    def dst(self, dt):
        return ZERO_TIME_DELTA

class UTC(datetime.tzinfo):
    def utcoffset(self, dt):
        return ZERO_TIME_DELTA

    def dst(self, dt):
        return ZERO_TIME_DELTA

a = datetime.datetime.now().replace(tzinfo=UTC()).astimezone(LocalTimezone())
print a

b = datetime.datetime.strptime("2010/12/15 16:22:47", "%Y/%m/%d %H:%M:%S").replace(tzinfo=LocalTimezone()).astimezone(UTC())
#b = b.replace(tzinfo=LocalTimezone())
print b