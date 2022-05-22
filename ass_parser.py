import re
import file_utils as file_utils

RE_ASS_1 = re.compile(r'(?P<script_info>\[Script Info\]'
                      r'(?P<script_info_comments>\s; [\w:. ]*\s)*'
                      r')')

def from_ass(path):
    print(path)

    # Read ass file text
    ass_text = file_utils.readtxt_encoded(path)

    ass_info = {
        'script_info': {}
    }

    print("regex: ", RE_ASS_1)

    for i in RE_ASS_1.finditer(ass_text):
        print("group -> script_info: ", i.group("script_info"))
        print("group -> script_info_comments: ", i.group("script_info_comments"))
