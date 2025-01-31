# test_inference.py
import os

import pytest
from PIL import Image

from hordelib.comfy_horde import Comfy_Horde
from hordelib.shared_model_manager import SharedModelManager

from .testing_shared_functions import CosineSimilarityResultCode, check_single_inference_image_similarity


class TestInference:
    def test_unknown_pipeline(self, isolated_comfy_horde_instance: Comfy_Horde):
        result = isolated_comfy_horde_instance.run_image_pipeline("non-existent-pipeline", {})
        assert result is None

    def test_stable_diffusion_pipeline(
        self,
        stable_diffusion_model_name_for_testing: str,
        shared_model_manager: type[SharedModelManager],
        isolated_comfy_horde_instance: Comfy_Horde,
    ):
        params = {
            "sampler.sampler_name": "dpmpp_2m",
            "sampler.cfg": 7.5,
            "sampler.denoise": 1.0,
            "sampler.seed": 12345,
            "empty_latent_image.width": 512,
            "empty_latent_image.height": 512,
            "empty_latent_image.batch_size": 1,
            "sampler.scheduler": "karras",
            "sampler.steps": 25,
            "prompt.text": "a closeup photo of a confused dog",
            "negative_prompt.text": "cat, black and white, deformed",
            "model_loader.model_name": stable_diffusion_model_name_for_testing,
            "clip_skip.stop_at_clip_layer": -1,
            "model_loader.model_manager": shared_model_manager,
        }
        images = isolated_comfy_horde_instance.run_image_pipeline("stable_diffusion", params)
        assert images is not None

        pil_image = Image.open(images[0]["imagedata"])
        img_filename = "pipeline_stable_diffusion.png"
        pil_image.save(f"images/{img_filename}", quality=100)
        assert check_single_inference_image_similarity(
            f"images_expected/{img_filename}",
            pil_image,
        )

    def test_stable_diffusion_pipeline_clip_skip(
        self,
        stable_diffusion_model_name_for_testing: str,
        shared_model_manager: type[SharedModelManager],
        isolated_comfy_horde_instance: Comfy_Horde,
    ):
        params = {
            "sampler.sampler_name": "dpmpp_2m",
            "sampler.cfg": 7.5,
            "sampler.denoise": 1.0,
            "sampler.seed": 12345,
            "empty_latent_image.width": 512,
            "empty_latent_image.height": 512,
            "empty_latent_image.batch_size": 1,
            "sampler.scheduler": "karras",
            "sampler.steps": 25,
            "prompt.text": "a closeup photo of a confused dog",
            "negative_prompt.text": "cat, black and white, deformed",
            "model_loader.model_name": stable_diffusion_model_name_for_testing,
            "clip_skip.stop_at_clip_layer": -2,
            "model_loader.model_manager": shared_model_manager,
        }
        images = isolated_comfy_horde_instance.run_image_pipeline("stable_diffusion", params)
        assert images is not None

        pil_image = Image.open(images[0]["imagedata"])
        img_filename = "pipeline_stable_diffusion_clip_skip_2.png"
        pil_image.save(f"images/{img_filename}", quality=100)
        assert check_single_inference_image_similarity(
            f"images_expected/{img_filename}",
            pil_image,
        )

    def test_stable_diffusion_hires_fix_pipeline(
        self,
        stable_diffusion_model_name_for_testing: str,
        shared_model_manager: type[SharedModelManager],
        isolated_comfy_horde_instance: Comfy_Horde,
    ):
        params = {
            "sampler.seed": 1014,
            "sampler.cfg": 7.5,
            "sampler.scheduler": "normal",
            "sampler.sampler_name": "euler",
            "sampler.denoise": 1.0,
            "sampler.steps": 30,
            "prompt.text": (
                "photograph of medusa, snakes in hair, reverence princesss, cinematic, realistic, "
                "hyperrealistic, very realistic, extremely detailed, detailed, sharp focus, "
                "establishing shot, 8k resolution, dramatic lighting, award winning "
                "photograph, masterpiece, very detailed, sharp focus, very realistic lighting"
            ),
            "negative_prompt.text": (
                "render, cg, drawing, painting, artist, graphics, deformed, black and white, deformed eyes"
            ),
            "model_loader.model_name": stable_diffusion_model_name_for_testing,
            "model_loader.model_manager": shared_model_manager,
            "empty_latent_image.width": 512,
            "empty_latent_image.height": 512,
            "latent_upscale.width": 768,
            "latent_upscale.height": 768,
            "latent_upscale.crop": "disabled",
            "latent_upscale.upscale_method": "nearest-exact",
            "upscale_sampler.seed": 450089106307460,
            "upscale_sampler.steps": 30,
            "upscale_sampler.cfg": 8.0,
            "upscale_sampler.sampler_name": "euler",
            "upscale_sampler.scheduler": "simple",
            "upscale_sampler.denoise": 0.65,
            "clip_skip.stop_at_clip_layer": -1,
        }
        images = isolated_comfy_horde_instance.run_image_pipeline("stable_diffusion_hires_fix", params)
        assert images is not None

        pil_image = Image.open(images[0]["imagedata"])
        img_filename = "pipeline_stable_diffusion_hires_fix.png"
        pil_image.save(f"images/{img_filename}", quality=100)
        assert check_single_inference_image_similarity(
            f"images_expected/{img_filename}",
            pil_image,
        )

        params["clip_skip.stop_at_clip_layer"] = -2
        images = isolated_comfy_horde_instance.run_image_pipeline("stable_diffusion_hires_fix", params)
        assert images is not None

        pil_image = Image.open(images[0]["imagedata"])
        img_filename = "pipeline_stable_diffusion_hires_fix_clip_skip_2.png"
        pil_image.save(f"images/{img_filename}", quality=100)
        assert check_single_inference_image_similarity(
            f"images_expected/{img_filename}",
            pil_image,
        )
