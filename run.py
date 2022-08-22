"""
Example cmd:

python run.py -b /media/dshin/katago/test123 -n test123
"""

import argparse
import os
import signal
import subprocess
import sys
import time


DEFAULT_NUM_THREADS = 24
DEFAULT_SELF_PLAY_CONFIG = 'cpp/configs/training/selfplay1.cfg'
DEFAULT_GATEKEEPER_CONFIG = 'cpp/configs/training/gatekeeper1.cfg'


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base-dir', required=True, help='base dir')
    parser.add_argument('-n', '--name-of-run', required=True, help='name of run (globally unique)')
    parser.add_argument('-s', '--self-play-config', default=DEFAULT_SELF_PLAY_CONFIG, help='self play cfg')
    parser.add_argument('-g', '--gatekeeper-config', default=DEFAULT_GATEKEEPER_CONFIG, help='gatekeeper cfg')
    parser.add_argument('-t', '--num-threads', default=DEFAULT_NUM_THREADS, type=int, help='num selfplay threads')
    args = parser.parse_args()

    return args


def main():
    args = get_args()
    base_dir = args.base_dir
    name_of_run = args.name_of_run
    num_threads = args.num_threads
    batch_size = 256
    use_gating = 1

    rejected_models_dir = os.path.join(base_dir, 'rejectedmodels')
    sgf_dir = os.path.join(base_dir, 'gatekeepersgf')
    test_models_dir = os.path.join(base_dir, 'modelstobetested')
    self_play_dir = os.path.join(base_dir, 'selfplay')
    models_dir = os.path.join(base_dir, 'models')
    scratch_dir = os.path.join(base_dir, 'scratch')
    self_play_config_file = args.self_play_config
    gatekeeper_config_file = args.gatekeeper_config

    training_name = f'{name_of_run}-train-s0-d0'
    log_file = 'log.txt'

    self_play_cmd = [
            'cpp/katago',
            'selfplay',
            '-output-dir', self_play_dir,
            '-models-dir', models_dir,
            '-config', self_play_config_file,
            '>>',
            log_file,
            ]

    shuffle_cmd = [
            'cd python;',
            './selfplay/shuffle_and_export_loop.sh',
            name_of_run,
            base_dir,
            scratch_dir,
            num_threads,
            batch_size,
            use_gating,
            ]

    train_cmd = [
            'cd python;',
            './selfplay/train.sh',
            base_dir,
            training_name,
            'b6c96',
            batch_size,
            'main',
            '-lr-scale 1.0'
            '>>',
            log_file,
            ]

    gatekeeper_cmd = [
            'cpp/katago',
            'gatekeeper',
            '-rejected-models-dir', rejected_models_dir,
            '-accepted-models-dir', models_dir,
            '-sgf-output-dir', sgf_dir,
            '-test-models-dir', test_models_dir,
            '-selfplay-dir', self_play_dir,
            '-config', gatekeeper_config_file,
            '>>',
            log_file,
            ]

    outshuffle_file = os.path.join(base_dir, 'logs/outshuffle.txt')
    outexport_file = os.path.join(base_dir, 'logs/outexport.txt')
    print(f'Log files to track: {log_file}, {outshuffle_file}, {outexport_file}')

    procs = []
    procs.append(make_proc(self_play_cmd))
    procs.append(make_proc(shuffle_cmd))
    procs.append(make_proc(train_cmd))
    procs.append(make_proc(gatekeeper_cmd))

    def signal_handler(sig, frame):
        print('Caught kill signal! Killing katago processes.')
        pid_str = ' '.join(map(str, [p.pid for p in procs]))
        kill_cmd = f'kill {pid_str}'
        print(kill_cmd)
        os.system(kill_cmd)
        os._exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    while True:
        time.sleep(10)


def make_proc(tokens):
    cmd = ' '.join(map(str, tokens))
    print(f'Launching: {cmd}')
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


if __name__ == '__main__':
    main()

