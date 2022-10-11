from os import listdir
from os.path import isfile, join
import json, subprocess, tempfile, os, time, uuid, boto3, binascii, hashlib, sys, shutil, requests
from botocore.config import Config
from dateutil.parser import parse
from discord_webhook import DiscordWebhook, DiscordEmbed

if (os.path.exists("zips")):
    shutil.rmtree("zips")

os.mkdir("zips")

files = [f for f in listdir("./themes") if isfile(join("./themes", f)) and f.endswith(".json")]

UPLOAD_FILES = "upload" in sys.argv
FORCE_REFRESH = "force" in sys.argv

VALID_TARGETS = [
    "System-Wide",
    "Keyboard",
    "Home",
    "Background",
    "Library",
    "Store",
    "Friends and Chat",
    "Media",
    "Downloads",
    "Settings",
    "Lock Screen",
    "Tweak",
    "Other",
]

# Stolen from https://github.com/backblaze-b2-samples/b2-python-s3-sample/blob/main/sample.py
class B2Bucket():
    def __init__(self, b2Connection, bucket):
        self.resource = b2Connection
        self.bucket = bucket
        self.loadFiles()
        pass

    def loadFiles(self):
        self.files = [x for x in self.bucket.objects.all()]
    
    def fileExists(self, fileName : str) -> bool:
        for x in self.files:
            if x.key == fileName:
                return True
        return False

    def getFileUrl(self, fileName : str) -> str:
        for x in self.files:
            if x.key == fileName:
                return f"https://cdn.beebl.es/file/{x.bucket_name}/{x.key}"

        return None
    
    def upload(self, path : str):
        filename = os.path.basename(path)
        self.bucket.upload_file(path, filename)

class B2Connection():
    def __init__(self):
        self.ENDPOINT = os.getenv("SECRET_ENDPOINT")
        self.KEYID = os.getenv("SECRET_KEYID")
        self.APPLICATIONKEY = os.getenv("SECRET_APPLICATIONKEY")
        self.resource = boto3.resource(service_name='s3',
                        endpoint_url=self.ENDPOINT,                # Backblaze endpoint
                        aws_access_key_id=self.KEYID,              # Backblaze keyID
                        aws_secret_access_key=self.APPLICATIONKEY, # Backblaze applicationKey
                        config = Config(
                            signature_version='s3v4',
                        ))
    
    def getBucket(self, bucketName : str) -> B2Bucket:
        bucket = self.resource.Bucket(bucketName)
        return B2Bucket(self, bucket)


b2Connection = None
b2ThemeBucket = None

if (UPLOAD_FILES):
    print("Connecting to backblaze...")
    b2Connection = B2Connection()
    b2ThemeBucket = b2Connection.getBucket("deck-themes")

class MegaJson():
    def __init__(self):
        self.megaJson = requests.get("https://github.com/suchmememanyskill/CssLoader-ThemeDb/releases/download/1.1.0/themes.json").json()

    def getMegaJsonEntry(self, themeId : str) -> dict:
        for x in self.megaJson:
            if (themeId == x["id"]):
                return x
        return None
    
    def doesThemeExist(self, themeName : str) -> bool:
        for x in self.megaJson:
            if (themeName == x["name"]):
                return True
        
        return False


print("Getting megajson...")
megaJson = MegaJson()

