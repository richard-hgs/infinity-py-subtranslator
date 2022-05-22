import chardet

def decode(s):
    for encoding in "utf-8-sig", "utf-16":
        try:
            return s.decode(encoding)
        except UnicodeDecodeError:
            continue
    return s.decode("latin-1") # will always work

def fix_encoding(string, encodeAs = 'ascii'):
    strChars = list(string)
    strToReturn = '';
    for i in range(0, len(strChars)):
        charFixed = strChars[i]
        charOrd = ord(charFixed)
        charEncoding = chardet.detect(charFixed.encode())['encoding']
        if charEncoding == 'Windows-1252':
            if charOrd == 8212:
                if (encodeAs == 'ascii'):
                    charFixed = "-"

        strToReturn += charFixed
        print('char: ', ord(charFixed), " - ", charFixed)


    return strToReturn