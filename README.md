# GPU Resource Monitor

[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/Ze-Yang/GPU-Monitor.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/Ze-Yang/GPU-Monitor/context:python)

This project aims at helping AI researchers put their GPU computational resource into full play.
It is common that a GPU server will be idle when on-going tasks finished, until noticed by its users.
Undoubtedly, it is troublesome for one to manually monitor the tasks on a server. To address this problem, 
we make task succession completely automatic by resource monitoring. Specifically, it can 
monitor the GPU resource iteratively and seamlessly start the pending task once GPU resource meet its 
requirement. You will receive email notification upon task starting and finished. Additionally, if
your program encounters errors during running, you will get informed to fix it in time.

## New features:
- support occupying gpus one by one and once reach the specified number, your task will be executed automatically. 
(30/07/2021)

## Package Requirement
- python >= 3.6
- reprint

## Usage
`python gpu_monitor.py -m 12000 -n-gpus 8 --dir path/to/project --msg`

Args:
- `-m`: Estimated GPU memory you need (MB per GPU)
- `-n-gpus`: Number of GPU(s) you need
- `--dir`: Specify the working directory under which your task will run
- `--msg`: Notify the user via email when the task starts and finishes.
- `--sleep`: Run a infinite loop programme to temporarily claim the specified number of GPUs.

Note: 
- Remember to set the variable `cmd` in `gpu_monitor.py` with the your own command.
- To use `--msg`, please first setup the sender and receiver information in `message.py`.
- Running with `--sleep` will claim the specified number of GPUs temporarily until your actual task is ready.
In this mode, you are not required to specify `--dir`.

## License
This project is released under the [MIT License](LICENSE).