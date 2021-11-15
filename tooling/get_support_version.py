import json

def get_support_version(branch):
   with open("supported-ocp-versions.json", "r", encoding="UTF-8") as file:
      obj = json.load(file)
   return obj[branch]