class RepoReference:
    def __init__(self, json : dict, path : str):
        self.path = path
        self.repoUrl = json["repo_url"] if "repo_url" in json else None
        self.repoSubpath = json["repo_subpath"] if "repo_subpath" in json else "."
        self.repoCommit = json["repo_commit"] if "repo_commit" in json else None
        self.overrides = json["overrides"] if "overrides" in json else {}
        self.previewImage = ""
        self.previewImagePath = json["preview_image_path"] if "preview_image_path" in json else None
        self.downloadUrl = ""
        self.repo = None
        self.id = binascii.hexlify(hashlib.sha256(f"{self.repoUrl}.{self.repoSubpath}.{self.repoCommit}".encode("utf-8")).digest()).decode("ascii")
        self.megaJsonEntry = None
        self.target = None

        result = subprocess.run(["git", "log", "-1", "--pretty=%ci", path], capture_output=True)
        dateText = result.stdout.decode("utf-8").strip()
        if (dateText == ""):
            # Assume the theme is new. This will get fixed when it's actually committed
            self.lastChanged = ""
        else:
            parsedDate = parse(dateText)
            self.lastChanged = parsedDate.isoformat()

        self.override()

    def override(self):
        self.target = self.overrides["target"] if "target" in self.overrides else self.target

    def verify(self):
        if self.repoUrl is None:
            raise Exception("No repo url was specified")
        
        if self.repoCommit is None:
            raise Exception("No commit was specified")
        
        if self.previewImagePath is None:
            raise Exception("No preview image was specified")

        if not os.path.exists(self.previewImagePath):
            raise Exception("Image does not exist in repo")
        
        self.previewImage = f"https://raw.githubusercontent.com/suchmememanyskill/CssLoader-ThemeDb/main/{self.previewImagePath}"
    
    def existsInMegaJson(self) -> bool:
        self.megaJsonEntry = megaJson.getMegaJsonEntry(self.id)
        return self.megaJsonEntry != None

    def toDict(self):
        themeId = self.id
        downloadUrl = self.downloadUrl
        previewImage = self.previewImage
        name = None
        version = None
        author = None
        lastChanged = self.lastChanged
        target = self.target
        repo = self.repoUrl
        manifestVersion = 1
        description = None

        if self.repo != None:
            name = self.repo.name
            version = self.repo.version
            author = self.repo.author
            target = self.repo.target
            manifestVersion = self.repo.manifestVersion
            description = self.repo.description

        if self.megaJsonEntry != None:
            def possiblyReturnMegaJsonStuff(attribute : str, original):
                return self.megaJsonEntry[attribute] if attribute in self.megaJsonEntry else original

            themeId = possiblyReturnMegaJsonStuff("id", themeId)
            downloadUrl = possiblyReturnMegaJsonStuff("download_url", downloadUrl)
            previewImage = possiblyReturnMegaJsonStuff("preview_image", previewImage)
            name = possiblyReturnMegaJsonStuff("name", name)
            version = possiblyReturnMegaJsonStuff("version", version)
            author = possiblyReturnMegaJsonStuff("author", author)
            target = possiblyReturnMegaJsonStuff("target", target)
            manifestVersion = possiblyReturnMegaJsonStuff("manifest_version", manifestVersion)
            description = possiblyReturnMegaJsonStuff("description", description)
        
        return {
            "id": themeId,
            "download_url": downloadUrl,
            "preview_image": previewImage,
            "name": name,
            "version": version,
            "author": author,
            "last_changed": lastChanged,
            "target": target,
            "source": repo,
            "manifest_version": manifestVersion,
            "description": description,
        }
    
