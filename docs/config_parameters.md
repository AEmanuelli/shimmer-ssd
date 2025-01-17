# Available config parameters in the project
Note: We use a "dot" separated syntax to represent nested values in the yaml config.
`dataset.path` refers to:
```yaml
dataset:
    path: 
```

## Create the config folder
You first need to generate your local `config` folder with:
```
ssd config create
```
This will locally create a `config` folder for the project.
Additional arguments:
* `--path`, `-p`, where to save the config files (defaults to `./config`)
* `--force`, `-f`, whether to override files if the destination of `--path` already
exists.

The folder contains several files:
* `main.yaml` (or historically `local.yaml`) where you will put most of your
configuration
* `debug.yaml` some config overides used when starting scripts in "debug mode" (see 
later section).
* other config files containing overides related to specific scripts. For example, 
`train_v.yaml` is also loaded (before `main.yaml`)

The files are loaded in the following order (lower priority, to higher priority):
* script specific config files (lowest priority)
* `main.yaml`
* `local.yaml`
* `debug.yaml` (if in debug mode)
* command line arguments (highest priority)

## Required values
The strict minimum in your config. In the following we will use the notation:
```
config_value: type (= default value if one exist)
```

### `dataset.path: Path`
Path to the simple-shapes-dataset. Can be downloaded with `shapesd download`

## Other config options
### `seed: int = 0`
Seed used for the alignment splits generated with `shapesd alignment add` and 
for training.
### `default_root_dir: Path = "./checkpoints"`
Path where wandb logs and checkpoints will be stored.

### `training.batch_size: int = 2056`

### `dataset.max_train_size: int | None = 500_000`
Max number of unpaired examples used during training.
This is here for legacy reasons. Prefer changing `domain_proportions`.
The proportion is relative to this value.

### `ood_seed: int | None = None`
Seed to load the out of distribution data.

## Config formatting
We also use some custom code to allow some interpolations, described here:
[https://github.com/bdvllrs/cfg-tools](https://github.com/bdvllrs/cfg-tools).

## Command line arguments

## Debug mode
