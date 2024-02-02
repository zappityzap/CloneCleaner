# About this Fork
[CloneCleaner](https://github.com/artyfacialintelagent/CloneCleaner) is a great extension, but it hasn't been maintained since it was released. This is an opinionated fork, which means I change it to work the way I want. Have a look at the original repo for more details about how it works.

# Notable changes
* Disabled by default! Accordion closed by default!
* Compatible with Dynamic Prompts
* Allows using a fixed declone seed per batch
* Exclude hair styles by length
* Infotext pasting
* Debug logging

# Compatibility
* Hires Fix: reuses first pass prompt correctly, does not insert into hires prompt
* ADetailer: doesn't seem to make a difference, but works when clonecleanerz is added to the list of scripts to apply in ADetailer settings
* Dynamic Prompts: compatible, Dynamic Prompts runs first

# Version History / Change Log / Releases
* v1.0.6 - Supoort infotext pasting, revert broken prompt building code, new README
* v1.0.5 - Add exclude hairstyles, debug logging
* v1.0.4 - Add fixed batch seed option
* v1.0.3 - Add debug logging
* v1.0.2 - Replace JS UI code with Gradio event handlers, clean up and style fixes.
* v1.0.1 - Disable by default, close accordion by default.

# Contributing
1. Open an issue to discuss a change before working on the code.
1. PRs should be well-tested and documented.
