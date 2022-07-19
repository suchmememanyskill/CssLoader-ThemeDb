# Theme name

To submit a theme or theme update, make or update a file called `{author}-{themename}.json` in the themes folder.
This .json file has 3 required fields, and 1 optional field

```
{
    "repo_url": "https://github.com/suchmememanyskill/wagu", # Required, points to another github repository with the theme
    "repo_subpath": "MoreLibraryIcons", # Optional, defaults to '.', indicates the subpath to the folder containing the theme
    "repo_commit": "e04fdaf", # Required, the commit in the git repo you want to release
    "preview_image": "https://raw.githubusercontent.com/suchmememanyskill/wagu/main/images/edge-case.jpg" # Required. This image is displayed in the browse themes UI of the plugin. The image needs to be located in this repository
}
```

## Checklist:

- [ ] I am the original author of this theme.
- [ ] I understand that messing with the repository remotely will lead to the immediate removal from this repository
- [ ] I have verified that my theme works properly on the latest versions of SteamOS, decky-loader and SDH-CssLoader.