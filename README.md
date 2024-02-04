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

## Extension Compatibility
* ADetailer: Yes, see below for details.
* Dynamic Prompts: Yes, Dynamic Prompts runs first.
* XYZ Plot: Works with XYZ plots, but doesn't expose parameters for plotting. PRs welcome.
* Hires Fix: Yes? Reuses first pass prompt correctly, does not insert into hires prompt.

## Version History
* [v1.0.7] - ADetailer support, improved debug logging, README update
* [v1.0.6] - Support infotext pasting, revert broken prompt building code, new README
* [v1.0.5] - Add exclude hairstyles, debug logging
* [v1.0.4] - Add fixed batch seed option
* [v1.0.3] - Add debug logging
* [v1.0.2] - Replace JS UI code with Gradio event handlers, clean up and style fixes
* [v1.0.1] - Disable by default, close accordion by default

## Seeds
CloneCleanerZ uses a declone seed to randomly generate a prompt. By default CloneCleanerZ uses the main image seed as the declone seed. Any generated prompt will be reproduced with the same seed and prompt tree.

The **declone seed** can be chosen separately from the main image seed. Setting a fixed declone seed behaves the same as A1111. 

**Using the first seed for entire batch** will generate the same inserted prompt for each member of the batch. This reproduces the behavior of the original CloneCleaner when Dynamic Prompts was also enabled.

## ADetailer
It can be helpful to save mask previews when adjusting mask settings, and to save images before ADetailer when adjusting any other settings. **Save mask previews** and **Save images before ADetailer** can be applied at any time without restarting the UI or A1111.

Mask settings may need to be adjusted to include hair.

## Declong Multiple Subjects
Add CloneCleanerZ to the list of scripts run by ADetailer and override the main prompt in ADetailer. CloneCleanerZ will modify the main prompt, and run again to modify each ADetailer prompt. Enable debug logging and watch the console to see what is happening.

I'm not an expert on ADetailer or ControlNet. These settings worked for me with Photon. Use a high denoise with ControlNet Tile and a medium weight so it has enough room to change the face.

* Override the positive prompt with something. Copying the main prompt seems to work, or use something generic.
* Inpainting
    * Inpaint denoise strength: 0.9
* ControlNet
    * Model: control_v11f1e_sd15_tile
    * Weight: 0.5

# Contributing
1. Open an issue to discuss a change before working on the code.
1. PRs should be well-tested and documented.
