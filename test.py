#! /usr/local/bin/python3
from simplewave import fetch
import os.path


def _check_fetch(test_data_file_path: str, expected_Fs: int, expected_nch: int, expected_byte_depth: int, expected_num_samples: int) -> bool:
    actual_Fs, actual_nch, actual_byte_depth, actual_num_samples = fetch(test_data_file_path)
    is_succeeded = True
    if actual_Fs != expected_Fs:
        print(f'[FAILED] Fs: expected {expected_Fs}, actual {actual_Fs}')
        is_succeeded = False
    if actual_nch != expected_nch:
        print(f'[FAILED] nch: expected {expected_nch}, actual {actual_nch}')
        is_succeeded = False
    if actual_byte_depth != expected_byte_depth:
        print(f'[FAILED] byte_depth: expected {expected_byte_depth}, actual {actual_byte_depth}')
        is_succeeded = False
    if actual_num_samples != expected_num_samples:
        print(f'[FAILED] num_samples: expected {expected_num_samples}, actual {actual_num_samples}')
        is_succeeded = False
    return is_succeeded


def _main():
    TEST_ROOT = os.path.dirname(__file__)
    is_succeeded = True
    if not _check_fetch(f'{TEST_ROOT}/testdata/test_monoral_48000_16bit.wav', 48000, 1, 2, 240000):
        print('[FAILED] Fetch Test Case 1')
        is_succeeded = False
    if not _check_fetch(f'{TEST_ROOT}/testdata/test_stereo_44100_16bit.wav', 44100, 2, 2, 328704):
        print('[FAILED] Fetch Test Case 1')
        is_succeeded = False
    return 0 if is_succeeded else 1


if __name__ == '__main__':
    exit(_main())
