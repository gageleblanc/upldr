from pathlib import Path
import json

class Loader:
  @staticmethod
  def getActiveModules():
    user_home = str(Path.home())
    with open(user_home + "/.local/upldr_config/modules.json") as f:
      moduleSpec = json.load(f)
    return moduleSpec