class Repo:
    def __init__(self, repoReference : RepoReference):
        self.repoReference = repoReference
        self.json = None
        self.name = None
        self.version = None
        self.author = None
        self.target = repoReference.target
        self.hex = self.repoReference.id
        self.themePath = None
        self.repoPath = None
        self.manifestVersion = None
        self.description = None 
    
    def get(self):
        tempDir = tempfile.TemporaryDirectory()
        print(tempDir.name)
        if self.repoReference.repoUrl != "LOCAL":
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
        else:
            shutil.copytree(self.repoReference.repoSubpath, join(tempDir.name, "theme"))
            self.themePath = join(tempDir.name, "theme")
        
        themeDataPath = join(self.themePath, "theme.json")

        if not os.path.exists(themeDataPath):
            raise Exception("theme.json not found!")

        print(f"Reading {themeDataPath}")
        with open(themeDataPath, "r") as fp:
            data = json.load(fp)
        
        self.read(data)
        self.verify()
        self.zip()

        if (UPLOAD_FILES):
            self.upload()

        print("Cleaning up temp dir...")
        tempDir.cleanup()
    
    def zip(self):
        tempDir = tempfile.TemporaryDirectory()
        print(f"Generating zip...")
        shutil.copytree(self.themePath, join(tempDir.name, self.name))
        shutil.make_archive(join("zips", self.hex), "zip", tempDir.name, ".")
        tempDir.cleanup()

    def upload(self):
        if (b2ThemeBucket.fileExists(f"{self.hex}.zip")):
            self.repoReference.downloadUrl = b2ThemeBucket.getFileUrl(f"{self.hex}.zip")
            return

        print("Uploading zip...")
        b2ThemeBucket.upload(join("zips",f"{self.hex}.zip"))
        b2ThemeBucket.loadFiles()
        self.repoReference.downloadUrl = b2ThemeBucket.getFileUrl(f"{self.hex}.zip")

    def read(self, json : dict):
        self.json = json
        self.name = str(json["name"]) if "name" in json else None
        self.version = str(json["version"]) if "version" in json else "v1.0"
        self.author = str(json["author"]) if "author" in json else None # This isn't required by the css loader but should be for the theme store 
        self.target = str(json["target"]) if "target" in json else self.target # This isn't used by the css loader but used for sorting instead
        self.manifestVersion = int(json["manifest_version"]) if "manifest_version" in json else 1
        self.description = str(json["description"]) if "description" in json else ""

    def verify(self):
        if self.json is None:
            raise Exception("No json was loaded?")
        
        if self.name is None:
            raise Exception("Theme has no name")
        
        if self.author is None:
            raise Exception("Theme has no author")
        
        if (self.target is None):
            raise Exception("Theme has no target!")

        if (self.target not in VALID_TARGETS):
            raise Exception(f"'{self.target}' is not a valid target!")

        releasePath = join(self.themePath, "release.json") if os.path.exists(join(self.themePath, "release.json")) else "release.json"

        with open(releasePath, "r") as fp:
            data = json.load(fp)

        if not isinstance(data, dict) and not "include" in data and not "ignore" in data:
            raise Exception("Invalid ignore.json")

        data["ignore"].append("release.json")
        
        for x in data["ignore"]:
            if os.path.exists(join(self.themePath, x)):
                os.remove(join(self.themePath, x))
                print(f"Removing {x} from theme")

        expectedFiles = [join(self.themePath, "theme.json")]

        for x in data["include"]:
            expectedFiles.append(join(self.themePath, x))
        
        if "dependencies" in self.json:
            if self.manifestVersion < 3: # Dependencies got introduced in manifest v3
                raise Exception("A v3+ Patch was detected but a v2 or v1 manifest was provided")

            for x in self.json["dependencies"]:
                if not megaJson.doesThemeExist(x):
                    raise Exception("Theme dependency does not exist on the themedb")


        if "inject" in self.json:
            for x in self.json["inject"]:
                if not os.path.exists(join(self.themePath, x)):
                    raise Exception("Inject contains css that does not exist")

                if not x.endswith(".css"):
                    raise Exception(f"Inject contains a non-css file '{x}'!")
                
                # print(f"{x} exists in theme")
                filePath = join(self.themePath, x)
                if filePath not in expectedFiles:
                    expectedFiles.append(filePath)
        
        if "patches" in self.json:
            for x in self.json["patches"]:
                patch = self.json["patches"][x]
                if "default" not in patch and self.manifestVersion < 3: # Default is only required on pre-3 manifest
                    raise Exception(f"Missing default on patch {x}")
                
                if "type" in patch:
                    if patch["type"] not in ["dropdown", "checkbox", "slider", "none"]:
                        raise Exception(f"Type '{patch['type']}' is not a valid type!")


                values = None

                if "values" in patch: # V2 patch
                    if self.manifestVersion < 2: # Manifest version needs to be set to 2 or above to support v2 patches
                        raise Exception("A v2+ Patch was detected but a v1 manifest was provided")

                    values = patch["values"]
                else: # V1 patch
                    if self.manifestVersion > 1: # Manifest version needs to be set to 1 or below to support v1 patches
                        raise Exception("A v1 patch was detected but a v2+ manifest was provided")

                    values = patch
                    del patch["default"]
                
                if "default" not in patch:
                    default = list(values.keys())[0]
                else:
                    default = patch["default"]

                if default not in values:
                    raise Exception("Default does not exist")
                
                for y in values:
                    if isinstance(values[y], dict):
                        for z in values[y]:
                            if not os.path.exists(join(self.themePath, z)):
                                raise Exception(f"Patch '{x}' contains css that does not exist")

                            if not z.endswith(".css"):
                                raise Exception(f"Path '{x}' contains a non-css file '{z}'!")

                            # print(f"{z} exists in theme")
                            filePath = join(self.themePath, z)
                            if filePath not in expectedFiles:
                                expectedFiles.append(filePath)
                    else:
                        raise Exception(f"Non-dictionary in values of patch '{x}'")
                
                if "components" in patch:
                    if self.manifestVersion < 3: # Components got introduced in manifest v3
                        raise Exception("A v3+ Patch was detected but a v2 or v1 manifest was provided")
                    
                    if not isinstance(patch["components"], list):
                        raise Exception("Components is not a list??")

                    for z in patch["components"]:
                        items = ["name", "type", "on", "default", "css_variable", "tabs"]

                        for i in items:
                           if i not in z:
                               raise Exception(f"Field {y} not found in component of '{x}'")

                        valid_types = ["color-picker", "image-picker"] if self.manifestVersion >= 4 else ["color-picker"]

                        if (z["type"] not in valid_types):
                            raise Exception(f"Component type {z['type']} not found")
                        
                        if (z["on"] not in values):
                            raise Exception(f"{z['on']} value was not found in patch")

        
        actualFiles = []

        for root, dirs, files in os.walk(self.themePath):
            for f in files:
                actualFiles.append(join(root, f))

        if (os.name == "nt"):
            expectedFiles = [x.replace("/", "\\") for x in expectedFiles]
            actualFiles = [x.replace("/", "\\") for x in actualFiles]

        file_validation_fail = False

        for x in expectedFiles:
            if x in actualFiles:
                print(f"[OK] {x[len(self.themePath):]}")
            else:
                print(f"[MISSING] {x[len(self.themePath):]}")
                file_validation_fail = True
        
        for x in [x for x in actualFiles if x not in expectedFiles]:
            print(f"[EXCESS] {x[len(self.themePath):]}")
            file_validation_fail = True

        if (file_validation_fail):
            raise Exception("File validation failed")

        if (len(actualFiles) != len(expectedFiles)):
            raise Exception("Theme folder contains an unexpected amount of files!")

        totalSize = 0
        for x in expectedFiles:
            size = os.path.getsize(x)
            totalSize += size
            # print(f"{x} is {size} bytes")

        print(f"Total theme size is {totalSize} bytes")

        if (totalSize > 0x400000): # 4 MB max per theme
            raise Exception("Total theme size exceeds 4MB")

