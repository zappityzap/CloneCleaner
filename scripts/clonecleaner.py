import gradio as gr
import os
import random
import sys
import yaml

from modules import scripts, script_callbacks, shared, paths
from modules.processing import Processed
from modules.ui_components import FormRow, FormColumn, FormGroup, ToolButton
from modules.ui import random_symbol, reuse_symbol, gr_show
from modules.generation_parameters_copypaste import parse_generation_parameters

from scripts.clonecleanerz_logger import logger_clonecleanerz as logger


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
                    is_enabled = gr.Checkbox(value=False, label="Enable CloneCleanerZ")
                with FormColumn(elem_id="CCZ_gender"):
                    gender = gr.Radio(
                        ["female", "male", "generic"],
                        value="female",
                        interactive=False,
                        label="Male & generic not yet implemented.")
            with FormRow(elem_id="CCZ_components"):
                components = ["name", "country", "hair length", "hair color", "hair style"]
                use_components = gr.CheckboxGroup(
                    choices=components,
                    label="Use declone components",
                    type="value",
                    value=components,
                    elem_id="CCZ_use_components")

            with FormRow(elem_id="CCZ_midsection"):
                with FormGroup():
                    insert_start = gr.Checkbox(value=True, label="Put declone tokens at beginning of prompt")
                    declone_weight = gr.Slider(
                        minimum=0.0,
                        maximum=2.0,
                        step=0.05,
                        value=1.0,
                        label="Weight of declone tokens",
                        elem_id="CCZ_slider")
                with FormGroup():
                    use_main_seed = gr.Checkbox(value=True, label="Use main image seed for decloning")
                    with FormRow(variant="compact", elem_id="CCZ_seed_row"):
                        declone_seed = gr.Number(
                            visible=False,
                            label='Declone seed',
                            value=-1,
                            elem_id="CCZ_seed")
                        random_seed = ToolButton(
                            random_symbol,
                            visible=False,
                            elem_id="CCZ_random_seed",
                            label='Random seed')
                        reuse_seed = ToolButton(
                            reuse_symbol,
                            visible=False,
                            elem_id="CCZ_reuse_seed",
                            label='Reuse seed')
                    fixed_batch_seed = gr.Checkbox(
                        value=False,
                        elem_id="CCZ_fixed_batch_seed",
                        label="Use first seed for entire batch")
            with FormRow(elem_id="CCZ_exclude_row") as exclude_row:
                exclude_regions = gr.Dropdown(choices=regions, label="Exclude regions", multiselect=True)
                exclude_hairlength = gr.Dropdown(choices=hairlength, label="Exclude hair lengths", multiselect=True)
                exclude_haircolor = gr.Dropdown(choices=haircolor, label="Exclude hair colors", multiselect=True)
                exclude_hairstyle = gr.Dropdown(choices=hairstyle, label="Exclude hair styles", multiselect=True)

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
            (is_enabled, "CloneCleanerZ enabled"),
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
            is_enabled,
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
        is_enabled,
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
        if not is_enabled:
            logger.debug(f"process(): not enabled, returning")
            return

        logger.debug(f"setting declone seed")
        if use_main_seed:
            logger.debug(f"use_main_seed is true, using p.all_seeds[0]={p.all_seeds[0]}")
            declone_seed = p.all_seeds[0]
        elif declone_seed == -1:
            logger.debug(f"use_main_seed false and declone seed is -1, choosing random seed")
            declone_seed = int(random.randrange(4294967294))
        else:
            logger.debug(f"use_main_seed false and declone seed is not -1, using specified seed={declone_seed}")
            declone_seed = int(declone_seed)
        logger.debug(f"declone_seed={declone_seed}")

        # add params to batch
        p.extra_generation_params["CloneCleanerZ enabled"] = True
        p.extra_generation_params["CCZ_gender"] = gender
        p.extra_generation_params["CCZ_insert_start"] = insert_start
        p.extra_generation_params["CCZ_declone_weight"] = declone_weight
        p.extra_generation_params["CCZ_use_main_seed"] = use_main_seed
        p.extra_generation_params["CCZ_declone_seed"] = declone_seed
        p.extra_generation_params["CCZ_use_components"] = ",".join(use_components)
        if exclude_regions:
            p.extra_generation_params["CCZ_exclude_regions"] = ",".join(exclude_regions)
        if exclude_hairlength:
            p.extra_generation_params["CCZ_exclude_hairlength"] = ",".join(exclude_hairlength)
        if exclude_haircolor:
            p.extra_generation_params["CCZ_exclude_haircolor"] = ",".join(exclude_haircolor)
        if exclude_hairstyle:
            p.extra_generation_params["CCZ_exclude_hairstyle"] = ",".join(exclude_hairstyle)
            
        countrytree = self.prompt_tree["country"]
        hairtree = self.prompt_tree["hair"]

        regions = sorted_difference(countrytree.keys(), exclude_regions)
        hairlengths = sorted_difference(hairtree["length"].keys(), exclude_hairlength)
        haircolors = sorted_difference(hairtree["color"].keys(), exclude_haircolor)
        hairstyles = sorted_difference(hairtree["style"].keys(), exclude_hairstyle)

        use_name = "name" in use_components
        use_country = "country" in use_components
        use_length = "hair length" in use_components
        use_style = "hair style" in use_components
        use_color = "hair color" in use_components

        logger.debug(f"iterating through prompts for batch")
        for i, prompt in enumerate(p.all_prompts):
            # set declone seed and initialize rng
            rng = random.Random()
            logger.debug(f"fixed_batch_seed={fixed_batch_seed}")
            seed = declone_seed
            if not fixed_batch_seed:
                logger.debug("not using fixed_batch_seed, incrementing image declone_seed")
                seed = p.all_seeds[i] if use_main_seed else declone_seed + i
            logger.debug(f"prompt #{i} main seed={p.all_seeds[i]}, declone_seed={declone_seed}, image declone_seed={seed}")
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
            logger.debug(f"countrydata={countrydata}")

            # select hair color
            hairdata = countrydata.get("hair", hairtree["defaultweight"][region])
            logger.debug(f"hairdata={hairdata}")
            maincolor = rng.choices(haircolors, weights=[hairdata[col] for col in haircolors])[0]
            logger.debug(f"selected maincolor={maincolor} from {haircolors}")
            maincolor_colors = hairtree["color"][maincolor]
            color = rng.choice(maincolor_colors)
            logger.debug(f"selected color={color} from {maincolor_colors}")
            
            # select hair length
            mainlength = rng.choice(hairlengths)
            logger.debug(f"selected mainlength={mainlength} from {hairlengths}")
            mainlength_lengths = hairtree["length"][mainlength]
            length = rng.choice(mainlength_lengths)
            logger.debug(f"selected length={length} from {mainlength_lengths}")

            # select hair style
            mainstyle = rng.choice(hairstyles)
            logger.debug(f"selected mainstyle={mainstyle} from {hairstyles}")
            mainstyle_styles = hairtree["style"][mainstyle]
            style = rng.choice(mainstyle_styles)
            logger.debug(f"selected style={style} from {mainstyle_styles}")

            # select name
            names = countrydata["names"]
            name = rng.choice(names)
            logger.debug(f"select name={name} from {names}")

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

            if inserted_prompt:
                if declone_weight != 1:
                    inserted_prompt = f"({inserted_prompt}:{declone_weight})"

                if insert_start:
                    p.all_prompts[i] = inserted_prompt + ", " + prompt
                else:
                    p.all_prompts[i] = prompt + ", " + inserted_prompt

                logger.debug(f"prompt #{i} {p.all_prompts[i]}")
    

            # set prompt weight
            if declone_weight != 1:
                inserted_prompt = f"({inserted_prompt}:{declone_weight})"
            
            # insert prompt
            logger.info(f"{inserted_prompt}")
            p.all_prompts[i] = f"{inserted_prompt}, {prompt}" if insert_start else f"{prompt}, {inserted_prompt}"
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


script_callbacks.on_ui_settings(on_ui_settings)
