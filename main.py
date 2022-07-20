from os import listdir
from os.path import isfile, join
import json, subprocess, tempfile, os, time, uuid, boto3, binascii, hashlib, sys, shutil, requests
from botocore.config import Config
from dateutil.parser import parse

files = [f for f in listdir("./themes") if isfile(join("./themes", f)) and f.endswith(".json")]

UPLOAD_FILES = len(sys.argv) > 1 and sys.argv[1] == "upload"

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
                return f"{self.resource.ENDPOINT}/{x.bucket_name}/{x.key}"

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
        self.megaJson = requests.get("https://github.com/suchmememanyskill/CssLoader-ThemeDb/releases/download/1.0.0/themes.json").json()

    def getMegaJsonEntry(self, themeId : str) -> dict:
        for x in self.megaJson:
            if (themeId == x["id"]):
                return x
        return None


print("Getting megajson...")
megaJson = MegaJson()

class RepoReference:
    def __init__(self, json : dict, path : str):
        self.path = path
        self.repoUrl = json["repo_url"] if "repo_url" in json else None
        self.repoSubpath = json["repo_subpath"] if "repo_subpath" in json else "."
        self.repoCommit = json["repo_commit"] if "repo_commit" in json else None
        self.previewImage = ""
        self.previewImagePath = json["preview_image_path"] if "preview_image_path" in json else None
        self.downloadUrl = ""
        self.repo = None
        self.id = binascii.hexlify(hashlib.sha256(f"{self.repoUrl}.{self.repoSubpath}.{self.repoCommit}".encode("utf-8")).digest()).decode("ascii")
        self.megaJsonEntry = None

        result = subprocess.run(["git", "log", "-1", "--pretty=%ci", path], capture_output=True)
        dateText = result.stdout.decode("utf-8").strip()
        parsedDate = parse(dateText)
        self.lastChanged = parsedDate.isoformat()

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

        if self.repo != None:
            name = self.repo.name
            version = self.repo.version
            author = self.repo.author

        if self.megaJsonEntry != None:
            def possiblyReturnMegaJsonStuff(attribute : str, original):
                return self.megaJsonEntry[attribute] if attribute in self.megaJsonEntry else original

            themeId = possiblyReturnMegaJsonStuff("id", themeId)
            downloadUrl = possiblyReturnMegaJsonStuff("download_url", downloadUrl)
            previewImage = possiblyReturnMegaJsonStuff("preview_image", previewImage)
            name = possiblyReturnMegaJsonStuff("name", name)
            version = possiblyReturnMegaJsonStuff("version", version)
            author = possiblyReturnMegaJsonStuff("author", author)
        
        return {
            "id": themeId,
            "download_url": downloadUrl,
            "preview_image": previewImage,
            "name": name,
            "version": version,
            "author": author,
            "lastChanged": lastChanged,
        }
    
class Repo:
    def __init__(self, repoReference : RepoReference):
        self.repoReference = repoReference
        self.json = None
        self.name = None
        self.version = None
        self.author = None
        self.themePath = None
        self.repoPath = None
    
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

        if (UPLOAD_FILES):
            self.upload()

        print("Cleaning up temp dir...")
        tempDir.cleanup()
    
    def upload(self):
        self.hex = self.repoReference.id

        if (b2ThemeBucket.fileExists(f"{self.hex}.zip")):
            self.repoReference.downloadUrl = b2ThemeBucket.getFileUrl(f"{self.hex}.zip")
            return

        tempDir = tempfile.TemporaryDirectory()
        print(f"Generating zip...")
        shutil.copytree(self.themePath, join(tempDir.name, self.name))
        shutil.make_archive(self.hex, "zip", tempDir.name, ".")
        print("Uploading zip...")
        b2ThemeBucket.upload(f"{self.hex}.zip")
        b2ThemeBucket.loadFiles()
        self.repoReference.downloadUrl = b2ThemeBucket.getFileUrl(f"{self.hex}.zip")
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

        expectedFiles = [join(self.themePath, "theme.json")]
        
        if "inject" in self.json:
            for x in self.json["inject"]:
                if not os.path.exists(join(self.themePath, x)):
                    raise Exception("Inject contains css that does not exist")

                if not x.endswith(".css"):
                    raise Exception(f"Inject contains a non-css file '{x}'!")
                
                print(f"{x} exists in theme")
                expectedFiles.append(join(self.themePath, x))
        
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

                            if not z.endswith(".css"):
                                raise Exception(f"Path {x} contains a non-css file '{z}'!")

                            print(f"{z} exists in theme")
                            expectedFiles.append(join(self.themePath, z))
        
        actualFiles = []

        for root, dirs, files in os.walk(self.themePath):
            for f in files:
                actualFiles.append(join(root, f))

        if (os.name == "nt"):
            expectedFiles = [x.replace("/", "\\") for x in expectedFiles]
        
        print(expectedFiles)
        print(actualFiles)

        if (len(actualFiles) != len(expectedFiles)):
            raise Exception("Theme folder contains an unexpected amount of files!")

        for x in actualFiles:
            if x not in expectedFiles:
                raise Exception(f"Theme folder contains file '{x}' that is not referenced in a theme!")

        totalSize = 0
        for x in expectedFiles:
            size = os.path.getsize(x)
            totalSize += size
            print(f"{x} is {size} bytes")

        print(f"Total theme size is {totalSize} bytes")

        if (totalSize > 0x100000): # 1 MB max per theme
            raise Exception("Total theme size exceeds 1MB")

    

themes = []

for x in files:
    path = join("./themes", x)
    print(f"Processing {path}...")
    with open(path, "r") as fp:
        data = json.load(fp)

    reference = RepoReference(data, path)
    reference.verify()

    if (reference.existsInMegaJson()):
        print(f"Skipping {path} as it's up to date")
        themes.append(reference.toDict())
        continue

    repo = Repo(reference)
    repo.get()
    reference.repo = repo
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