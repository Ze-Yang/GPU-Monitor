# author: zeyang
import subprocess
import os
import time
import argparse
import numpy as np
import socket
from reprint import output
from message import send_mail


cmd = 'python /path/to/script.py'


def parse_args():
    """Parse input arguments"""
    parser = argparse.ArgumentParser(description='GPU resource monitoring.')
    parser.add_argument(
        '-n-gpus', '--num-gpus', type=int, default=8,
        help='Number of GPUs you need.')
    parser.add_argument(
        '-m', '--memory', type=int, required=True,
        help='Estimated GPU memory you need (MB per GPU).')
    parser.add_argument(
        '-inv', '--interval', type=int, default=2,
        help='Interval time (s) between queries of GPU status.')
    parser.add_argument(
        '--dir', type=str, default='path/to/project',
        help='Specify the working directory for your project.')
    parser.add_argument(
        '--sleep', action='store_true',
        help='Run sleep.py with endless loop to temporarily claim idle GPUs.')
    parser.add_argument(
        '--msg', action='store_true',
        help='Whether to send email message to report the status of task.')
    return parser.parse_args()


def gpu_info(args, ready_gpuids=[]):
    memory_total = list(map(int, os.popen('nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits')
                            .read().strip().split('\n')))
    memory_used = list(map(int, os.popen('nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits')
                           .read().strip().split('\n')))
    memory_free = list(map(int, os.popen('nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits')
                           .read().strip().split('\n')))
    power = list(map(float, os.popen('nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits')
                     .read().strip().split('\n')))
    power_limit = list(map(float, os.popen('nvidia-smi --query-gpu=power.limit --format=csv,noheader,nounits')
                           .read().strip().split('\n')))
    num_gpus = len(memory_total)
    assert num_gpus >= args.num_gpus, f'{num_gpus} GPU(s) detected, however {args.num_gpus} GPU(s) needed.'

    # number of GPUs that have memory in design larger than the required memory
    n_sat = np.sum(np.array(memory_total) >= args.memory)
    assert n_sat >= args.num_gpus, \
        f'Require {args.num_gpus} GPU(s) that have memory in design larger than {args.memory} MB, ' \
            f'however only {n_sat} GPU(s) satisfied.'

    # the id list of GPU(s) that are ready for the task.
    ids = list(set(map(str, np.nonzero(np.array(memory_free) >= args.memory)[0])) - set(ready_gpuids))

    return ids, list(zip(range(num_gpus), power, power_limit, memory_used, memory_total))


def main(args):
    global cmd
    assert cmd != 'python /path/to/script.py', 'Please specify the command to run in gpu_monitor.py.'
    if not args.sleep:
        assert args.dir != 'path/to/project', 'Please specify the working directory for your project.'
        assert os.path.exists(args.dir), f'The specified working directory {args.dir} does not exist.'
    ready = False
    ready_gpuids = []
    running_process = []
    _, info = gpu_info(args, ready_gpuids)
    gpu_info_format = '|{:^7d}|   {:>3.0f}W / {:>3.0f}W   | {:>5d}MiB / {:>5d}MiB |\r\n'
    i = 0
    with output(output_type='list', initial_len=len(info) + 3, interval=0) as gpu_info_print:
        while not ready:  # set waiting condition
            # exclude the ready gpuids in a new round
            ids, info = gpu_info(args, ready_gpuids)
            if len(ids) > 0:
                ready_gpuids.extend(ids)
                if len(ready_gpuids) >= args.num_gpus:  # kill the sleep processes and prepare for our task
                    for proc in running_process:
                        proc.kill()
                    # read the gpu status again and if not ready, do three trials
                    for _ in range(3):
                        time.sleep(5)
                        ready_gpuids, info = gpu_info(args)
                        if len(ready_gpuids) >= args.num_gpus:
                            os.environ["CUDA_VISIBLE_DEVICES"] = ','.join(ready_gpuids[:args.num_gpus])
                            ready = True
                            break
                        else:
                            ready_gpuids = []
                else:
                    for id in ids:
                        os.environ["CUDA_VISIBLE_DEVICES"] = id
                        proc = subprocess.Popen('exec python sleep.py', shell=True)
                        running_process.append(proc)

            i = i % 5
            gpu_info_print[0] = '|  GPU  |  Pwr:Usage/Cap  |     Memory-Usage    |\r\n'
            for j, info_j in enumerate(info, start=1):
                gpu_info_print[j] = gpu_info_format.format(*info_j)
            gpu_info_print[-2] = 'Monitoring' + '.' * (i + 1)
            gpu_info_print[-1] = 'Ready GPU ids: ' + ','.join(sorted(ready_gpuids))
            time.sleep(args.interval)
            i += 1
    start = time.time()
    if args.sleep:
        cmd = 'python sleep.py -b {}'.format(64 * args.num_gpus)
    else:
        os.chdir(os.path.expanduser(args.dir))  # change working directory
    send_mail(cmd)  # send notification via email to the user

    print('\n' + cmd)
    try:
        if args.sleep:
            subprocess.Popen('exec ' + cmd, shell=True)
            with output(output_type='list', initial_len=1, interval=0) as info_print:
                while True:
                    for i in range(3):
                        info_print[0] = 'Sleeping GPU ids: ' + ','.join(sorted(ready_gpuids)) + '.' * (i + 1)
                        time.sleep(args.interval)
        if os.system(cmd) != 0:
            raise Exception('Error encountered.')
    except Exception:
        sub = 'Error Encountered'
        content = 'Hi,\n\nWe regret to inform you that your program encountered some errors ' \
                  'during running, please check with it, Thanks.' \
                  '\n\nThis is a system generated email, do not reply.\n\n' \
                  'Nice day,\n' + socket.gethostname()
        send_mail(cmd, subject=sub, content=content)
    else:
        send_mail(cmd, finish=True, time_used=time.time() - start)


if __name__ == '__main__':
    args = parse_args()
    main(args)
