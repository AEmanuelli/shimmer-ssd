import os
from typing import cast

import matplotlib
import matplotlib.pyplot as plt
import torch
import torchvision.transforms.functional as F
from PIL.Image import Image
from shimmer.config import load_structured_config
from torchvision.utils import make_grid

import wandb
from simple_shapes_dataset import PROJECT_DIR
from simple_shapes_dataset.config.root import Config
from simple_shapes_dataset.logging import get_pil_image
from simple_shapes_dataset.modules.domains.visual import VisualDomainModule
from simple_shapes_dataset.modules.vae import (
    RAEEncoder,
    dim_exploration_figure,
)

matplotlib.use("Agg")


def image_grid_from_v_tensor(
    samples: torch.Tensor,
    _: int,
    ncols: int,
) -> Image:
    image = make_grid(samples, nrow=ncols, pad_value=1).detach()
    return F.to_pil_image(image)


def main() -> None:
    debug_mode = bool(int(os.getenv("DEBUG", "0")))
    config = load_structured_config(
        PROJECT_DIR / "config",
        Config,
        load_dirs=["viz_vae_v"],
        debug_mode=debug_mode,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    domain_module = cast(
        VisualDomainModule,
        VisualDomainModule.load_from_checkpoint(
            config.visualization.explore_vae.checkpoint
        ),
    )
    domain_module.eval().freeze()

    num_samples = config.visualization.explore_vae.num_samples
    range_start = config.visualization.explore_vae.range_start
    range_end = config.visualization.explore_vae.range_end
    fig = dim_exploration_figure(
        domain_module.vae,
        cast(RAEEncoder, domain_module.vae.encoder).z_dim,
        device,
        image_grid_from_v_tensor,
        num_samples,
        range_start,
        range_end,
    )
    caption = f"VAE_Exploration_from_{range_start}_to_{range_end}"
    image = get_pil_image(fig)

    if config.visualization.explore_vae.wandb_name is not None:
        wandb.init(
            project=config.wandb.project,
            entity=config.wandb.entity,
            id=config.visualization.explore_vae.wandb_name,
            resume=True,
        )
        wandb.log({"vae_exploration": [wandb.Image(image, caption=caption)]})

    else:
        plt.savefig(PROJECT_DIR / f"data/{caption}.pdf")
        plt.show()


if __name__ == "__main__":
    main()
