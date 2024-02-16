import gradio as gr
import os
import random
import sys
import yaml
import traceback

from modules import scripts, script_callbacks, shared, paths
from modules.processing import Processed
from modules.ui_components import FormRow, FormColumn, FormGroup, ToolButton
from modules.ui import random_symbol, reuse_symbol, gr_show
from modules.generation_parameters_copypaste import parse_generation_parameters

from scripts.clonecleanerz_logger import logger_clonecleanerz as logger
from lib_ccz.state import state, xyz_attrs, apply_xyz
from lib_ccz import xyz_grid

def read_yaml():
    prompt_database_path = shared.opts.data.get("ccz_prompt_database_path", "prompt_tree.yml")
    promptfile = os.path.join(scripts.basedir(), prompt_database_path)
    with open(promptfile, "r", encoding="utf8") as stream:
        prompt_tree = yaml.safe_load(stream)
        return prompt_tree

def get_last_params(declone_seed, gallery_index):
    filename = os.path.join(paths.data_path, "params.txt")
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf8") as file:
            prompt = file.read()

    if gallery_index > 0:
        gallery_index -= 1
    params = parse_generation_parameters(prompt)
    if params.get("CCZ_use_main_seed", "") == "True":
        return [int(float(params.get("Seed", "-0.0"))) + gallery_index, gr_show(False)]
    else:
        return [int(float(params.get("CCZ_declone_seed", "-0.0"))) + gallery_index, gr_show(False)]

def sorted_difference(a, b):
    newlist = list(set(a).difference(b))
    newlist.sort()
    return newlist

