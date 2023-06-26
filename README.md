# Simple Shapes dataset

## Installation
First clone and cd to the downloaded directory.

Using poetry:

```
poetry install
```

With pip:
```
pip install .
```

## Create dataset
```
shapesd create --output_path "/path/to/dataset"
```
Configuration values:
- `--output_path, -o OUTPUT_PATH` where to save the dataset
- `--seed, -s SEED` random seed (defaults to 0)
- `--img_size` size of the images (defaults to 32)
- `--ntrain` number of train examples (defaults to 500,000)
- `--nval` number of validation examples (defaults to 1000)
- `--ntest` number of test examples (defaults to 1000)
- `--bert_path, -b` which pretrained BERT model to use (defaults to "bert-base-uncased")
- `--domain_alignment, --da, -a` domain alignment to generate (see next section).

For more configurations, see
```
shapesd create --help
```

## Add a domain alignment split
```
shapesd alignment --dataset_path "/path/to/dataset" --seed 0 --da t,v 0.01 --da t 1. --da v 1.
```
will create an alignment split where 0.01% of the example between domains "t" and "v" will
be aligned, and that contains all data for "t" and "v".


## Use the dataset
Load the dataset:
```python
import torchvision

from simple_shapes_dataset.modules import SimpleShapesDataset


dataset = SimpleShapesDataset(
    "/path/to/dataset",
    split="train",
    selected_domains=["v"],  # Will only load the visual domain
    transforms={
        # transform to apply to the visual domain
        "v": torchvision.transforms.ToTensor(),
    }
)

```

If you need to use the alignment splits, use:
```python
from simple_shapes_dataset.modules import get_aligned_datasets

datasets = get_aligned_datasets(
    "/path/to/dataset",
    split="train",
    # Node that this will load the file created using `shapesd alignement`
    # if the requested configuration does not exist, it will fail.
    domain_proportions={
        frozenset(["v", "t"]): 0.5,  # proportion of data where visual and text are aligned
        # you also need to provide the proportion for individual domains.
        frozenset("v"): 1.0,
        frozenset("t"): 1.0,
    },
    seed=0,
    transforms={
        "v": torchvision.transforms.ToTensor(),
    }
)
```

## Old style dataset
If `train_latent.npy` is not available in your dataset, you may need to specify to path
to the latent vectors (probably something like `train_bert-base-uncased.npy`).


```python
SimpleShapesDataset(
    "/path/to/dataset",
    split="train",
    selected_domains=["t"],  # Will only load the visual domain
    transforms={
        # transform to apply to the visual domain
        "v": torchvision.transforms.ToTensor(),
    },
    domain_args={
        "t": {
            "latent_filepath": "bert-base-uncased"
        }
    }
)
```
The `domain_args` argument is also available in `get_aligned_datasets`.
