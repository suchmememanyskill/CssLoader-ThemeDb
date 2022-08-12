# CSS Loader - Theme Database
A repo containing themes for [SDH-CssLoader](https://github.com/suchmememanyskill/SDH-CssLoader), a CSS loader for the Steam Deck.

* [Making a theme for SDH-CssLoader](#making-a-theme-for-sdh-cssloader)
    * [Prerequisites](#prerequisites)
    * [Setting up the CEF debugger (Optional)](#setting-up-the-cef-debugger-optional)
        * [Setup](#setup)
    * [Making a theme compatible with the CSS loader](#making-a-theme-compatible-with-the-css-loader)
        * [Simple themes](#simple-themes)
        * [Complex themes](#complex-themes)
* [Submitting a theme to the theme store](#submitting-a-theme-to-the-theme-store)
* [Support](#support)
    * [Upgrading a theme](#upgrading-a-theme)

# Making a theme for SDH-CssLoader
## Prerequisites
- Some experience in JSON and CSS
- Installed the CSS loader
- (Optional) Installed a Chromium-based browser

## Setting up the CEF debugger (Optional)
![Debugger](images/Readme/Debugger.png)

The CEF debugger is very useful for creating themes, as it allows you to play around directly with the style of the Steam Deck UI.

The debugger allows you to access the multiple tabs that are used for the UI. A few common ones are:
- `SP` - The main UI of the Steam Deck
- `QuickAccess` - The Quick Access overlay
- `MainMenu` - The Steam menu overlay

### Setup
1. Open a Chromium-based browser (ex. Google Chrome, Microsoft Edge, Brave)
2. Connect to `{DECK_IP}:8081` in the browser
    - You need to be on the same network as your Steam Deck
    - You can find the IP of your Steam Deck by going into your internet settings, selecting the current connected network, and looking at the `IP Address` field
3. Select a tab
    - After selecting a tab, you should be able to see the HTML and CSS used for that specific tab, like the screenshot above

## Making a theme compatible with the CSS loader
Themes are folders with CSS files and a single `theme.json` inside. The `theme.json` determines how everything will be displayed, and any dropdown options if the theme has them. The CSS loader loads themes from `/home/deck/homebrew/themes`.

### Simple themes
![SimpleTheme](images/Readme/simpletheme.png)

For a simple theme, like the image above, `theme.json` should look something like this:

```json
{
    "name": "Clean Gameview",
    "author": "SuchMeme",
    "target": "Library",
    "manifest_version": 2,
    "inject": {
        "shared.css": ["SP"]
    }
}
```

- The name element describes the theme name. This is also used as the folder name for the theme store.
- The author element describes the theme author.
- An optional field `"version": "v1.0"` can be added. If no version field is found, the version defaults to `v1.0`.
- The manifest version tells the CSS Loader which version of `themes.json` you are using. The current version is `2`.
- The inject tab is a dictionary of relative CSS file paths as keys, and a list of tabs you want the CSS to be injected into.
- The target field describes what part of the UI your theme themes. This is only useful for submitting a theme. The following options are available, but more can be added through creating an issue:
    - System-Wide
    - Background
    - Keyboard
    - Home
    - Background
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

A complex theme is a theme with patches. Patches are displayed as dropdown menus that apply additional CSS depending on the selection. The `theme.json` for a complex theme should look something like this:

```json
{
    "name": "Colored Toggles",
    "version": "v1.2",
    "author": "SuchMeme",
    "target": "System-Wide",
    "manifest_version": 2,
    "inject": {
        "shared.css": [
            "QuickAccess", "SP", "MainMenu"
        ] 
    },
    "patches": {
        "Theme Color": {
            "default": "Orange",
            "type": "dropdown",
            "values": {
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
}
```

> The patches section is a dictionary of patch names as key. The value is a dictionary where keys are it's options and their value is the applied CSS, similar to the "inject" section. The special key "default" is required to indicate a default option.

Patches allow for choosing between a dropdown, a checkbox (toggle), or a slider for patch selection using the `type` field.

#### Dropdown
`"type": "dropdown"`

This is the default value. This type gives a dropdown of all keys in the `values` dictionary. Choosing an option injects only the CSS specified within the selected value.

![dropdown](images/Readme/dropdown.jpg)

#### Slider
`"type": "slider"`

This type gives a slider with the labels of the points of all keys in the `values` dictionary. Choosing an option injects only the CSS specified within the selected value.

![dropdown](images/Readme/slider.jpg)

#### Checkbox (Toggle)
`"type": "checkbox"`

This type represents the `values` field as a toggle. This type is unique in the sense that it limits what options you can put in the `values` dictionary. You need to have a `Yes` and a `No` option in the `values` dictionary, otherwise the type falls back to a dropdown. When the toggle is on, `Yes` is selected, otherwise `No` is selected.

![dropdown](images/Readme/checkbox.jpg)


# Submitting a theme to the theme store

A pull request to this repository has a specific template to adhere to. Please make sure your theme adheres to [these requirements](https://github.com/EMERALD0874/CssLoader-ThemeDb/blob/main/.github/pull_request_template.md).

1. Fork this repository
2. Clone the forked repository to your PC using your favorite Git tool
3. Create a preview image and place it in the `images/{AUTHOR}` folder
    - Preferably upload an image in the .jpg format
4. Create a JSON file named `{AUTHOR}-{THEME_NAME}.json` in the themes folder with the following content:
    - `repo_url`: Required, points to another GitHub repository with the theme
    - `repo_subpath`: Optional, defaults to '.', indicates the subpath to the folder containing the theme
    - `repo_commit`: Required, the commit in the Git repo you want to release
    - `preview_image_path`: Required. This image is displayed in the browse themes UI of the plugin and must be located in this repository
5. (Optional) Test your theme submission using `py main.py` in the repository folder
    - Python and Git CLI need to be installed
    - If you are missing Python libraries, type `pip install -r requirements.txt`
    - If the script throws no exception, you are ready to commit
6. Make a commit with the image and JSON files
7. (Optional) Repeat steps 3 through 6 for any additional themes you would like to add to your pull request
8. Create a pull request from your fork to this repository

Here is an example `{AUTHOR}-{THEME_NAME}.json` file:
```json
{
    "repo_url": "https://github.com/suchmememanyskill/Steam-Deck-Themes",
    "repo_subpath": "Clean Gameview",
    "repo_commit": "d9f160",
    "preview_image_path": "images/SuchMeme/Clean Gameview.jpg"
}
```

# Support
If you need any help creating or submitting a theme, [there's the Decky loader discord server.](https://discord.gg/ZU74G2NJzk). In the server, see the `Css-Loader Support` thread in the `support-plugins` channel

## Upgrading a theme
If you created a theme and would like to upgrade it to the latest manifest version, please follow this guide.

### Upgrading from version 1
To upgrade a version 1 `themes.json`, all options of a patch need to be put in a `values` dictionary, and a `manifest_version` field should be added to the root of the .json with value `2`. Please see [Making a theme compatible with the CSS loader](#making-a-theme-compatible-with-the-css-loader) for an example.
