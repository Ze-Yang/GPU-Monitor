# GPU Resource Monitor

This project aims at helping AI researchers put their GPU computational resource into full play.
It is common that a GPU server will be idle when on-going tasks finished, until noticed by its users.
Undoubtedly, it is troublesome for one to manually monitor the tasks on a server. To address this problem, 
we make task succession completely automatic by resource monitoring. Specifically, it can 
monitor the GPU resource iteratively and seamlessly start the pending task once GPU resource meet its 
requirement.

## Package Requirement
- python
- reprint

## Usage
`python gpu_monitor.py -m 12000 -n-gpus 8 --dir path/to/project --msg`

Args:
- `-m`: Estimated GPU memory you need (MB per GPU)
- `-n-gpus`: Number of GPU(s) you need
- `--dir`: Specify the working directory under which your task will run
- `--msg`: Notify the user via email when the task starts and finishes.

Note: 
- Remember to set the variable `cmd` in `gpu_monitor.py` with the your own command.
- To use `--msg`, please first setup the sender and receiver information in `message.py`.

## License
This project is released under the [MIT License](LICENSE).