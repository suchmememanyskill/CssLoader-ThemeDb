from os import listdir
from os.path import isfile, join
import json, subprocess, tempfile, os, time, uuid

files = [f for f in listdir("./themes") if isfile(join("./themes", f)) and f.endswith(".json")]

class RepoReference:
    def __init__(self, json : dict):
        self.repoUrl = json["repo_url"] if "repo_url" in json else None
        self.repoSubpath = json["repo_subpath"] if "repo_subpath" in json else "."
        self.repoCommit = json["repo_commit"] if "repo_commit" in json else None
        self.previewImage = json["preview_image"] if "preview_image" in json else None
        self.repo = None
        self.id = str(uuid.uuid4())

    def verify(self):
        if self.repoUrl is None:
            raise Exception("No repo url was specified")
        
        if self.repoCommit is None:
            raise Exception("No commit was specified")
        
        if self.previewImage is None:
            raise Exception("No preview image was specified")

        if not self.previewImage.startswith("https://raw.githubusercontent.com/suchmememanyskill/CssLoader-ThemeDb"):
            raise Exception("Image is not located on this repo!")
    
    def toDict(self):
        return {
            "id": self.id,
            "repo_url": self.repoUrl,
            "repo_subpath": self.repoSubpath,
            "repo_commit": self.repoCommit,
            "preview_image": self.previewImage,
            "name": self.repo.name,
            "version": self.repo.version,
            "author": self.repo.author
        }
    
class Repo:
    def __init__(self, repoReference : RepoReference):
        self.repoReference = repoReference
        self.json = None
        self.name = None
        self.version = None
        self.author = None
        self.themePath = None
    
    def get(self):
        tempDir = tempfile.TemporaryDirectory()
        print(f"Cloning {self.repoReference.repoUrl} into {tempDir.name}...")
        subprocess.run([
            "git",
            "clone",
            self.repoReference.repoUrl,
            tempDir.name
        ], check=True)

        subprocess.run([
            "git",
            "-C",
            tempDir.name,
            "reset",
            "--hard",
            self.repoReference.repoCommit
        ], check=True)

        self.themePath = join(tempDir.name, self.repoReference.repoSubpath)
        themeDataPath = join(self.themePath, "theme.json")

        if not os.path.exists(themeDataPath):
            raise Exception("theme.json not found!")

        print(f"Reading {themeDataPath}")
        with open(themeDataPath, "r") as fp:
            data = json.load(fp)
        
        self.read(data)
        self.verify()

        print("Cleaning up temp dir...")
        tempDir.cleanup()
    
    def read(self, json : dict):
        self.json = json
        self.name = json["name"] if "name" in json else None
        self.version = json["version"] if "version" in json else "v1.0"
        self.author = json["author"] if "author" in json else None # This isn't required by the css loader but should be for the theme store 

    def verify(self):
        if self.json is None:
            raise Exception("No json was loaded?")
        
        if self.name is None:
            raise Exception("Theme has no name")
        
        if self.author is None:
            raise Exception("Theme has no author")
        
        if "inject" in self.json:
            for x in self.json["inject"]:
                if not os.path.exists(join(self.themePath, x)):
                    raise Exception("Inject contains css that does not exist")
                print(f"{x} exists in theme")
        
        if "patches" in self.json:
            for x in self.json["patches"]:
                patch = self.json["patches"][x]
                if "default" not in patch:
                    raise Exception(f"Missing default on patch {x}")
                
                for y in patch:
                    if isinstance(patch[y], dict):
                        for z in patch[y]:
                            if not os.path.exists(join(self.themePath, z)):
                                raise Exception(f"Patch {x} contains css that does not exist")
                            print(f"{z} exists in theme")

    

themes = []

for x in files:
    path = join("./themes", x)
    with open(path, "r") as fp:
        data = json.load(fp)

    reference = RepoReference(data)
    reference.verify()

    repo = Repo(reference)
    repo.get()
    reference.repo = repo
    themes.append(reference.toDict())

print("Done! Dumping result")
with open("themes.json", 'w') as fp:
    json.dump(themes, fp)