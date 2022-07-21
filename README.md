# CssLoader-ThemeDb
A repo containing themes for SDH-CssLoader

# Making a theme for SDH-CssLoader
## Prerequisites
- You have some experience in json and css
- You have installed the Css loader
- (Optional) Have a chromium based browser installed

## Setting up the CEF debugger (Optional)
![Debugger](images/Readme/Debugger.png)

The CEF debugger is very useful for creating themes, as it allows you to play around directly with the style of the Steam deck UI.

The debugger allows you to access the multiple tabs that are used for the UI. A few common ones are:
- `SP`: The main UI of the steam deck
- `QuickAccess`: The quick access overlay
- `MainMenu` The Steam menu overlay

### Setup
1. Open a chromium based browser
2. Connect to `{deck ip}:8081` in the browser
    - You need to be on the same network as your deck
    - You can find the ip of your deck by going into your internet settings, selecting the current connected network, and looking at the `IP Address` field
3. Select a tab
    - After selecting a tab, you should be able to see the html and css used for that specific tab, like the screenshot above

## Making a theme compatible with the Css Loader
Themes are folders with css files and a single `theme.json` inside. The theme.json determines how everything will be displayed, and any dropdown options if the theme has them

### Simple themes
![SimpleTheme](images/Readme/simpletheme.png)

For a simple theme, like the image above, the theme json should look something like this

```json
{
    "name": "Clean Gameview",
    "author": "SuchMeme",
    "inject": {
        "shared.css": ["SP"]
    }
}
```

- The name element describes the theme name. This is also used as the folder name for the theme store.
- The author element describes the theme author.
- An optional field `"version": "v1.0"` can be added. If no version field is found, the version defaults to `v1.0`
- The inject tab is a dictionary of relative css file paths as keys, and a list of tabs you want the css to be injected into

### Complex themes
![ComplexTheme](images/Readme/complextheme.png)

A complex theme is a simple theme with patches. Patches are displayed as dropdown menus that apply additional css depending on the selection. A complex theme's json should look something like this:

```json
{
    "name": "Colored Toggles",
    "version": "v1.2",
    "author": "SuchMeme",
    "inject": {
        "shared.css": [
            "QuickAccess", "SP", "MainMenu"
        ] 
    },
    "patches": {
        "Theme Color": {
            "default": "Orange",
            "Orange": {},
            "Lime": {
                "colors/lime.css": ["QuickAccess", "SP", "MainMenu"]
            },
            "Red": {
                "colors/red.css": ["QuickAccess", "SP", "MainMenu"]
            },
            "Magenta": {
                "colors/magenta.css": ["QuickAccess", "SP", "MainMenu"]
            },
            "Gradient RGB": {
                "colors/gradient_rgb.css": ["QuickAccess", "SP", "MainMenu"]
            },
            "Gradient Deck": {
                "colors/gradient_deck.css": ["QuickAccess", "SP", "MainMenu"]
            }
        }
    }
}
```

- The patches section is a dictionary of patch names as key. The value is another dictionary, which keys are it's options, and their value is the same as the value of the "inject" section. A special key "default" is required to indicate which key is the default option

# Submitting a theme to the theme store

To submit a theme, fork this repository. Make a .json file called `{author}-{themename}.json`, and put it in the themes folder. You also need to provide a preview image. This preview image should go in the images folder. Preferably upload images in a .jpg format. The format for a remote .json is stated below

```json
{
    "repo_url": "https://github.com/suchmememanyskill/wagu", # Required, points to another github repository with the theme
    "repo_subpath": "MoreLibraryIcons", # Optional, defaults to '.', indicates the subpath to the folder containing the theme
    "repo_commit": "e04fdaf", # Required, the commit in the git repo you want to release
    "preview_image_path": images/Clean Gameview.jpg" # Required. This image is displayed in the browse themes UI of the plugin. The image needs to be located in this repository
}
```

After creating the necessary files, create a pull request to this repository