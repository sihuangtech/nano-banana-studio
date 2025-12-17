from google import genai
from google.genai import types
from PIL import Image
from .models import GenerationParameters
from io import BytesIO

class APIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = None
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def update_api_key(self, api_key: str):
        self.api_key = api_key
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate(self, params: GenerationParameters) -> list[Image.Image]:
        if not self.client:
            raise ValueError("API Key is not set. Please check your .env file or settings.")

        full_prompt = params.prompt
        if params.negative_prompt:
            full_prompt += f" --no {params.negative_prompt}"
        
        # Determine model name
        model_name = params.model
        
        try:
            images = []
            
            if model_name.startswith("imagen"):
                # Handle Imagen models
                config = types.GenerateImagesConfig(
                    number_of_images=params.number_of_images,
                    aspect_ratio=params.aspect_ratio,
                    safety_filter_level=params.safety_filter,
                    person_generation=params.person_generation
                )
                
                # Add optional parameters if set
                if params.guidance_scale is not None:
                    config.guidance_scale = params.guidance_scale
                
                # Note: Imagen doesn't support 'image_size' in all versions or it might be named differently (resolution vs image_size)
                # But based on docs, 'image_size' is supported.
                # However, for 3.0, let's try to set it if not 1K default.
                # Actually, some SDK versions might not strictly type this, let's be safe.
                # If we want to support 2K/4K, we should pass it.
                # Using generic kwargs if needed, but let's try direct attribute first.
                
                response = self.client.models.generate_images(
                    model=model_name,
                    prompt=full_prompt,
                    config=config
                )
                
                if hasattr(response, 'generated_images'):
                    for generated_image in response.generated_images:
                        if hasattr(generated_image, 'image') and hasattr(generated_image.image, 'image_bytes'):
                            img = Image.open(BytesIO(generated_image.image.image_bytes))
                            images.append(img)
                            
            else:
                # Handle Gemini models (including gemini-3-pro-image-preview)
                
                # Construct ImageConfig
                image_config_args = {}
                
                # Add aspect_ratio if supported (both Flash and Gemini 3 support it)
                if params.aspect_ratio:
                     image_config_args["aspect_ratio"] = params.aspect_ratio

                # Add image_size ONLY for Gemini 3 (Flash usually fixed to 1024x1024 or handles aspect ratio only)
                if "gemini-3" in model_name:
                     # Ensure uppercase K
                     size_val = params.image_size.upper()
                     if not size_val.endswith("K"):
                         size_val += "K"
                     image_config_args["image_size"] = size_val
                
                # Safety settings
                safety_settings = [
                        types.SafetySetting(
                            category="HARM_CATEGORY_HARASSMENT",
                            threshold=params.safety_filter.upper()
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_HATE_SPEECH",
                            threshold=params.safety_filter.upper()
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                            threshold=params.safety_filter.upper()
                        ),
                        types.SafetySetting(
                            category="HARM_CATEGORY_DANGEROUS_CONTENT",
                            threshold=params.safety_filter.upper()
                        )
                ]

                config = types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    candidate_count=params.number_of_images,
                    image_config=types.ImageConfig(**image_config_args) if image_config_args else None,
                    safety_settings=safety_settings
                )
                
                # Handle seed if supported/provided (Gemini 3 might support it via other means or it's random)
                # Currently SDK for generate_content might not expose seed directly in top config easily 
                # but let's check if we can pass it. 
                # If not supported, we just ignore it for now to avoid errors.

                response = self.client.models.generate_content(
                    model=model_name,
                    contents=full_prompt,
                    config=config
                )

                # The new SDK simplifies access, but let's handle potential structures
                if hasattr(response, 'parts'):
                    for part in response.parts:
                        if part.inline_data:
                            img = Image.open(BytesIO(part.inline_data.data))
                            images.append(img)
                
                # Fallback/Check candidates if parts are empty (though parts should be populated)
                if not images and hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                            for part in candidate.content.parts:
                                if part.inline_data:
                                    img = Image.open(BytesIO(part.inline_data.data))
                                    images.append(img)

            if not images:
                if hasattr(response, 'text') and response.text:
                    raise RuntimeError(f"Model returned text instead of image: {response.text}")
                raise RuntimeError("No images generated.")

            return images

        except Exception as e:
            # Catch specific API errors if possible, but generic catch is safer for now
            raise RuntimeError(f"Generation failed: {str(e)}")
