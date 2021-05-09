from pathlib import Path
from os import walk
from upldr_libs.config_utils.loader import Loader as ConfigLoader
from clilib.util.util import Util
import json


class IndexData:
    def __init__(self):
        self.log = Util.configure_logging(__name__)
        user_home = str(Path.home())
        upldr_config_dir = user_home + "/.config/upldr_apiserver"
        config_dir = Path(upldr_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = str(config_dir) + "/slave_config.json"
        config_loader = ConfigLoader(config=config_file, keys=["data_dir", "timeout", "host"], auto_create=True)
        self.config = config_loader.get_config()
        self.category_list = []
        data_dirname = self.config.data_dir.split('/')[-1]
        for (dirpath, dirnames, filenames) in walk(self.config.data_dir):
            parsed_dir = dirpath.split('/')[-1]
            self.category_list = dirnames
            break
        self.categories = {}
        for category in self.category_list:
            cat_dir = "%s/%s" % (self.config.data_dir, category)
            for (dirpath, dirnames, filenames) in walk(cat_dir):
                self.categories[category] = {
                    "tags": dirnames
                }
                break
        self.tagged_files = {}
        self.tags_by_category = {}
        self.category_tags = {}
        for name, category in self.categories.items():
            for tag in category["tags"]:
                if name in self.category_tags:
                    self.category_tags[name].append(tag)
                else:
                    self.category_tags[name] = [tag]
                tag_dir = "%s/%s/%s" % (self.config.data_dir, name, tag)
                for (dirpath, dirnames, filenames) in walk(tag_dir):
                    if tag in self.tagged_files:
                        self.tagged_files[tag].extend(filenames)
                    else:
                        self.tagged_files[tag] = filenames

                    if name not in self.tags_by_category:
                        self.tags_by_category[name] = {}

                    if tag in self.tags_by_category[name]:
                        self.tags_by_category[name][tag].extend(filenames)
                    else:
                        self.tags_by_category[name][tag] = filenames

        self.data = {
            "categories": self.categories,
            "tagged_files": self.tagged_files,
            "tags_by_category": self.tags_by_category,
            "category_tags": self.category_tags
        }
        print(json.dumps(self.data))
