from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Mapping, cast

import matplotlib.path as mpath
import numpy as np
import torch
from matplotlib import patches as patches
from matplotlib import pyplot as plt
from torchdata.datapipes.iter import IterableWrapper
from tqdm import tqdm
from transformers import BertModel, BertTokenizer


@dataclass
class Dataset:
    classes: np.ndarray
    locations: np.ndarray
    sizes: np.ndarray
    rotations: np.ndarray
    colors: np.ndarray
    colors_hls: np.ndarray
    unpaired: np.ndarray


def get_transformed_coordinates(
    coordinates: np.ndarray, origin: np.ndarray, scale: float, rotation: float
) -> np.ndarray:
    center = np.array([[0.5, 0.5]])
    rotation_m = np.array(
        [
            [np.cos(rotation), -np.sin(rotation)],
            [np.sin(rotation), np.cos(rotation)],
        ]
    )
    rotated_coordinates = (coordinates - center) @ rotation_m.T
    return origin + scale * rotated_coordinates


def get_diamond_patch(
    location: np.ndarray,
    scale: int,
    rotation: float,
    color: np.ndarray,
) -> patches.Polygon:
    x, y = location[0], location[1]
    coordinates = np.array([[0.5, 0.0], [1, 0.3], [0.5, 1], [0, 0.3]])
    origin = np.array([[x, y]])
    patch = patches.Polygon(
        get_transformed_coordinates(coordinates, origin, scale, rotation),
        facecolor=color,
    )
    return patch


def get_triangle_patch(
    location: np.ndarray,
    scale: int,
    rotation: float,
    color: np.ndarray,
) -> patches.Polygon:
    x, y = location[0], location[1]
    origin = np.array([[x, y]])
    coordinates = np.array([[0.5, 1.0], [0.2, 0.0], [0.8, 0.0]])
    patch = patches.Polygon(
        get_transformed_coordinates(coordinates, origin, scale, rotation),
        facecolor=color,
    )
    return patch


def get_egg_patch(
    location: np.ndarray, scale: int, rotation: float, color: np.ndarray
) -> patches.PathPatch:
    x, y = location[0], location[1]
    origin = np.array([[x, y]])
    coordinates = np.array(
        [
            [0.5, 0],
            [0.8, 0],
            [0.9, 0.1],
            [0.9, 0.3],
            [0.9, 0.5],
            [0.7, 1],
            [0.5, 1],
            [0.3, 1],
            [0.1, 0.5],
            [0.1, 0.3],
            [0.1, 0.1],
            [0.2, 0],
            [0.5, 0],
        ]
    )
    codes = [
        mpath.Path.MOVETO,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
    ]
    path = mpath.Path(
        get_transformed_coordinates(coordinates, origin, scale, rotation),
        codes,
    )
    patch = patches.PathPatch(path, facecolor=color)
    return patch


def generate_image(
    ax: plt.Axes,
    cls: int,
    location: np.ndarray,
    scale: int,
    rotation: float,
    color: np.ndarray,
    imsize: int = 32,
) -> None:
    color = color.astype(np.float32) / 255
    if cls == 0:
        patch = get_diamond_patch(location, scale, rotation, color)
    elif cls == 1:
        patch = get_egg_patch(location, scale, rotation, color)
    elif cls == 2:
        patch = get_triangle_patch(location, scale, rotation, color)
    else:
        raise ValueError("Class does not exist.")

    ax.add_patch(patch)
    ax.set_xticks([])  # type: ignore
    ax.set_yticks([])  # type: ignore
    ax.grid(False)
    ax.set_xlim(0, imsize)
    ax.set_ylim(0, imsize)


def generate_scale(n_samples: int, min_val: int, max_val: int) -> np.ndarray:
    assert max_val > min_val
    return np.random.randint(min_val, max_val + 1, n_samples)


def generate_color(
    n_samples: int, min_lightness: int = 0, max_lightness: int = 256
) -> tuple[np.ndarray, np.ndarray]:
    import cv2

    assert 0 <= max_lightness <= 256
    hls = np.random.randint(
        [0, min_lightness, 0],
        [181, max_lightness, 256],
        size=(1, n_samples, 3),
        dtype=np.uint8,
    )
    rgb = cv2.cvtColor(hls, cv2.COLOR_HLS2RGB)[0]  # type: ignore
    return rgb.astype(int), hls[0].astype(int)


def generate_rotation(n_samples: int) -> np.ndarray:
    rotations = np.random.rand(n_samples) * 2 * np.pi
    return rotations


def generate_location(
    n_samples: int, max_scale: int, imsize: int
) -> np.ndarray:
    assert max_scale <= imsize
    margin = max_scale // 2
    locations = np.random.randint(margin, imsize - margin, (n_samples, 2))
    return locations


def generate_class(n_samples: int) -> np.ndarray:
    return np.random.randint(3, size=n_samples)


def generate_unpaired_attr(n_samples: int) -> np.ndarray:
    return np.random.rand(n_samples)


