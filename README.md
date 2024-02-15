# CloneCleanerZ
**CloneCleanerZ**, a fork of [CloneCleaner](https://github.com/artyfacialintelagent/CloneCleaner). Have a look at the original repo for more details about how it works.

The repo name name is `zccz` so that this extension runs *after* Dynamic Prompts.

The Prompt Tree is unchanged from the original repo. Make a copy and customize it to your needs.

If there's anything about this extension that doesn't work the way you think it should: open an issue with details and examples.

## Notable changes
* Disabled by default! Accordion closed by default!
* ADetailer support
* Compatible with Dynamic Prompts
* Allows using a fixed declone seed per batch
* Exclude hair styles by length
* Infotext pasting
* Debug logging

## Compatibility
* Automatic1111: Yes, v1.7.0+
* Automatic1111 forks: unknown
* ComfyUI: No, maybe later?

## Feature Compatibility
* Infotext: Yes
* Hires Fix: Yes? Reuses first pass prompt correctly, does not insert into hires prompt.
* XYZ Plot: Works with XYZ plots, and supports plotting all parameters except declone components and exclude lists.

## Extension Compatibility
* [ADetailer](https://github.com/Bing-su/adetailer): Yes, see below for details.
* [Dynamic Prompts](https://github.com/adieyal/sd-dynamic-prompts): Yes, Dynamic Prompts runs first.
* [One Button Prompt](https://github.com/AIrjen/OneButtonPrompt): Yes
* [AnimateDiff](https://github.com/continue-revolution/sd-webui-animatediff): Yes

## Version History
* [v1.0.9](https://github.com/zappityzap/zccz/releases/tag/v1.0.8) - XYZ Plot support
* [v1.0.8](https://github.com/zappityzap/zccz/releases/tag/v1.0.8) - ADetailer-only mode
* [v1.0.7](https://github.com/zappityzap/zccz/releases/tag/v1.0.7) - ADetailer support, improved debug logging, README update
* [v1.0.6](https://github.com/zappityzap/zccz/releases/tag/v1.0.6) - Support infotext pasting, revert broken prompt building code, new README
* [v1.0.5](https://github.com/zappityzap/zccz/releases/tag/v1.0.5) - Add exclude hairstyles, debug logging
* [v1.0.4](https://github.com/zappityzap/zccz/releases/tag/v1.0.4) - Add fixed batch seed option
* [v1.0.3](https://github.com/zappityzap/zccz/releases/tag/v1.0.3) - Add debug logging
* [v1.0.2](https://github.com/zappityzap/zccz/releases/tag/v1.0.2) - Replace JS UI code with Gradio event handlers, clean up and style fixes
* [v1.0.1](https://github.com/zappityzap/zccz/releases/tag/v1.0.1) - Disable by default, close accordion by default

## Settings
* **Enable CloneCleanerZ** - Note: "clonecleanerz" must be added to ADetailer scripts to modify ADetailer prompts.
* **Only ADetailer** - Only modify the ADetailer prompts, does not change main prompt.
* **Use declone components** - Select what should be inserted. If **name** is not selected then the prompt will use "person" instead.
* **Put declone settings at beginning of prompt** - Insert in front of the prompt. Inserts at the end when unchecked.
* **Weight of declone tokens** - Wraps inserted prompt with attention weight like (prompt:0.7).
* **Use main image seed for decloning** - Use the same seed as the main prompt to generate the inserted prompt.
* **Use first seed for entire batch** - Generate the same inserted prompt for each member of the batch.
* **Exclude region/hair/etc** - Exclude the selected categories from the generated prompt.

## ADetailer
CCZ can modify the main prompt, or all of the ADetailer prompts, or both. To modify ADetailer prompts: add "clonecleanerz" to the list of scripts run by ADetailer. To modify only the ADetailer prompt: check **Only ADetailer** in CCZ.

Note that using a blank ADetailer prompt will result in double prompt insertion unless **Only ADetailer** is checked.

It can be helpful to save mask previews when adjusting mask settings, and to save images before ADetailer when adjusting any other settings. **Save mask previews** and **Save images before ADetailer** can be applied at any time without restarting the UI or A1111.

Mask settings may need to be adjusted to include hair.

## Declong Multiple Subjects
Add CloneCleanerZ to the list of scripts run by ADetailer and override the main prompt in ADetailer. CloneCleanerZ will modify the main prompt, and run again to modify each ADetailer prompt. Enable debug logging and watch the console to see what is happening.

I'm not an expert on ADetailer or ControlNet. These settings worked for me with Photon. Use a high denoise with ControlNet Tile and a medium weight so it has enough room to change the face.

* Override the main prompt
* Inpainting denoise strength: 0.9
* ControlNet
    * Model: control_v11f1e_sd15_tile
    * Weight: 0.5

# Contributing
1. Open an issue to discuss a change before working on the code.
1. PRs should be well-tested and documented.
