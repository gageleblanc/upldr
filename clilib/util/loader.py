from pathlib import Path
import json

class Loader:
  @staticmethod
  def getActiveModules():
    rootdir = Path(__file__).parent.parent.parent.absolute()
    with open(str(rootdir) + "/modules.json") as f:
      moduleSpec = json.load(f)
    return moduleSpec