class CloneCleanerZScript(scripts.Script):
    log_level = shared.opts.data.get("ccz_log_level", "INFO")
    logger.setLevel(log_level)

    prompt_tree = read_yaml()

    def title(self):
        return "CloneCleanerZ"

    # show menu in either txt2img or img2img
    def show(self, is_img2img):
        return scripts.AlwaysVisible
    
    def ui(self, is_img2img):
        with gr.Accordion("CloneCleanerZ", open=False):
            dummy_component = gr.Label(visible=False)
            regions = self.prompt_tree["country"].keys()
            hairlength = self.prompt_tree["hair"]["length"].keys()
            haircolor = self.prompt_tree["hair"]["color"].keys()
            hairstyle = self.prompt_tree["hair"]["style"].keys()
            with FormRow():
                with FormColumn(min_width=160):
                    enable = gr.Checkbox(
                        label="Enable CloneCleanerZ",
                        value=False,
                        elem_id="CCZ_enable")
                    only_adetailer = gr.Checkbox(
                        label="Only ADetailer",
                        value=False,
                        elem_id="CCZ_only_adetailer")
                with FormColumn():
                    gender = gr.Radio(
                        label="Male & generic not yet implemented.",
                        interactive=False,
                        value="female",
                        choices=["female", "male", "generic"],
                        elem_id="CCZ_gender")
            with FormRow():
                use_components = ["name", "country", "hair length", "hair color", "hair style"]
                use_components = gr.CheckboxGroup(
                    label="Use declone components",
                    type="value",
                    value=use_components,
                    choices=use_components,
                    elem_id="CCZ_use_components")
            with FormRow():
                with FormGroup():
                    insert_start = gr.Checkbox(
                        label="Insert declone tokens at start of prompt",
                        value=True,
                        elem_id="CCZ_insert_start")
                    declone_weight = gr.Slider(
                        label="Weight of declone tokens",
                        minimum=0.0,
                        maximum=2.0,
                        step=0.05,
                        value=1.0,
                        elem_id="CCZ_declone_weight")
                with FormGroup():
                    use_main_seed = gr.Checkbox(
                        label="Use main image seed for decloning",
                        value=True,
                        elem_id="CCZ_use_main_seed")
                    with FormRow(variant="compact"):
                        declone_seed = gr.Number(
                            label="Declone seed",
                            visible=False,
                            value=-1,
                            elem_id="CCZ_declone_seed")
                        random_seed = ToolButton(
                            random_symbol,
                            visible=False,
                            label="Random seed",
                            elem_id="CCZ_random_seed")
                        reuse_seed = ToolButton(
                            reuse_symbol,
                            visible=False,
                            label="Reuse seed",
                            elem_id="CCZ_reuse_seed")
                    fixed_batch_seed = gr.Checkbox(
                        label="Use first seed for entire batch",
                        value=False,
                        elem_id="CCZ_fixed_batch_seed")
            with FormRow():
                exclude_regions = gr.Dropdown(
                    label="Exclude regions",
                    choices=regions,
                    multiselect=True,
                    elem_id="CCZ_exclude_regions")
                exclude_hairlength = gr.Dropdown(
                    label="Exclude hair lengths",
                    choices=hairlength,
                    multiselect=True,
                    elem_id="CCZ_exclude_hairlength")
                exclude_haircolor = gr.Dropdown(
                    label="Exclude hair colors",
                    choices=haircolor,
                    multiselect=True,
                    elem_id="CCZ_exclude_haircolor")
                exclude_hairstyle = gr.Dropdown(
                    label="Exclude hair styles",
                    choices=hairstyle,
                    multiselect=True,
                    elem_id="CCZ_exclude_hairstyle")

        # event handlers        
        def use_main_seed_change(use_main_seed):
            return [
                gr.update(visible=not use_main_seed),
                gr.update(visible=not use_main_seed),
                gr.update(visible=not use_main_seed)
            ]
        use_main_seed.change(
            fn=use_main_seed_change,
            inputs=use_main_seed,
            outputs=[declone_seed, random_seed, reuse_seed],
            show_progress=False
        )
        
        def random_seed_click():
            return gr.update(value=-1)
        random_seed.click(fn=random_seed_click, outputs=declone_seed, show_progress=False)

        # set up the recycle seed button
        # TODO find a way to avoid using js here
        jsgetgalleryindex = "(x, y) => [x, selected_gallery_index()]"
        reuse_seed.click(
            fn=get_last_params,
            _js=jsgetgalleryindex,
            show_progress=False,
            inputs=[declone_seed, dummy_component],
            outputs=[declone_seed, dummy_component])

        def use_components_change(use_components):
            exclude_regions = "country" in use_components
            exclude_hairlength = "hair length" in use_components
            exclude_haircolor = "hair color" in use_components
            exclude_hairstyle = "hair style" in use_components
            return [
                gr.update(visible=exclude_regions),
                gr.update(visible=exclude_hairlength),
                gr.update(visible=exclude_haircolor),
                gr.update(visible=exclude_hairstyle),
            ]
        use_components.change(
            fn=use_components_change,
            inputs=use_components,
            outputs=[exclude_regions, exclude_hairlength, exclude_haircolor, exclude_hairstyle],
            show_progress=False)

        # infotext
        def list_from_params_key(key, params):
            regionstring = params.get(key, "")
            regions = regionstring.split(",") if regionstring else []
            return gr.update(value = regions)

        self.infotext_fields = [
            (enable, "CCZ_enable"),
            (gender, "CCZ_gender"),
            (insert_start, "CCZ_insert_start"),
            (declone_weight, "CCZ_declone_weight"),
            (use_main_seed, "CCZ_use_main_seed"),
            (declone_seed, "CCZ_declone_seed"),
            (use_components, lambda params:list_from_params_key("CCZ_use_components", params)),
            (exclude_regions, lambda params:list_from_params_key("CCZ_exclude_regions", params)),
            (exclude_hairlength, lambda params:list_from_params_key("CCZ_exclude_hairlength", params)),
            (exclude_haircolor, lambda params:list_from_params_key("CCZ_exclude_haircolor", params)),
            (exclude_hairstyle, lambda params:list_from_params_key("CCZ_exclude_hairstyle", params))
        ]
        return [
            enable,
            only_adetailer,
            gender,
            insert_start,
            declone_weight,
            use_main_seed,
            fixed_batch_seed,
            declone_seed,
            use_components,
            exclude_regions,
            exclude_hairlength,
            exclude_haircolor,
            exclude_hairstyle
        ]

    def process(
        self,
        p,
        enable,
        only_adetailer,
        gender,
        insert_start,
        declone_weight,
        use_main_seed,
        fixed_batch_seed,
        declone_seed,
        use_components,
        exclude_regions,
        exclude_hairlength,
        exclude_haircolor,
        exclude_hairstyle):
        logger.debug(f"process(): entered")

        state.enable = enable
        state.only_adetailer = only_adetailer
        state.gender = gender
        state.insert_start = insert_start
        state.declone_weight = declone_weight
        state.use_main_seed = use_main_seed
        state.fixed_batch_seed = fixed_batch_seed
        state.declone_seed = declone_seed
        state.use_components = use_components
        state.exclude_regions = exclude_regions
        state.exclude_hairlength = exclude_hairlength
        state.exclude_haircolor = exclude_haircolor
        state.exclude_hairstyle = exclude_hairstyle

        # apply XYZ settings
        apply_xyz()
        xyz_attrs.clear()

        if not state.enable:
            logger.debug(f"process(): not enabled, returning")
            return

        stack = traceback.extract_stack()
        from_adetailer = any("adetailer" in frame.filename for frame in stack)
        
        if not from_adetailer and state.only_adetailer:
            logger.debug(f"from_adetailer={from_adetailer} and only_adetailer={state.only_adetailer}, returning")
            return
        
        logger.debug(f"setting declone seed")
        if state.use_main_seed:
            logger.debug(f"use_main_seed is true, using p.all_seeds[0]={p.all_seeds[0]}")
            state.declone_seed = p.all_seeds[0]
        elif state.declone_seed == -1:
            logger.debug(f"use_main_seed false and declone seed is -1, choosing random seed")
            state.declone_seed = int(random.randrange(4294967294))
        else:
            logger.debug(f"use_main_seed false and declone seed is not -1, using specified seed={state.declone_seed}")
            state.declone_seed = int(state.declone_seed)
        logger.debug(f"declone_seed={state.declone_seed}")

        # add params to batch
        p.extra_generation_params["CCZ_enable"] = state.enable
        p.extra_generation_params["CCZ_gender"] = state.gender
        p.extra_generation_params["CCZ_insert_start"] = state.insert_start
        p.extra_generation_params["CCZ_declone_weight"] = state.declone_weight
        p.extra_generation_params["CCZ_use_main_seed"] = state.use_main_seed
        p.extra_generation_params["CCZ_declone_seed"] = state.declone_seed

        # p.extra_generation_params["CCZ_use_components"] = ",".join(state.use_components)
        p.extra_generation_params["CCZ_use_components"] = (
            state.use_components[0]
            if len(state.use_components) == 1
            else ",".join(state.use_components)
        )

        if state.exclude_regions:
            p.extra_generation_params["CCZ_exclude_regions"] = ",".join(state.exclude_regions)
        if state.exclude_hairlength:
            p.extra_generation_params["CCZ_exclude_hairlength"] = ",".join(state.exclude_hairlength)
        if state.exclude_haircolor:
            p.extra_generation_params["CCZ_exclude_haircolor"] = ",".join(state.exclude_haircolor)
        if state.exclude_hairstyle:
            p.extra_generation_params["CCZ_exclude_hairstyle"] = ",".join(state.exclude_hairstyle)
            
        countrytree = self.prompt_tree["country"]
        hairtree = self.prompt_tree["hair"]

        regions = sorted_difference(countrytree.keys(), state.exclude_regions)
        hairlengths = sorted_difference(hairtree["length"].keys(), state.exclude_hairlength)
        haircolors = sorted_difference(hairtree["color"].keys(), state.exclude_haircolor)
        hairstyles = sorted_difference(hairtree["style"].keys(), state.exclude_hairstyle)

        use_name = "name" in state.use_components
        use_country = "country" in state.use_components
        use_length = "hair length" in state.use_components
        use_style = "hair style" in state.use_components
        use_color = "hair color" in state.use_components

        logger.debug(f"iterating through prompts for batch")
        for i, prompt in enumerate(p.all_prompts):
            # set declone seed and initialize rng
            rng = random.Random()
            logger.debug(f"fixed_batch_seed={state.fixed_batch_seed}")
            seed = state.declone_seed
            if not state.fixed_batch_seed:
                logger.debug("not using fixed_batch_seed, incrementing image declone_seed")
                seed = p.all_seeds[i] if state.use_main_seed else state.declone_seed + i
            logger.debug(f"prompt #{i} main seed={p.all_seeds[i]}, declone_seed={state.declone_seed}, image declone_seed={seed}")
            rng.seed(seed)

            # select region
            region = rng.choice(regions)
            logger.debug(f"selected region={region} from {regions}")

            # select countries from regions
            countries = list(countrytree[region].keys())

            # select country from countries
            countryweights = [countrytree[region][cty]["weight"] for cty in countries]
            country = rng.choices(countries, weights=countryweights)[0]
            logger.debug(f"selected country={country} from {countries}")

            # countrydata is country weight, optional hair color weights, and names
            countrydata = countrytree[region][country]

            # load hairdata
            if use_color or use_length or use_style:
                hairdata = countrydata.get("hair", hairtree["defaultweight"][region])
            
            # select hair color
            if use_color:
                maincolor = rng.choices(haircolors, weights=[hairdata[col] for col in haircolors])[0]
                logger.debug(f"selected maincolor={maincolor} from {haircolors}")
                maincolor_colors = hairtree["color"][maincolor]
                color = rng.choice(maincolor_colors)
                logger.debug(f"selected color={color} from {maincolor_colors}")
            
            # select hair length
            if use_length:
                mainlength = rng.choice(hairlengths)
                logger.debug(f"selected mainlength={mainlength} from {hairlengths}")
                mainlength_lengths = hairtree["length"][mainlength]
                length = rng.choice(mainlength_lengths)
                logger.debug(f"selected length={length} from {mainlength_lengths}")
            
            # select hair style
            if use_style:
                mainstyle = rng.choice(hairstyles)
                logger.debug(f"selected mainstyle={mainstyle} from {hairstyles}")
                mainstyle_styles = hairtree["style"][mainstyle]
                style = rng.choice(mainstyle_styles)
                logger.debug(f"selected style={style} from {mainstyle_styles}")

            # select name
            if use_name:
                names = countrydata["names"]
                name = rng.choice(names)
                logger.debug(f"selected name={name} from {names}")

            # build prompt
            inserted_prompt = ""

            if use_name or use_country:
                inserted_prompt += name if use_name else "person"
                inserted_prompt += " from " + country if use_country else ""
            
            if use_length or use_style or use_color:
                if inserted_prompt:
                    inserted_prompt += ", "
                if use_length:
                    inserted_prompt += length + " "
                if use_style:
                    inserted_prompt += style + " "
                if use_color:
                    inserted_prompt += color + " "
                inserted_prompt += "hair"

            if state.declone_weight != 1:
                inserted_prompt = f"({inserted_prompt}:{state.declone_weight})"

            if state.insert_start:
                p.all_prompts[i] = inserted_prompt + ", " + prompt
            else:
                p.all_prompts[i] = prompt + ", " + inserted_prompt

            # insert prompt
            logger.info(f"{inserted_prompt}")
            p.all_prompts[i] = f"{inserted_prompt}, {prompt}" if state.insert_start else f"{prompt}, {inserted_prompt}"
            logger.debug(f"prompt #{i} {p.all_prompts[i]}")

    def postprocess(self, p, processed, *args):
        # TODO this doesn't seem right, the extension shouldn't be writing params.txt
        with open(os.path.join(paths.data_path, "params.txt"), "w", encoding="utf8") as file:
            p.all_prompts[0] = p.prompt
            processed = Processed(p, [], p.seed, "")
            file.write(processed.infotext(p, 0))

def on_ui_settings():
    section = ("clonecleanerz", "CloneCleanerZ")
    shared.opts.add_option(
        key="ccz_prompt_database_path",
        info = shared.OptionInfo(
            default="prompt_tree.yml",
            label="CloneCleanerZ prompt database path",
            section=section
        )
        .info("prompt_tree.yml will be overwritten by updates. To customize, make a copy and update path here. Restart required.")
    )

    shared.opts.add_option(
        key="ccz_log_level",
        info=shared.OptionInfo(
            default="INFO",
            label="Log level",
            component=gr.Dropdown,
            component_args={"choices": ["INFO", "DEBUG", "WARNING", "ERROR", "CRITICAL"]},
            section=section,
        )
        # .link("?", "https://somewhere/something#here")
        .info("Amount of detail in console logging. Restart required.")
    )

xyz_grid.patch()

script_callbacks.on_ui_settings(on_ui_settings)