class DiscordWebhooks:
    def __init__(self):
        envStr = os.getenv("SECRET_DISCORD_WEBHOOKS")
        self.urls = []
        if (envStr != None):
            self.urls = envStr.split("@")
    
    def send(self, repo : Repo):
        if (self.urls == []):
            return
        
        try:
            webhook = DiscordWebhook(self.urls, rate_limit_retry=True)
            embed = DiscordEmbed(title=repo.name, description=repo.target, color="03b2f8")
            embed.set_image(url=repo.repoReference.previewImage.replace(" ", "%20"))
            embed.set_footer(text=f"By {repo.author} | {repo.version}")
            webhook.add_embed(embed)
            webhook.execute()
        except Exception as e:
            print(f"Failed to send webhook... {str(e)}")
    

webhooks = DiscordWebhooks()

themes = []

for x in files:
    path = join("./themes", x)
    print(f"Processing {path}...")
    with open(path, "r") as fp:
        data = json.load(fp)

    reference = RepoReference(data, path)
    reference.verify()

    if not FORCE_REFRESH and reference.existsInMegaJson():
        print(f"Skipping {path} as it's up to date")
        themes.append(reference.toDict())
        continue

    repo = Repo(reference)
    repo.get()
    reference.repo = repo

    webhooks.send(repo)
    themes.append(reference.toDict())

print("Verifying there are no identical themes")
for x in themes:
    if len([y for y in themes if y["name"] == x["name"]]) > 1:
        raise Exception(f"Multiple themes with the same name detected in the repository! Name is '{x['name']}'")

print("Sorting db...")

def getName(elem):
    return elem["name"]

themes.sort(key=getName)

print("Done! Dumping result")
with open("themes.json", 'w') as fp:
    json.dump(themes, fp)