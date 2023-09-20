# node_model_loader.py
# Simple proof of concept custom node to load models.

import contextlib
import os
import pickle
import time
import zstandard as zstd

from loguru import logger


class HordeCheckpointLoader:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model_manager": ("<model manager instance>",),
                "model_name": ("<model name>",),
            },
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE")
    FUNCTION = "load_checkpoint"

    CATEGORY = "loaders"

    def load_checkpoint(
        self,
        model_manager,
        model_name,
    ):
        logger.debug(f"Loading model {model_name} through our custom node")

        if model_manager.manager is None:
            logger.error("horde_model_manager appears to be missing!")
            raise RuntimeError  # XXX better guarantees need to be made

        loaded_models = model_manager.manager.loaded_models
        if model_name not in loaded_models:
            logger.error(f"Model {model_name} is not loaded")
            raise RuntimeError  # XXX better guarantees need to be made

        model = loaded_models[model_name]["model"]
        clip = loaded_models[model_name]["clip"]
        vae = loaded_models[model_name]["vae"]

        # If we got strings, not objects, it's a cache reference, load the cache
        if type(model) is str:
            start_time = time.time()
            logger.info(f"Loading from disk cache model {model_name}")
            model_cache = model
            try:
                with model_manager.manager.disk_read_mutex:
                    with open(model, "rb") as cache:
                        c = zstd.ZstdCompressor()
                        with c.stream_reader(cache) as decompressor:
                            model = pickle.load(decompressor)
                            vae = pickle.load(decompressor)
                            clip = pickle.load(decompressor)
                # Record this model as being in ram again
                model_manager.manager.move_from_disk_cache(model_name, model, clip, vae)
                logger.info(
                    f"Loaded model {model_name} from disk cache in {round(time.time() - start_time, 1)} seconds",
                )
            except (pickle.PickleError, EOFError):
                # Most likely corrupt cache file, remove the file
                with contextlib.suppress(OSError):
                    os.remove(model)  # ... at least try to remove it

                raise Exception(f"Model cache file {model_cache} was corrupt. It has been removed.")

        # XXX # TODO I would like to revisit this dict->tuple conversion at some point soon
        return (model, clip, vae)


NODE_CLASS_MAPPINGS = {"HordeCheckpointLoader": HordeCheckpointLoader}
