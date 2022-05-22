import file_utils as file_utils
import pcre as pcre
import chardet
import string_utils as string_utils

if __name__ == "__main__":
    print("Hello")
    path = 'D:/Media/Animes/Yowamushi Pedal/SUBDL.com--yowamushi.pedal.movie1480111/[HorribleSubs] Yowamushi Pedal The Movie - 00 [720p].ass'
    fileData = file_utils.readtxt_encoded(path)
    lines = fileData.splitlines()

    assBuffer = ""

    assEventsFormatList = None
    assEventsTextOffset = None
    for i in range(0, len(lines)):
        if i > 102:
            i += 60
        prevLine = None
        if i > 0:
            prevLine = lines[i - 1]

        lineAt = lines[i]

        # Events found in previous operation
        if assEventsTextOffset:
            if "," in lineAt:
                eventAtSplit = lineAt.split(",", len(assEventsFormatList) - 1)
                eventTextAt = eventAtSplit[assEventsTextOffset]

                # rResult = pcre.findall('(?<name>\\N)*(?<function>{+\\\\+[a-z0-9]+(\(+[0-9,]+\)+)*\}+)*(?<text>[a-z\sA-Z0-9.,!?]+)*', eventTextAt)
                the_encoding = chardet.detect(eventTextAt.encode())['encoding']
                if the_encoding == 'Windows-1252':
                    eventTextAt = string_utils.fix_encoding(eventTextAt)
                    the_encoding = chardet.detect(eventTextAt.encode())['encoding']
                # rResult = pcre.findall('(?<line_break>\\N)*(?<function>{+\\+[a-z0-9]+(\(+[0-9,]+\)+)*)*(?<text>[a-zA-Z0-9!@#$%¨&*\(\):;.,+=_\-]+)*(?![^{]*}|[^{}])*', eventTextAt)
                rResult = pcre.findall('(?<line_break>\\\\N)*(?<function>{+\\\\+[a-zA-Z0-9&]+(\\\\+[a-zA-Z0-9&]+)*(\\(+[0-9,]+\\)+)*)*(?<text>[a-zA-Z0-9!,\s\'\"\-:.;?!@#$%&*]+)*(?![^{]*}|[^{}])*', eventTextAt)
                if rResult['error_msg']:
                    print(rResult['error_msg'])
                    break
                else:
                    regexResult = rResult['result']
                    oldText = eventTextAt
                    newText = ''
                    for key in regexResult:
                        for groupKey in regexResult[key]['named_groups']:
                            groupObj = regexResult[key]['named_groups'][groupKey]
                            groupName = groupObj['name']
                            groupText = groupObj['text']
                            # print('match - key: ', key, ' - named_group:', groupName, ' - text:', groupText)
                            if groupName == 'function' and len(groupText) > 0:
                                newText += groupText + '}'
                            elif groupName == 'text':
                                print("")
                                newText += groupText
                            else:
                                newText += groupText
                    if newText != oldText:
                        print("oldText: ", oldText, " - newText:", newText)

                    print("progress: ", i, "/", len(lines), " - encoding:", the_encoding, ' - result: ', regexResult,
                          '\n\n')

                # Regex:
                # (?P<line_break>\\N*)*(?P<text>[a-zA-Z\s0-9:-]*)(?P<function>\{[\a-zA-Z]*\})*
                # (?P<line_break>\\N)(?P<function>\{\\+[a-z0-9]+(\(+[0-9,]+\)+)*\}+)(?P<text>[a-z\sA-Z]+)
                # (?P<line_break>\\N)*(?P<function>\{\\+[a-z0-9]+(\(+[0-9,]+\)+)*\}+)(?P<text>[a-z\sA-Z]+)*
                # (?<name>\\\\N)*(?<function>{\\\\+[a-z0-9]+(\\(+[0-9,]+\\)+)*\\}+)(?<text>[a-z\\sA-Z]+)*
                # regex = re.compile("(?P<name>\\\[N])(?P<function>{\\\+[a-z0-9]+(\(+[0-9,]+\)+)*\}+)(?P<text>[a-z\sA-Z]+)*", re.MULTILINE)
                # regexResults = regex.findall(eventTextAt)
                # if regexResults:
                #     for regexResult in regexResults:
                #         # regexResultGroups = regexResult.groups()
                #         if "{\\fad(2027,1)}{\\fs30}Yowamushi Pedal \\N{\\fs20}The Movie" in eventTextAt:
                #             print(eventTextAt)
                #             # print(regexResult, " - groups: ", regexResultGroups, "\n")

        if prevLine:
            if "[Events]" in prevLine:
                eventsFormatStrCleared = lineAt.replace("Format: ", "")
                assEventsFormatList = eventsFormatStrCleared.split(", ")
                for x in range(0, len(assEventsFormatList)):
                    eventNameAt = assEventsFormatList[x]
                    if "Text" in eventNameAt:
                        assEventsTextOffset = x
                        break
                print("EventsFound", len(assEventsFormatList), assEventsTextOffset, assEventsFormatList)


        assBuffer += lineAt + "\n"
        # print("Line:", line)

    # print(assBuffer)
