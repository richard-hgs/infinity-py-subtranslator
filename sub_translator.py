import srt_parser as srt_parser
import deepl_manager as deepl_manager
import file_utils as file_utils
import string_utils
import os
import chardet
import pcre

DEBUG_ASS = 0

def translate(path, start=0, end=0, driver=None):
    fileExtension = os.path.splitext(path)[1]
    if fileExtension == '.srt':
        translate_srt(path, start, end, driver)
    elif fileExtension == '.ass':
        translate_ass(path, start, end, driver)

def translate_ass(path, start=0, end=0, driver=None):
    if (driver is None and DEBUG_ASS == 0):
        print("isNone")
        # Open broser translator
        driver = deepl_manager.open_browser()

    fileData = file_utils.readtxt_encoded(path)
    lines = fileData.splitlines()

    start_ass = -1
    end_ass = -1

    curr_ass = 0
    first_ass_pos = 0

    assEventsFormatList = None
    assEventsTextOffset = None
    for i in range(0, len(lines)):
        prevLine = None
        if i > 0:
            prevLine = lines[i - 1]

        lineAt = lines[i]

        # Events found in previous operation
        if assEventsTextOffset:
            if "," in lineAt:
                if first_ass_pos == 0:
                    first_ass_pos = i

                    start_ass = 0
                    end_ass = (len(lines) - first_ass_pos) + 1

                    if (start > 0 and start < end_ass):
                        start_ass = start
                    if (end > 0 and end < end_ass):
                        end_ass = end

                if (start_ass <= curr_ass) and (end_ass - 1 > curr_ass):
                    eventAtSplit = lineAt.split(",", len(assEventsFormatList) - 1)
                    eventTextAt = eventAtSplit[assEventsTextOffset]

                    # rResult = pcre.findall('(?<name>\\N)*(?<function>{+\\\\+[a-z0-9]+(\(+[0-9,]+\)+)*\}+)*(?<text>[a-z\sA-Z0-9.,!?]+)*', eventTextAt)
                    the_encoding = chardet.detect(eventTextAt.encode())['encoding']
                    if the_encoding == 'Windows-1252':
                        eventTextAt = string_utils.fix_encoding(eventTextAt)
                        the_encoding = chardet.detect(eventTextAt.encode())['encoding']
                    # rResult = pcre.findall('(?<line_break>\\N)*(?<function>{+\\+[a-z0-9]+(\(+[0-9,]+\)+)*)*(?<text>[a-zA-Z0-9!@#$%¨&*\(\):;.,+=_\-]+)*(?![^{]*}|[^{}])*', eventTextAt)
                    rResult = pcre.findall(
                        # (?<line_break>\\N)*(?<escape2>(\\h)+)*(?<function>({+)*\\+([a-zA-Z0-9&,.]+)*(\(+[0-9.,]+\)+)*)*(?<text>[a-zA-Z0-9!,\s\'\"\-:.;?!@#$%&*]+)*(?![^{]*}|[^{}])*
                        # (?<line_break>\\N)*(?<escape2>(\\h)+)*(?<function>{+\\+[a-zA-Z0-9&]+(\\+[a-zA-Z0-9&.]+)*(\(+[0-9.,]+\)+)*)*(?<text>[a-zA-Z0-9!,\s\'\"\-:.;?!@#$%&*]+)*(?![^{]*}|[^{}])*
                        # (?<line_break>\\N)*(?<escape2>(\\h)+)*(?<function>{+((\\+[a-zA-Z0-9&.]+)*(\(+[0-9.,]+\)+)*)*)*(?<text>[a-zA-Z0-9!,\s\'\"\-:.;?!@#$%&*]+)*(?![^{]*}|[^{}])*
                        # (?<line_break>\\N)*(?<escape2>(\\h)+)*(?<function>{+((\\\\+[a-zA-Z0-9&.]+)*(\\(+[0-9.,]+\\)+)*)*)*(?<text>[a-zA-Z0-9!,\s\'\"\-:.;?!@#$%&*]+)*(?![^{]*}|[^{}])*
                        '(?<line_break>\\\\N)*(?<escape2>(\\\h)+)*(?<function>{+((\\\\+[a-zA-Z0-9&.]+)*(\\(+[0-9.,]+\\)+)*)*)*(?<text>[a-zA-Z0-9!,\s\'\"\-:.;?!@#$%&*]+)*(?![^{]*}|[^{}])*',
                        eventTextAt)
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
                                if (groupName == 'function') and len(groupText) > 0:
                                    newText += groupText
                                    if (groupName == 'function'):
                                        newText += '}'
                                elif groupName == 'text':
                                    if (DEBUG_ASS == 0):
                                        newText += deepl_manager.translate(driver, groupText)
                                    else:
                                        newText += groupText
                                else:
                                    newText += groupText
                        if (DEBUG_ASS == 1 and newText != oldText):
                            print("oldText: ", oldText, " - newText:", newText)

                        if (DEBUG_ASS == 0):
                            print("progress: ", curr_ass, "/", end_ass, " - text:", oldText, ' - translated: ', newText, '\n\n')
                            print("oldLine: ", lineAt, "\n")
                        lineAt = ''
                        for x in range(0, len(eventAtSplit)):
                            if x == assEventsTextOffset:
                                lineAt += newText
                            else:
                                lineAt += eventAtSplit[x]

                            if x < len(eventAtSplit) - 1:
                                lineAt += ','
                        if (DEBUG_ASS == 0):
                            print("newLine: ", lineAt, "\n")

                        (path, fileBaseName, fileName, fileExt, fileDirPath, fileDirParts) = file_utils.split_path(path)
                        translatedFilePath = fileDirPath + "/" + fileName + "_pt_BR" + fileExt
                        ass_text = ''
                        if not os.path.exists(translatedFilePath):
                            for assLinePos in range(0, i - 1):
                                ass_text += lines[assLinePos] + "\n"
                        ass_text += lineAt + "\n"

                        file_utils.writetxt_encoded(translatedFilePath, ass_text)

                curr_ass += 1

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
        # print("Line:", line)

    # print(assBuffer)

def translate_srt(path, start=0, end=0, driver=None):
    if (driver is None):
        print("isNone")
        # Open broser translator
        driver = deepl_manager.open_browser()

    # Read and parse srt to srt_array
    srt_array = srt_parser.from_srt(path)

    srt_translated_array = []
    start_srt = 0
    end_srt = len(srt_array)

    if (start > 0 and start < end_srt):
        start_srt = start
    if (end > 0 and end < end_srt):
        end_srt = end

    # For every item from srt_array
    for i in range(start, end_srt):
        (index, start_time, end_time, text) = srt_array[i]

        srt_translated_array.append((index, start_time,
                                     end_time, deepl_manager.translate(driver, text)))
        print(index, "\n- progress: ", i, "/", end_srt, "\n  text:", text, "\n- translated:",
              srt_translated_array[i - start][3])

        # After translation write new file with specified name
        (path, fileBaseName, fileName, fileExt, fileDirPath, fileDirParts) = file_utils.split_path(path)
        srt_txt = srt_parser.to_srt([srt_translated_array[i - start]])
        file_utils.writetxt_encoded(fileDirPath + "/" + fileName + "_pt_BR" + fileExt, srt_txt)