import subprocess
import sys
import random
import os
from time import sleep
from utils.utils import load_ready_contexts
from utils.utils import save_all_experiments
from utils.utils import read_context
from utils.utils import read_all_experiments
from utils.create_sbatch import  create_sbatch
from utils.utils import create_new_experiment
from utils.utils import update_jobs_status
from utils.utils import check_if_running
from utils.utils import load_cluster_info


VERBOSE = True
# READ ARGUMENTS:
project_name = sys.argv[1]
project_path = sys.argv[2]
file_dir = sys.argv[3]
file_to_execute = sys.argv[4]
file_path_relative_to_root = sys.argv[5]
file_name = sys.argv[6]

all_experiments_info = read_all_experiments()
if all_experiments_info is None:
    all_experiments_info = {}
ready_contexts = load_ready_contexts()
cluster_info = load_cluster_info()
login = cluster_info['login']
user = cluster_info['user']
remote_venv = cluster_info['remote_venv']
local_storage_path = cluster_info['local_storage_path']
local_experiments_path = cluster_info['local_experiments_path']

current_context_file = os.path.join(file_dir, 'run_context.yaml')
current_context = read_context(current_context_file)

#create remote folder
remote_folder = os.path.join(cluster_info['remove_storage_path'], project_name, current_context['remote_subfolder'])

print(f'Making folder: {remote_folder}') if VERBOSE else print('', end='')
subprocess.run(f'ssh {login} mkdir -p {remote_folder}', shell=True, capture_output=True)
subprocess.run(f'ssh {login} mkdir -p {remote_folder}/sbatch_files', shell=True, capture_output=True, encoding='utf-8')
subprocess.run(f'ssh {login} mkdir -p {remote_folder}/outputs', shell=True, capture_output=True, encoding='utf-8')
print(f'Synchronizing files.') if VERBOSE else print('', end='')
subprocess.run(f'rsync -avz --exclude cluster_runner {project_path}/ {login}:{remote_folder}/', shell=True, capture_output=True)

print('Creating root_run_file:') if VERBOSE else print('', end='')
#x = re.sub(file_path_relative_to_root, '/', '.')
local_id = random.randint(1,10**7)
import_path = 'import ' + file_path_relative_to_root.replace('/', '.').replace('.py', '')
local_entry_point = f'{file_name}_{local_id}.py'
entry_file_name = os.path.join(local_storage_path, f'{file_name}_{local_id}.py')
with open(entry_file_name, 'w') as file:
    file.write(import_path)
print('Sending root_run_file to remote') if VERBOSE else print('', end='')
subprocess.run(f'scp -- {entry_file_name} {login}:{remote_folder}/', shell=True, capture_output=True)
remote_output_file = f'{remote_folder}/outputs/out__{local_entry_point}__.out'
remote_error_file = f'{remote_folder}/outputs/err__{local_entry_point}__.err'
print('Creating sbatch file') if VERBOSE else print('', end='')
sbatch_file_name = entry_file_name + '__.sbatch'
local_sbatch_name = local_entry_point + '__.sbatch'
sbatch_content = create_sbatch(current_context['job_name'],
                               current_context['n_nodes'],
                               current_context['n_tasks_per_node'],
                               current_context['mem_per_cpu'],
                               current_context['time'],
                               current_context['grant_name'],
                               current_context['partition'],
                               remote_output_file,
                               remote_error_file,
                               remote_venv,
                               remote_folder,
                               local_entry_point
                               )

with open(sbatch_file_name, 'w') as file:
    file.write(sbatch_content)

subprocess.run(f'scp -- {sbatch_file_name} {login}:{remote_folder}/sbatch_files/', shell=True, capture_output=True)

print('Starting remote job') if VERBOSE else print('', end='')
job_info = subprocess.run(f'ssh {login} sbatch {remote_folder}/sbatch_files/{local_sbatch_name}', shell=True,
                          capture_output=True, encoding='utf-8')
if job_info.stdout == '':
    subprocess.run(f'ssh {login} sbatch {remote_folder}/sbatch_files/{local_sbatch_name}', shell=True,
                   capture_output=False, encoding='utf-8')

else:
    print(job_info.stdout)
    job_id = job_info.stdout.split()[3]
    new_experiment = create_new_experiment(entry_file_name, remote_output_file, remote_error_file, 'PD', current_context['time'],
                                           '0:00', project_name)
    all_experiments_info[job_id] = new_experiment
    save_all_experiments(all_experiments_info)
    update_jobs_status(login, user)

    running = True
    while running:
        output_lines_num = 0
        read_process = subprocess.run(f'ssh {login} cat "{remote_output_file}"', shell=True,
                                      capture_output=True, encoding='utf-8')
        output = read_process.stdout
        output_lines = output.split()
        if len(output_lines) > output_lines_num:
            for idx in range(output_lines_num, len(output_lines)):
                print(output_lines[idx])
        running = check_if_running(user, login, job_id)
        sleep(1)

    print('========== Finished ============')





# print('Create local sbatch file')
#
# def test_file_creating():
#     with open('elo_melo.txt', 'w') as file:
#         file.write('Siemanix')
#
# test_file_creating()
#
# subprocess.run(f'scp -- elo_melo.txt {login}:{remote_folder}/sbatch_files/', shell=True)


# x = my_jobs_info(login, user)
# print(x)
#create new experiment
# new_experiment = {
# 'experiment_id' : all_experiments_info['n_experiments'] + 1,
# 'experiment_original_entry_point' : file_to_execute
# 'experiment_sbatch_entry_point': 0}
