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
    
    #k.append('')
    def e(c):
        t = c%a
        return ("" if c < a else e(int(c/a))) + (chr(c+29) if t>35 else baseN(c, 36))
    if True:
        while c:
            d[e(c-1)] = k[c-1] or e(c)
            c = c-1
        c = 1
    r = re.compile('\\b\d\\b')
    for match in r.finditer(p):
        print "%s:%s" %(match.start(), match.end())
        p = p[0:match.start()] + d[match.group()] + p[match.end():]

    return p

c = unpacked('2.4("3://5.0.1")',62,6,'baidu|com|document|http|write|www'.split('|'),0,{})
print c