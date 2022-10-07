# CSS Loader - Theme Database
A repo containing themes for [SDH-CssLoader](https://github.com/suchmememanyskill/SDH-CssLoader), a CSS loader for the Steam Deck.

* [Making a theme for SDH-CssLoader](#making-a-theme-for-sdh-cssloader)
    * [Prerequisites](#prerequisites)
    * [Setting up the CEF debugger (Optional)](#setting-up-the-cef-debugger-optional)
        * [Recommended setup](#recommended-setup)
        * [Legacy setup](#legacy-setup)
    * [Making a theme compatible with the CSS loader](#making-a-theme-compatible-with-the-css-loader)
        * [Simple themes](#simple-themes)
        * [Complex themes](#complex-themes)
* [Additional features](#additional-features)
    * [Theme Dependencies](#theme-dependencies)
    * [Components](#components)
        * [Color Picker](#color-picker)
    * [Local Images](#local-images)
* [Submitting a theme to the theme store](#submitting-a-theme-to-the-theme-store)
    * [File management](#file-management)
* [Support](#support)
    * [Upgrading a theme](#upgrading-a-theme)
        * [Upgrading from version 2 to version 3](#upgrading-from-version-2-to-version-3)
        * [Upgrading from version 1 to version 2 or 3](#upgrading-from-version-1-to-version-2-or-3)

# Making a theme for SDH-CssLoader
## Prerequisites
- Some experience in JSON and CSS
- Installed the CSS loader
- (Optional) Installed a Chromium-based browser

## Templates
[There is a sample/template repository available](https://github.com/suchmememanyskill/Steam-Deck-Theme-Template). Feel free to use this to more easily create a theme by using the template.

## Setting up the CEF debugger (Optional)
![Debugger](images/Readme/Debugger.png)

The CEF debugger is very useful for creating themes, as it allows you to play around directly with the style of the Steam Deck UI.

The debugger allows you to access the multiple tabs that are used for the UI. A few common ones are:
- `SP` - The main UI of the Steam Deck
- `QuickAccess` - The Quick Access overlay
- `MainMenu` - The Steam menu overlay

### Recommended setup
1. Turn on the "Allow Remote CEF Debugging" setting in the Decky settings.
1. Open a Chromium-based browser (ex. Google Chrome, Microsoft Edge, Brave)
1. Go to the inspect page of your browser (ex. chrome://inspect, edge://inspect, brave://inspect)
1. Under "Discover network targets", click "Configure", and enter "{DECK_IP}:8081"
    - You can find the IP of your Steam Deck by going into your internet settings, selecting the current connected network, and looking at the `IP Address` field
1. Wait a few seconds, and you will see multiple tabs appear under "Remote Target"
    - After selecting a tab, you should be able to see the HTML and CSS used for that specific tab, like the screenshot above

### Legacy setup
1. Turn on the "Allow Remote CEF Debugging" setting in the Decky settings.
1. Open a Chromium-based browser (ex. Google Chrome, Microsoft Edge, Brave)
1. Connect to {DECK_IP}:8081 in the browser
    - You need to be on the same network as your Steam Deck
    - You can find the IP of your Steam Deck by going into your internet settings, selecting the current connected network, and looking at the `IP Address` field
1. Select a tab
    - After selecting a tab, you should be able to see the HTML and CSS used for that specific tab, like the screenshot above

## Making a theme compatible with the CSS loader
Themes are folders with CSS files and a single `theme.json` inside. The `theme.json` determines how everything will be displayed, and any dropdown options if the theme has them. The CSS loader loads themes from `/home/deck/homebrew/themes`.

### Simple themes
![SimpleTheme](images/Readme/simpletheme.png)

[Example](https://github.com/suchmememanyskill/Steam-Deck-Theme-Template/tree/main/Sample%20Simple%20Theme)

For a simple theme, like the image above, `theme.json` should look something like this:

```json
{
    "name": "Clean Gameview",
    "author": "SuchMeme",
    "target": "Library",
    "manifest_version": 3,
    "description": "this is an example description",
    "inject": {
        "shared.css": ["SP"]
    }
}
```

- The name element describes the theme name. This is also used as the folder name for the theme store.
- The author element describes the theme author.
- An optional field `"version": "v1.0"` can be added. If no version field is found, the version defaults to `v1.0`.
- The manifest version tells the CSS Loader which version of `themes.json` you are using. The current version is `3`.
- An optional field `"description": ""` can be added to show a text description in the theme store.
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
    - Tweak
    - Other


### Complex themes
![ComplexTheme](images/Readme/complextheme.png)

[Example](https://github.com/suchmememanyskill/Steam-Deck-Theme-Template/tree/main/Sample%20Advanced%20Theme)

A complex theme is a theme with patches. Patches are displayed as dropdown menus that apply additional CSS depending on the selection. The `theme.json` for a complex theme should look something like this:

```json
{
    "name": "Colored Toggles",
    "version": "v1.2",
    "author": "SuchMeme",
    "target": "System-Wide",
    "description": "this is an example description",
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

![slider](images/Readme/slider.jpg)

#### Checkbox (Toggle)
`"type": "checkbox"`

This type represents the `values` field as a toggle. This type is unique in the sense that it limits what options you can put in the `values` dictionary. You need to have a `Yes` and a `No` option in the `values` dictionary, otherwise the type falls back to a dropdown. When the toggle is on, `Yes` is selected, otherwise `No` is selected.

![checkbox](images/Readme/checkbox.jpg)

#### None
`"type": "none"`

Displays only a little arrow with the patch name. For use with components

# Additional features
## Theme dependencies

[Example](https://github.com/suchmememanyskill/Steam-Deck-Theme-Template/tree/main/Sample%20Dependency%20Theme)

Since CSSLoader v1.2.0, a small dependency system has been added. This is useful for if you want to bundle another theme or want to make small modifications to an existing theme. All dependencies get enabled alongside your theme.

In the themes.json file, specify a field called `"dependencies"`. This is a dictionary of which the keys are the name of the theme you want to be dependencies, with their values being another dictionary. This dictionary's keys are the name of any patch this theme has, and the value the name of a value in the patch. If you don't want to modify any patch value, write `{}` as value

```json
"dependencies": {
    "Switch Like Home": {
        "No Friends": "Yes"
    },
    "Clean Gameview": {}
}
```
> If a theme has a dependencies field like the one above, it will enable both Switch Like Home and Clean Gameview. Switch Like Home's 'No Friends' patch gets forced to 'Yes'

## Components

Components are a way to attach extra parts to a selectable patch option. For now, this only includes a color picker.

Components are part of a patch. Inside a patch, you can make a `"components"` field (it's value is a list), and put the components inside

### Color Picker

![colorpicker](images/Readme/color-picker.jpg)

[Example](https://github.com/suchmememanyskill/Steam-Deck-Theme-Template/tree/main/Sample%20Color%20Picker%20Theme)

The color picker component injects a css variable with a user specified color.

```json
"components": [
    {
        "name": "Background Picker",
        "type": "color-picker",
        "on": "_",
        "default": "#000",
        "css_variable": "test-main-color",
        "tabs": ["QuickAccess"]
    }
]
```
- `name` refers to the of the component. This is shown to the user
- `type` refers to the type of component. For the color picker it's `color-picker`
- `on` refers to what value the component should be displayed on
- `default` refers to what default color the color picker should start out with. Only hex is supported, in 3,4,6 and 8 character variants
- `css_variable` refers to the name of the css variable that will be injected
- `tabs` refers to what tabs the css variable will be injected into

## Local Images

[Example](https://github.com/suchmememanyskill/Steam-Deck-Theme-Template/tree/main/Sample%20Background%20Theme)

Since CSSLoader v1.2.0, you can now access images locally from css. You can access images by using the following url: `/themes_custom/{your_theme_name}/{image_path}`

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

## File management
Sometimes, you want to ignore specific files or remove specific files before they get analyzed by the CI of the theme db. This is for example needed if you want to include images in your theme. You can create a file called 'release.json' in the same folder as your 'theme.json' of your theme. Inside, the file should be structured as follows

```json
{
    "include": [],
    "ignore": ["README.MD", "README.md", "Readme.md", "readme.md"]
}
```

Any paths in the include field will be included in the theme. Any paths in the ignore field will be ignored.

# Support
If you need any help creating or submitting a theme, please use [the Steam Deck Homebrew Discord server](https://discord.gg/ZU74G2NJzk). Please use the CSS-Loader Support thread in the #support-plugins channel.

## Upgrading a theme
If you created a theme and would like to upgrade it to the latest manifest version, please follow this guide. The current highest manifest version is 3.

### Upgrading from version 2 to version 3
No breaking changes have been made. Just change `manifest_version` from a `2` to a `3` to update a theme to manifest level 3

### Upgrading from version 1 to version 2 or 3
To upgrade a version 1 `themes.json`, all options of a patch need to be put in a `values` dictionary, and a `manifest_version` field should be added to the root of the .json with value `2` (or `3`). Please see [Making a theme compatible with the CSS loader](#making-a-theme-compatible-with-the-css-loader) for an example.
