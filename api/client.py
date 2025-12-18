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

                # Log the raw response for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.info("=" * 80)
                logger.info("RAW API RESPONSE:")
                logger.info(f"Response type: {type(response)}")
                logger.info(f"Response object: {response}")
                logger.info(f"Response dir: {dir(response)}")
                
                # Try to serialize response to see its structure
                try:
                    logger.info(f"Response __dict__: {response.__dict__ if hasattr(response, '__dict__') else 'N/A'}")
                except:
                    pass
                
                # Log specific attributes
                for attr in ['text', 'parts', 'candidates', 'prompt_feedback', 'usage_metadata']:
                    if hasattr(response, attr):
                        try:
                            value = getattr(response, attr)
                            logger.info(f"response.{attr}: {value}")
                        except Exception as e:
                            logger.info(f"response.{attr}: Error accessing - {e}")
                
                logger.info("=" * 80)

                # The new SDK simplifies access, but let's handle potential structures
                # First check if content was blocked
                if hasattr(response, 'prompt_feedback'):
                    if hasattr(response.prompt_feedback, 'block_reason'):
                        block_reason = response.prompt_feedback.block_reason
                        raise RuntimeError(f"Content blocked by safety filter: {block_reason}")
                
                # Check candidates for safety ratings
                if hasattr(response, 'candidates') and response.candidates:
                    for candidate in response.candidates:
                        # Check if candidate was blocked
                        if hasattr(candidate, 'finish_reason'):
                            finish_reason = str(candidate.finish_reason)
                            if 'SAFETY' in finish_reason or 'BLOCKED' in finish_reason:
                                safety_info = ""
                                if hasattr(candidate, 'safety_ratings'):
                                    safety_info = f" Safety ratings: {candidate.safety_ratings}"
                                raise RuntimeError(f"Content blocked due to safety: {finish_reason}{safety_info}")
                        
                        # Try to extract images from candidate
                        if hasattr(candidate, 'content') and candidate.content:
                            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                                for part in candidate.content.parts:
                                    if hasattr(part, 'inline_data') and part.inline_data:
                                        img = Image.open(BytesIO(part.inline_data.data))
                                        images.append(img)
                
                # Fallback: try response.parts directly (some SDK versions)
                if not images and hasattr(response, 'parts') and response.parts:
                    for part in response.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            img = Image.open(BytesIO(part.inline_data.data))
                            images.append(img)

            if not images:
                # Provide detailed error information
                error_details = []
                if hasattr(response, 'text') and response.text:
                    error_details.append(f"Model returned text: {response.text}")
                if hasattr(response, 'candidates'):
                    error_details.append(f"Candidates: {len(response.candidates) if response.candidates else 0}")
                if hasattr(response, 'prompt_feedback'):
                    error_details.append(f"Prompt feedback: {response.prompt_feedback}")
                
                error_msg = "No images generated."
                if error_details:
                    error_msg += " Details: " + ", ".join(error_details)
                raise RuntimeError(error_msg)

            return images

        except Exception as e:
            # Preserve original error information
            error_msg = f"Generation failed: {type(e).__name__}: {str(e)}"
            
            # Try to add response details if available
            try:
                if 'response' in locals():
                    details = []
                    if hasattr(response, 'prompt_feedback'):
                        details.append(f"Prompt feedback: {response.prompt_feedback}")
                    if hasattr(response, 'candidates') and response.candidates:
                        details.append(f"Candidates count: {len(response.candidates)}")
                        for i, candidate in enumerate(response.candidates):
                            if hasattr(candidate, 'finish_reason'):
                                details.append(f"Candidate {i} finish_reason: {candidate.finish_reason}")
                            if hasattr(candidate, 'safety_ratings'):
                                details.append(f"Candidate {i} safety_ratings: {candidate.safety_ratings}")
                    if details:
                        error_msg += "\n\nResponse details:\n" + "\n".join(details)
            except:
                pass  # If we can't get details, just use the original error
            
            raise RuntimeError(error_msg)

