import json


league_str = '''
{
    "teams": ["bos", "mia", "sas"],
}
'''

data = json.loads(league_str)
