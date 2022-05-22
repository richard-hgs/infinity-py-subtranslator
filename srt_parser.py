import re
import string_utils as string_utils
import file_utils as file_utils

RE_SRT_1 = re.compile(r'(?P<index>\d+).'
    r'(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> '
    r'(?P<end>\d{2}:\d{2}:\d{2},\d{3}).'
    r'(?P<text>.*?)(\n\n|$)', re.DOTALL)

RE_SRT_2 = re.compile(r'(?P<index>\d+).'
    r'(?P<start>\d{2}:\d{2}:\d{2},\d{3}) --> '
    r'(?P<end>\d{2}:\d{2}:\d{2},\d{3}).'
    r'(?P<text>.*?)(\n\n|$)', re.DOTALL)

def from_srt(path):
    print(path)

    # Read srt file text
    srt_text = file_utils.readtxt_encoded(path)

    #print(srt_text)

    # Parse srt to array
    srt_array = []
    for i in RE_SRT_1.finditer(srt_text):
        srt_array.append((i.group('index'), i.group('start'),
                       i.group('end'), i.group('text')))

    #print(result)
    return srt_array

def to_srt(srt_array):
    # print(srt_array)

    srt_text = ""
    for i in range(0, len(srt_array)):
        srt_array_at = srt_array[i]

        srt_text += srt_array_at[0] + "\n"                                  # Srt index
        srt_text += srt_array_at[1] + " --> " + srt_array_at[2] + "\n"      # Srt time
        srt_text += srt_array_at[3] + "\n\n"                                # Srt time

    return srt_text