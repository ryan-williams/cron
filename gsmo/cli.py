from os import listdir
from os.path import isdir
from re import match
import yaml

class Arg:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


run_args = [
    Arg('-b','--branch',help="Branch to clone, work in, and push results back to. Can also be passed as a trailing '@<branch>' slug on directory path or remote Git repo URL. For local repositories, implies --clone"),
    Arg('--clone',action='store_true',help='Clone local directory into a temporary dir for duration of the run'),
    Arg('--commit',action='append',help='Paths to `git add` and commit after running'),
    Arg('-C','--dir',help="Resolve paths (incl. mounts) relative to this directory (default: current directory)"),
    Arg('-o','--out',help='Path or directory to write output notebook to (relative to `--dir` directory; default: "nbs")'),
    Arg('--push',action='append',help='Push to this remote spec when done running'),
    Arg('-x','--run','--execute',help='Notebook to run (default: run.ipynb)'),
    Arg('-y','--yaml',action='append',help='YAML string(s) with configuration settings for the module being run'),
    Arg('-Y','--yaml-path',action='append',help='YAML file(s) with configuration settings for the module being run'),  # TODO: update example nb
]

REMOTE_REFSPEC_REGEX = '(?P<remote>[^/]+)(?:/(?P<spec>.*))?'
def parse_ref(ref):
    if not (m := match(REMOTE_REFSPEC_REGEX, ref)):
        raise ValueError(f'Invalid push ref: {ref}')
    remote = m['remote']
    spec = m['spec']
    if spec:
        return (remote, spec)
    else:
        return (remote,)


def load_run_config(args):
    # Load configs to pass into run container
    run_config = {}
    if (run_config_yaml_paths := args.yaml_path):
        for run_config_yaml_path in run_config_yaml_paths:
            if isdir(run_config_yaml_path):
                raise RuntimeError(f'run_config_yaml_path {run_config_yaml_path} is a directory: {listdir(run_config_yaml_path)}')
            with open(run_config_yaml_path,'r') as f:
                run_config.update(yaml.safe_load(f))

    if (run_config_yaml_strs := args.yaml):
        for run_config_yaml_str in run_config_yaml_strs:
            run_config_yaml = yaml.safe_load(run_config_yaml_str)
            run_config.update(run_config_yaml)

    return run_config
