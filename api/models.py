from pydantic import BaseModel, Field
from typing import Optional, Literal

class GenerationParameters(BaseModel):
    prompt: str = Field(..., description="The prompt for image generation")
    negative_prompt: Optional[str] = Field(None, description="Negative prompt (appended to prompt)")
    model: str = Field("gemini-2.5-flash", description="Model to use for generation")
    
    # Image configuration
    aspect_ratio: str = Field("1:1", description="Aspect ratio of the generated image")
    number_of_images: int = Field(1, ge=1, le=4, description="Number of images to generate")
    image_size: str = Field("1K", description="Resolution of the image (1K, 2K, 4K)")
    
    # Advanced settings
    safety_filter: str = Field("block_none", description="Safety filter level")
    person_generation: str = Field("allow_adult", description="Person generation policy")
    seed: Optional[int] = Field(None, description="Seed for generation")
    guidance_scale: Optional[float] = Field(None, description="Guidance scale (CFG)")

class GenerationResponse(BaseModel):
    images: list[str]  # Base64 encoded strings or paths (handled by client)
    info: str
