import os
import yaml

def read_experiment_info(local_working_directory):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    experiments_info_file = os.path.join(dir_path, 'cluster_runner/project_experiments/experiments_info.yaml')
    if os.path.isfile(experiments_info_file):
        with open(experiments_info_file,'r') as stream:
            experiments_info = yaml.safe_load(stream)
    else:
        experiments_info = {'experiments_in_this_project' : 0}
        with open(experiments_info_file, 'w', encoding='utf8') as outfile:
            yaml.dump(experiments_info, outfile)

    return experiments_info