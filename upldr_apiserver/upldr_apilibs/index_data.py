from pathlib import Path
from os import walk
from upldr_libs.config_utils.loader import Loader as ConfigLoader
from clilib.util.util import Util
import json


class IndexData:
    def __init__(self):
        self.log = Util.configure_logging(name=__name__)
        user_home = str(Path.home())
        upldr_config_dir = user_home + "/.config/upldr_apiserver"
        config_dir = Path(upldr_config_dir)
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file = str(config_dir) + "/slave_config.json"
        config_loader = ConfigLoader(config=config_file, keys=["data_dir", "timeout", "host"], auto_create=True)
        self.config = config_loader.get_config()
        self.log.info("Indexing data directory")
        self.category_list = self._get_dirs(self.config.data_dir)
        self.categories = {}
        self.category_files = []
        for category in self.category_list:
            cat_dir = "%s/%s" % (self.config.data_dir, category)
            self.categories[category] = {
                "tags": self._get_dirs(cat_dir)
            }
            self.category_files = self._get_files(cat_dir)
        self.tagged_files = {}
        self.tags_by_category = {}
        self.category_tags = {}
        for name, category in self.categories.items():
            self.log.info("Found category: [%s]" % name)
            self.tags_by_category[name] = {}
            for tag in category["tags"]:
                self.log.info("Found tag [%s] in category [%s]" % (tag, name))
                if name in self.category_tags:
                    self.category_tags[name].append(tag)
                else:
                    self.category_tags[name] = [tag]
                tag_dir = "%s/%s/%s" % (self.config.data_dir, name, tag)
                self.tagged_files[tag] = self._get_files(tag_dir)
                self.tags_by_category[name][tag] = self._get_files(tag_dir)
                self.log.info("Done processing tag [%s]" % tag)
            self.log.info("Done processing category [%s]" % name)

        self.data = {
            "categories": self.categories,
            "tagged_files": self.tagged_files,
            "index": self.tags_by_category,
            "category_tags": self.category_tags
        }
        self._write_index()

    def _write_index(self):
        self.log.info("Writing indexes")
        with open(self.config.data_dir + "/index.json", 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def _get_files(self, path):
        files = []
        for (dirpath, dirnames, filenames) in walk(path):
            files.extend(filenames)
        return files

    def _get_dirs(self, path):
        dirs = []
        for (dirpath, dirnames, filenames) in walk(path):
            dirs.extend(dirnames)
            break
        return dirs

