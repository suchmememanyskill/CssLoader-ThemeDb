# CssLoader-ThemeDb
A repo containing themes for SDH-CssLoader

# Making a theme for SDH-CssLoader
## Prerequisites
- Some experience in json and css
- Installed the Css loader
- (Optional) Installed a chromium based browser

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
Themes are folders with css files and a single `theme.json` inside. The `theme.json` determines how everything will be displayed, and any dropdown options if the theme has them. The Css Loader loads themes from `/home/deck/homebrew/themes`

### Simple themes
![SimpleTheme](images/Readme/simpletheme.png)

For a simple theme, like the image above, the theme json should look something like this

```json
{
    "name": "Clean Gameview",
    "author": "SuchMeme",
    "target": "Library",
    "inject": {
        "shared.css": ["SP"]
    }
}
```

- The name element describes the theme name. This is also used as the folder name for the theme store.
- The author element describes the theme author.
- An optional field `"version": "v1.0"` can be added. If no version field is found, the version defaults to `v1.0`
- The inject tab is a dictionary of relative css file paths as keys, and a list of tabs you want the css to be injected into
- The target field describes what part of the UI your theme themes. This is only useful for submitting a theme. The following options are available: (Note: if you want an option to be added, open an issue on this repository)
    - System-Wide
    - Keyboard
    - Home
    - Library
    - Store
    - Friends and Chat
    - Media
    - Downloads
    - Settings
    - Lock Screen
    - Other


### Complex themes
![ComplexTheme](images/Readme/complextheme.png)

A complex theme is a simple theme with patches. Patches are displayed as dropdown menus that apply additional css depending on the selection. A complex theme's json should look something like this:

```json
{
    "name": "Colored Toggles",
    "version": "v1.2",
    "author": "SuchMeme",
    "target": "System-Wide",
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

Note: A pull request to this repository has a specific template to adhere to. Please make sure your theme adheres to the checklist below
- [ ] I am the original author of this theme.
- [ ] I am not bundling a part of another theme with my theme (or are making it optional with patches), to encourage mixing and matching themes
- [ ] I marked my theme target appropriately, and made sure my theme only themes the part it says it does
    - [ ] If this is a keyboard theme, this theme gets applied to the default keyboard
    - [ ] If this is a System-Wide theme, this theme does not bundle a keyboard theme (or are making it optional with patches)
- [ ] I have verified that my theme works properly on the latest versions of SteamOS, decky-loader and SDH-CssLoader.

### Steps to submit a theme

1. Fork this repository
2. Clone the forked repository to your pc using your favorite git tool
3. Create a preview image and place it in the images folder. Preferably make a subfolder with your username
    - Preferably upload an image in the .jpg format
4. Create a json called `{author}-{themename}.json` in the themes folder, with the following content: (See an example/template below)
    - `repo_url`: Required, points to another github repository with the theme
    - `repo_subpath`: Optional, defaults to '.', indicates the subpath to the folder containing the theme
    - `repo_commit`: Required, the commit in the git repo you want to release
    - `preview_image_path`: Required. This image is displayed in the browse themes UI of the plugin. The image needs to be located in this repository
5. (Optional) Test your theme submission using the python script, using `py main.py` in the repository folder.
    - Python and git cli needs to be installed
    - If you are missing python libraries, type `pip install -r requirements.txt`
    - If the script throws no exception, you're good
6. Make a commit with the image and .json files. Feel free to put multiple themes in 1 commit
7. Create a pull request back to this repository 

```json
{
    "repo_url": "https://github.com/suchmememanyskill/Steam-Deck-Themes",
    "repo_subpath": "Clean Gameview",
    "repo_commit": "d9f160",
    "preview_image_path": "images/SuchMeme/Clean Gameview.jpg"
}
```

If you need any help submitting a theme, [i have a discord server where you can ask for help](https://discord.gg/aH9rsuP)