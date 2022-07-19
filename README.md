# CssLoader-ThemeDb
A repo containing themes for SDH-CssLoader

## Submitting a theme

To submit a theme, fork this repository. Make a .json file called `{author}-{themename}.json`, and put it in the themes folder. Feel free to put a preview image in the images folder. This .json file has 3 required fields, and 1 optional field

```
{
    "repo_url": "https://github.com/suchmememanyskill/wagu", # Required, points to another github repository with the theme
    "repo_subpath": "MoreLibraryIcons", # Optional, defaults to '.', indicates the subpath to the folder containing the theme
    "repo_commit": "e04fdaf", # Required, the commit in the git repo you want to release
    "preview_image_path": images/Clean Gameview.jpg" # Required. This image is displayed in the browse themes UI of the plugin. The image needs to be located in this repository
}
```

After creating the necessary files, create a pull request to this repository