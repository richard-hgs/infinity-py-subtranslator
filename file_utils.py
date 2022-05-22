import os
import io
import chardet
import codecs

def split_path(path):
    fileBaseName = os.path.basename(path)
    fileName = os.path.splitext(fileBaseName)[0]
    fileExt = os.path.splitext(fileBaseName)[1]
    fileDirPath = os.path.dirname(path)
    fileDirParts = []

    tmpPath = fileDirPath
    while 1:
        parts = os.path.split(tmpPath)
        if parts[0] == tmpPath:  # sentinel for absolute paths
            fileDirParts.insert(0, parts[0])
            break
        elif parts[1] == tmpPath:  # sentinel for relative paths
            fileDirParts.insert(0, parts[1])
            break
        else:
            tmpPath = parts[0]
            fileDirParts.insert(0, parts[1])

    # print("fileBaseName:", fileBaseName)
    # print("fileName:", fileName)
    # print("fileExt:", fileExt)
    # print("fileDirs:", fileDirPath)
    # print("fileDirParts:", fileDirParts)

    return (path, fileBaseName, fileName, fileExt, fileDirPath, fileDirParts)

def readtxt_encoded(path):
    bytes = min(32, os.path.getsize(path))
    raw = open(path, 'rb').read(bytes)

    if raw.startswith(codecs.BOM_UTF8):
        encoding = 'utf-8-sig'
    else:
        result = chardet.detect(raw)
        encoding = result['encoding']

    infile = io.open(path, 'r', encoding=encoding)
    data = infile.read()
    infile.close()

    return data

def writetxt_encoded(path, text, mode="a"):
    # Open a file with access mode 'a'
    file_object = open(path, mode)
    # Append 'hello' at the end of file
    file_object.write(text)
    # Close the file
    file_object.close()

def list_files(path, extensions=None, ignored_words=[], required_words=[]):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if (len(ignored_words) > 0):
                file_ignored = False
                for word in ignored_words:
                    if (word in file):
                        file_ignored = True
                        break
                if (file_ignored):
                    continue
            if (len(required_words) > 0):
                file_accepted = False
                for word in required_words:
                    if (word in file):
                        file_accepted = True
                        break
                if (file_accepted == False):
                    continue

            if (extensions is not None):
                for extAt in extensions:
                    if extAt in file:
                        files.append(os.path.join(r, file))
                        break
            else:
                files.append(os.path.join(r, file))

    return files