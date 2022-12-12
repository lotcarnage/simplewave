""" Wave File read and write module
"""

import wave
import numpy


def fetch(input_wave_file_path: str) -> tuple[int, int, int, int]:
    """ Fetch Wave file header

    : arg input_wave_file_path: Fetch target Wave file path.
    """
    wave_reader = wave.open(input_wave_file_path, 'rb')
    Fs = wave_reader.getframerate()
    nch = wave_reader.getnchannels()
    depth = wave_reader.getsampwidth()
    num_samples = wave_reader.getnframes()
    wave_reader.close()
    return Fs, nch, depth, num_samples


def load(input_wave_file_path: str) -> tuple[numpy.ndarray, int, int]:
    """ Load Wave file

    : arg input_wave_file_path: Load target Wave file path.
    """
    wave_reader = wave.open(input_wave_file_path, 'rb')
    Fs = wave_reader.getframerate()
    nch = wave_reader.getnchannels()
    depth = wave_reader.getsampwidth()
    num_samples = wave_reader.getnframes()
    data = wave_reader.readframes(num_samples)
    if depth == 2:
        dt = numpy.int16
    elif depth == 4:
        dt = numpy.int32
    lpcms = numpy.frombuffer(data, dtype=dt)
    wave_reader.close()
    return lpcms, Fs, nch


def save(output_wave_file_path: str, lpcm: numpy.ndarray, Fs: int) -> None:
    """ Save Wave file

    : arg output_wave_file_path: Save target Wave file path.
    """
    wave_writer = wave.open(output_wave_file_path, 'wb')
    wave_writer.setframerate(Fs)
    wave_writer.setnchannels(1)
    if type(lpcm[0]) == numpy.int16:
        depth = 2
    wave_writer.setsampwidth(depth)
    wave_writer.writeframes(lpcm.tobytes())
    wave_writer.close()
    return None


def cli_entry():
    import argparse
    argment_parser = argparse.ArgumentParser()
    argment_parser.add_argument("input_wave_file_path", type=str)
    args = argment_parser.parse_args()
    wave_info = fetch(args.input_wave_file_path)
    print(f'{wave_info[0]},{wave_info[1]},{wave_info[2]},{wave_info[3]}')
    return 0


if __name__ == '__main__':
    exit(cli_entry())
