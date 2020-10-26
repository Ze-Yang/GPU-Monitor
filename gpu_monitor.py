# author: zeyang

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
        '--dir', type=str, required=True,
        help='Specify working directory for the command.')
    parser.add_argument(
        '--msg', action='store_true',
        help='Whether to send email message to report the status of task.')
    return parser.parse_args()


def gpu_info(args):
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

    # number of GPUs that have free memory larger than the required memory
    id = np.nonzero(np.array(memory_free) >= args.memory)[0]  # the id list of GPU(s) that are ready for the task.
    ready = id.size >= args.num_gpus

    return ready, id, list(zip(range(num_gpus), power, power_limit, memory_used, memory_total))


def main(args):
    assert os.path.exists(args.dir), f'The specified working directory {args.dir} does not exist.'
    assert cmd != 'python /path/to/script.py', 'Please specify the command to run in gpu_monitor.py'
    ready, id, info = gpu_info(args)
    gpu_info_format = '|{:^7d}|   {:>3.0f}W / {:>3.0f}W   | {:>5d}MiB / {:>5d}MiB |\r\n'
    i = 0
    with output(output_type='list', initial_len=len(info) + 2, interval=0) as gpu_info_print:
        while not ready:  # set waiting condition
            ready, id, info = gpu_info(args)
            i = i % 5
            gpu_info_print[0] = '|  GPU  |  Pwr:Usage/Cap  |     Memory-Usage    |\r\n'
            for j, info_j in enumerate(info, start=1):
                gpu_info_print[j] = gpu_info_format.format(*info_j)
            gpu_info_print[-1] = 'monitoring' + '.' * (i + 1)
            time.sleep(args.interval)
            i += 1
    start = time.time()
    send_mail(cmd)  # send notification via email to the user
    os.environ["CUDA_VISIBLE_DEVICES"] = ','.join(list(map(str, id[:args.num_gpus])))
    os.chdir(os.path.expanduser(args.dir))  # change working directory
    print('\n' + cmd)
    try:
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
