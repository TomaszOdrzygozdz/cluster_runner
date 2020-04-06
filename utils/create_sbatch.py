
def create_sbatch(job_name = 'project',
                  n_nodes = 1,
                  n_tasks_per_node = 24,
                  mem_per_cpu = '5GB',
                  time='00:01:00',
                  grant_name='plgrid',
                  partition='planningrl',
                  output='output.out',
                  error='err.err',
                  venv_path='',
                  remote_folder = '',
                  entry_point=''):
    sbatch = '#!/bin/bash -l\n'
    sbatch += f'#SBATCH -J {job_name}\n'
    sbatch += f'#SBATCH -N {n_nodes}\n'
    sbatch += f'#SBATCH --ntasks-per-node={n_tasks_per_node}\n'
    sbatch += f'#SBATCH --mem-per-cpu={mem_per_cpu}\n'
    sbatch += f'#SBATCH --time={time}\n'
    sbatch += f'#SBATCH -A {grant_name}\n'
    sbatch += f'#SBATCH -p {partition}\n'
    sbatch += f'#SBATCH --output="{output}"\n'
    sbatch += f'#SBATCH --error="{error}"\n'
    sbatch += 'module load plgrid/libs/python-mpi4py \n'
    sbatch += 'module load plgrid/tools/python \n'
    sbatch += 'module add plgrid/tools/impi\n'
    sbatch += f'source {venv_path}\n'
    sbatch += f'cd {remote_folder}\n'
    sbatch += f'mpiexec python3 {entry_point}'

    return sbatch
