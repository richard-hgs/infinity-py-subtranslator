import subprocess
import json

def findall(pattern, text):
    regexResult = {'error_msg': None, 'result': {}}
    result = subprocess.run(['cli\\InfinityPcreTools', '--regex', pattern, '--text', text], stdout=subprocess.PIPE)
    try:
        jsonResult = json.loads(result.stdout)
        regexResult['result'] = jsonResult
        # print('%s', result.stdout)
    except Exception as e:
        print("text:", text, "- error:", result.stdout, e)
    return regexResult