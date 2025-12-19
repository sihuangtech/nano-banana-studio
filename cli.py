import argparse
import sys
import logging
import yaml
import os
from api.models import GenerationParameters
from core.generator import GeneratorCore
from core.runner import GenerationRunner

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser(description="Nano Banana Studio CLI")
    
    # Config File
    parser.add_argument("-f", "--file", type=str, help="Path to YAML configuration file")

    # Generation Params (CLI arguments override YAML)
    parser.add_argument("--prompt", type=str, help="Prompt for image generation")
    parser.add_argument("--neg-prompt", type=str, default=None, help="Negative prompt")
    parser.add_argument("--model", type=str, default=None, help="Model name")
    parser.add_argument("--aspect-ratio", type=str, default=None, choices=["1:1", "16:9", "4:3", "3:4", "9:16"])
    parser.add_argument("--num-images", type=int, default=None, help="Number of images to generate")
    parser.add_argument("--image-size", type=str, default=None, choices=["1K", "2K", "4K"])
    parser.add_argument("--person-generation", type=str, default=None, choices=["allow_adult", "allow_all", "dont_allow"])
    parser.add_argument("--safety-filter", type=str, default=None, choices=["block_none", "block_only_high", "block_medium_and_above", "block_low_and_above"])
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument("--guidance-scale", type=float, default=None, help="Guidance scale")
    
    # Retry Params
    parser.add_argument("--retry", action="store_true", default=None, help="Enable auto retry")
    parser.add_argument("--retry-interval", type=int, default=None, help="Retry interval in seconds")
    parser.add_argument("--max-retries", type=int, default=None, help="Max retries (0 for infinite)")

    # API Key (optional override)
    parser.add_argument("--api-key", type=str, default=None, help="Google API Key (overrides env/config)")
    
    return parser.parse_args()

def load_config(args):
    """
    Load configuration from YAML file (if provided) and merge with CLI arguments.
    CLI arguments take precedence.
    """
    config = {
        "prompt": None,
        "neg_prompt": None,
        "model": "gemini-3-pro-image-preview",
        "aspect_ratio": "1:1",
        "num_images": 1,
        "image_size": "1K",
        "person_generation": "allow_adult",
        "safety_filter": "block_none",
        "seed": None,
        "guidance_scale": None,
        "retry": False,
        "retry_interval": 10,
        "max_retries": 0,
        "api_key": None
    }

    # 1. Load from YAML file if provided
    # Default to 'generate.yaml' if no file specified AND no prompt specified (assuming full config driven)
    yaml_file = args.file
    if not yaml_file and not args.prompt and os.path.exists("generate.yaml"):
        yaml_file = "generate.yaml"
        logger.info(f"No args provided, auto-loading default config: {yaml_file}")

    if yaml_file:
        if not os.path.exists(yaml_file):
            logger.error(f"Configuration file not found: {yaml_file}")
            sys.exit(1)
        
        try:
            with open(yaml_file, 'r') as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    # Update config with YAML values, mapping keys if necessary
                    # Assuming YAML keys match our internal config keys
                    # We might need to map 'negative_prompt' -> 'neg_prompt' etc if YAML schema differs
                    
                    # Direct mapping for matching keys
                    for key in config.keys():
                        if key in yaml_config:
                            config[key] = yaml_config[key]
                    
                    # Handle aliases
                    if "negative_prompt" in yaml_config:
                        config["neg_prompt"] = yaml_config["negative_prompt"]
                        
        except Exception as e:
            logger.error(f"Error parsing YAML file: {e}")
            sys.exit(1)

    # 2. Override with CLI arguments (if they are not None)
    if args.prompt is not None: config["prompt"] = args.prompt
    if args.neg_prompt is not None: config["neg_prompt"] = args.neg_prompt
    if args.model is not None: config["model"] = args.model
    if args.aspect_ratio is not None: config["aspect_ratio"] = args.aspect_ratio
    if args.num_images is not None: config["num_images"] = args.num_images
    if args.image_size is not None: config["image_size"] = args.image_size
    if args.person_generation is not None: config["person_generation"] = args.person_generation
    if args.safety_filter is not None: config["safety_filter"] = args.safety_filter
    if args.seed is not None: config["seed"] = args.seed
    if args.guidance_scale is not None: config["guidance_scale"] = args.guidance_scale
    
    # Retry params need special handling because store_true default is False/None logic
    # If args.retry is True (flag present), use it.
    # If args.retry is False (flag absent), use YAML or default.
    # But wait, argparse 'store_true' defaults to False. We changed default to None in parser to detect presence?
    # Actually, let's check if the user *explicitly* passed the flag.
    # With `default=None` and `action='store_true'`, if flag is present -> True. If not -> None.
    # Wait, store_true doesn't support default=None in the way we want for tri-state.
    # Let's stick to standard override: if YAML says True, and CLI flag is NOT present (False), result is True?
    # No, standard CLI practice: Flag enables it.
    # If we want YAML to enable it, and CLI to optionally disable it, we need --no-retry.
    # For simplicity:
    # If args.retry is True (flag passed), force True.
    # If args.retry is False (flag NOT passed), keep YAML value.
    if args.retry: 
        config["retry"] = True
    
    if args.retry_interval is not None: config["retry_interval"] = args.retry_interval
    if args.max_retries is not None: config["max_retries"] = args.max_retries
    if args.api_key is not None: config["api_key"] = args.api_key

    return config

def run_cli():
    args = parse_args()
    config = load_config(args)
    
    if not config["prompt"]:
        print("Error: Prompt is required (provide via CLI --prompt or YAML file)")
        sys.exit(1)

    core = GeneratorCore()
    
    if config["api_key"]:
        core.update_api_key(config["api_key"])
        
    if not core.settings.get("api_key"):
        print("Error: API Key not found. Set GOOGLE_API_KEY env var, use --api-key, or set in YAML")
        sys.exit(1)
        
    params = GenerationParameters(
        prompt=config["prompt"],
        negative_prompt=config["neg_prompt"],
        aspect_ratio=config["aspect_ratio"],
        number_of_images=config["num_images"],
        model=config["model"],
        image_size=config["image_size"],
        person_generation=config["person_generation"],
        safety_filter=config["safety_filter"],
        seed=config["seed"],
        guidance_scale=config["guidance_scale"]
    )
    
    runner = GenerationRunner(
        core=core,
        params=params,
        retry_enabled=config["retry"],
        retry_interval=config["retry_interval"],
        max_retries=config["max_retries"],
        status_callback=lambda msg: logger.info(f"STATUS: {msg}")
    )
    
    try:
        images = runner.run()
        print(f"Successfully generated {len(images)} images.")
    except Exception as e:
        print(f"Generation failed after retries: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_cli()