def generate_dataset(
    n_samples: int,
    min_scale: int,
    max_scale: int,
    min_lightness: int,
    max_lightness: int,
    imsize: int,
    classes: np.ndarray | None = None,
) -> Dataset:
    if classes is None:
        classes = generate_class(n_samples)
    sizes = generate_scale(n_samples, min_scale, max_scale)
    locations = generate_location(n_samples, max_scale, imsize)
    rotation = generate_rotation(n_samples)
    colors_rgb, colors_hls = generate_color(
        n_samples, min_lightness, max_lightness
    )
    unpaired = generate_unpaired_attr(n_samples)
    return Dataset(
        classes=classes,
        locations=locations,
        sizes=sizes,
        rotations=rotation,
        colors=colors_rgb,
        colors_hls=colors_hls,
        unpaired=unpaired,
    )


def save_dataset(path_root: Path, dataset: Dataset, imsize: int) -> None:
    dpi = 1
    enumerator = tqdm(
        enumerate(
            zip(
                dataset.classes,
                dataset.locations,
                dataset.sizes,
                dataset.rotations,
                dataset.colors,
            )
        ),
        total=len(dataset.classes),
    )
    for k, (cls, location, size, rotation, color) in enumerator:
        path_file = path_root / f"{k}.png"

        fig, ax = plt.subplots(figsize=(imsize / dpi, imsize / dpi), dpi=dpi)
        ax = cast(plt.Axes, ax)
        generate_image(ax, cls, location, size, rotation, color, imsize)
        ax.set_facecolor("black")
        plt.tight_layout(pad=0)
        plt.savefig(path_file, dpi=dpi, format="png")
        plt.close(fig)


def load_labels_old(path_root: Path) -> Dataset:
    labels = np.load(path_root)
    return Dataset(
        classes=labels[:, 0],
        locations=labels[:, 1:3],
        sizes=labels[:, 3],
        rotations=labels[:, 4],
        colors=labels[:, 5:8],
        colors_hls=labels[:, 8:11],
        unpaired=np.zeros_like(labels[:, 0]),
    )


def load_labels(path_root: Path) -> Dataset:
    labels = np.load(path_root)
    return Dataset(
        classes=labels[:, 0],
        locations=labels[:, 1:3],
        sizes=labels[:, 3],
        rotations=labels[:, 4],
        colors=labels[:, 5:8],
        colors_hls=labels[:, 8:11],
        unpaired=labels[:, 11],
    )


def save_labels(path_root: Path, dataset: Dataset) -> None:
    labels = np.concatenate(
        [
            dataset.classes.reshape((-1, 1)),
            dataset.locations,
            dataset.sizes.reshape((-1, 1)),
            dataset.rotations.reshape((-1, 1)),
            dataset.colors,
            dataset.colors_hls,
            dataset.unpaired.reshape((-1, 1)),
        ],
        axis=1,
    ).astype(np.float32)
    np.save(path_root, labels)


def save_bert_latents(
    sentences: list[str],
    bert_path: str,
    output_path: Path,
    split: str,
    device: torch.device,
    compute_statistics: bool = False,
) -> None:
    transformer = BertModel.from_pretrained(bert_path)
    transformer.eval()  # type: ignore
    transformer.to(device)  # type: ignore
    for p in transformer.parameters():  # type: ignore
        p.requires_grad_(False)
    tokenizer = BertTokenizer.from_pretrained(bert_path)

    batch_size = 64
    dp = IterableWrapper(sentences).batch(batch_size, drop_last=False)
    latents = []
    for batch in tqdm(dp, total=len(sentences) // batch_size):
        tokens = tokenizer(batch, return_tensors="pt", padding=True).to(device)
        z = transformer(**tokens)["last_hidden_state"][:, 0]  # type: ignore
        latents.append(z.cpu().numpy())
    all_latents = np.concatenate(latents, axis=0)
    np.save(output_path / f"{split}_latent.npy", latents)

    if compute_statistics:
        mean = all_latents.mean(axis=0)
        std = all_latents.std(axis=0)
        np.save(output_path / "latent_mean.npy", mean)
        np.save(output_path / "latent_std.npy", std)


def get_modality_split(
    dataset_size: int,
    aligned_domains_proportion: Mapping[frozenset, float],
) -> Dict[frozenset, np.ndarray]:
    print(aligned_domains_proportion)
    selection = {}
    for domains, proportion in aligned_domains_proportion.items():
        assert 0 <= proportion <= 1
        selection[domains] = np.random.rand(dataset_size) < proportion
    return selection


def get_deterministic_name(
    domain_alignment: Mapping[frozenset[str], float], seed: int
) -> str:
    domain_names = {
        ",".join(sorted(list(domain))): prop
        for domain, prop in domain_alignment.items()
    }
    sorted_domain_names = sorted(
        list(domain_names.items()),
        key=lambda x: x[0],
    )

    split_name = (
        "_".join([f"{domain}:{prop}" for domain, prop in sorted_domain_names])
        + f"_seed:{seed}"
    )
    return split_name
