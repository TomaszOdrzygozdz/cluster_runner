import re
import yaml
import subprocess


def load_cluster_info():
    with open("../cluster_info/cluster_info.yaml", 'r') as stream:
        cluster_info = yaml.safe_load(stream)

    return cluster_info

def load_ready_contexts():
    with open("cluster_info/run_contexts.yaml", 'r') as stream:
        ready_contexts = yaml.safe_load(stream)
    return ready_contexts

def read_all_experiments():
    with open("../project_experiments/experiments_info.yaml", 'r') as stream:
        all_experiments = yaml.safe_load(stream)
    return all_experiments

def save_all_experiments(all_experiments_data):
    with open("../project_experiments/experiments_info.yaml", 'w') as stream:
        yaml.dump(all_experiments_data, stream)

def read_context(file_name):
    all_contexts = load_ready_contexts()
    with open(file_name, 'r') as stream:
        current_context = yaml.safe_load(stream)
        if current_context['use_ready'] != 'None':
            return all_contexts[current_context['use_ready']]
        else:
            return current_context


def check_if_running(user, login, job_id):
    return job_id in show_my_jobs_info(user, login)


def show_my_jobs_info(user, login):
    my_jobs_raw_info = subprocess.run(f'ssh {login} squeue -u {user}', shell=True, capture_output=True,
                                      encoding='utf-8')
    info = my_jobs_raw_info.stdout.splitlines()
    my_jobs_info = {}
    for idx, line in enumerate(info):
        if idx > 0:
            job_id, partition, pname, _, status, time, nodes, nodelist = line.split()
            my_jobs_info[job_id] = {
                'status': status,
                'time': time,
                'nodes': nodes,
                'nodelist': nodelist
            }
    return my_jobs_info

def update_jobs_status(login, user):
    all_experiments = read_all_experiments()
    my_jobs_info = show_my_jobs_info(user, login)
    for job_id in my_jobs_info:
        if job_id not in all_experiments:
            all_experiments[job_id] = {}
        for key in my_jobs_info[job_id]:
            all_experiments[job_id][key] = my_jobs_info[job_id][key]
    for job_id in all_experiments:
        if job_id not in my_jobs_info:
            all_experiments[job_id]['status'] = 'D'
    save_all_experiments(all_experiments)




def create_new_experiment(remote_entry_point, remote_output, remote_error, status, time_limit, current_time, name):
    return {'remote_entry_point': remote_entry_point,
            'remote_output' : remote_output,
            'remote_error' : remote_error,
            'status' : status,
            'time_limit' : time_limit,
            'time' : current_time,
            'name' : name}