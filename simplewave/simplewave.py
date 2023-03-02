""" Wave File read and write module
"""

import struct
from enum import Enum


class _ValueType(Enum):
    SINT8 = 0
    SINT16 = 1
    SINT24 = 2
    SINT32 = 3
    UINT8 = 4
    UINT16 = 5
    UINT24 = 6
    UINT32 = 7
    FLOAT32 = 8


class PcmFormat(Enum):
    SINT8 = 0
    SINT16 = 1
    SINT24 = 2
    SINT32 = 3
    FLOAT32 = 4


def _split_chunk(bin: bytes, chunk_name: bytes):
    if bin[:4] != chunk_name:
        return None
    chunk_size = struct.unpack('<i', bin[4:8])[0]
    return bin[8:8 + chunk_size], bin[8 + chunk_size:]


def _convert_pack_format(type_array: list[_ValueType]):
    format_table = ['b', 'h', '', 'i', 'B', 'H', '', 'I', 'f']
    size_table = [1, 2, 3, 4, 1, 2, 3, 4, 4]
    byte_length = sum([size_table[t.value] for t in type_array])
    pack_format = f"<{''.join([format_table[t.value] for t in type_array])}"
    return pack_format, byte_length


def _read_structure(bin: bytes, structure_defs: list[tuple[str, _ValueType]]):
    type_array = [field_def[1] for field_def in structure_defs]
    pack_format, byte_length = _convert_pack_format(type_array)
    values = struct.unpack(pack_format, bin[:byte_length])
    structure = {field_def[0]: value for field_def, value in zip(structure_defs, values)}
    return structure, bin[byte_length:]


def _read_array_sint8(bin: bytes, num_elements: int):
    u8_array = [bin[i] for i in range(0, num_elements, 1)]
    s8_array = [v if v < (2**7) else v - (2**8) for v in u8_array]
    return s8_array


def _read_array_sint16(bin: bytes, num_elements: int):
    u16_array = [bin[i] + bin[i + 1] * (2**8) for i in range(0, num_elements * 2, 2)]
    s16_array = [v if v < (2**15) else v - (2**16) for v in u16_array]
    return s16_array


def _read_array_sint24(bin: bytes, num_elements: int):
    u24_array = [bin[i] + bin[i + 1] * (2**8) + bin[i + 2] * (2**16) for i in range(0, num_elements * 3, 3)]
    s24_array = [v if v < (2**23) else v - (2**24) for v in u24_array]
    return s24_array


def _read_array_sint32(bin: bytes, num_elements: int):
    u32_array = [bin[i] + bin[i + 1] * (2**8) + bin[i + 2] * (2**16) + bin[i + 3] * (2**24) for i in range(0, num_elements * 4, 4)]
    s32_array = [v if v < (2**31) else v - (2**32) for v in u32_array]
    return s32_array


def _serialize_sint8_array(values: list[int]):
    serialized = bytearray(len(values) * 1)
    for i, v in zip(range(0, len(values) * 1, 1), values):
        v_bytes = struct.pack('i', v)
        serialized[i + 0] = v_bytes[0]
    return serialized


def _serialize_sint16_array(values: list[int]):
    serialized = bytearray(len(values) * 2)
    for i, v in zip(range(0, len(values) * 2, 2), values):
        v_bytes = struct.pack('i', v)
        serialized[i + 0] = v_bytes[0]
        serialized[i + 1] = v_bytes[1]
    return serialized


def _serialize_sint24_array(values: list[int]):
    serialized = bytearray(len(values) * 3)
    for i, v in zip(range(0, len(values) * 3, 3), values):
        v_bytes = struct.pack('i', v)
        serialized[i + 0] = v_bytes[0]
        serialized[i + 1] = v_bytes[1]
        serialized[i + 2] = v_bytes[2]
    return serialized


def _serialize_sint32_array(values: list[int]):
    serialized = bytearray(len(values) * 4)
    for i, v in zip(range(0, len(values) * 4, 4), values):
        v_bytes = struct.pack('i', v)
        serialized[i + 0] = v_bytes[0]
        serialized[i + 1] = v_bytes[1]
        serialized[i + 2] = v_bytes[2]
        serialized[i + 3] = v_bytes[3]
    return serialized


def _read_array(bin: bytes, value_type: _ValueType, num_elements: int):
    if value_type == _ValueType.SINT8:
        return _read_array_sint8(bin, num_elements)
    elif value_type == _ValueType.SINT16:
        return _read_array_sint16(bin, num_elements)
    elif value_type == _ValueType.SINT24:
        return _read_array_sint24(bin, num_elements)
    elif value_type == _ValueType.SINT32:
        return _read_array_sint32(bin, num_elements)
    return None


def _read_wave(bin: bytes) -> tuple[list[list[int or float]], int, PcmFormat, int] or None:
    fmt_chunk_content = [
        ('encoding', _ValueType.UINT16),
        ('num_channels', _ValueType.UINT16),
        ('sampling_rate', _ValueType.UINT32),
        ('byte_par_sec', _ValueType.UINT32),
        ('frame_size', _ValueType.UINT16),
        ('sample_depth', _ValueType.UINT16)
    ]
    int_pcm_type_table = [None, PcmFormat.SINT8, PcmFormat.SINT16, PcmFormat.SINT24, PcmFormat.SINT32]
    riff_chunk, _ = _split_chunk(bin, b'RIFF')
    if riff_chunk is None:
        return None
    if riff_chunk[:4] != b'WAVE':
        return None
    maybe_fmt_chunk = riff_chunk[4:]
    fmt_chunk, maybe_data = _split_chunk(maybe_fmt_chunk, b'fmt ')
    if fmt_chunk is None:
        return None
    fmt, _ = _read_structure(fmt_chunk, fmt_chunk_content)
    if fmt['encoding'] not in [0x0001, 0x0003]:
        return None
    if fmt['encoding'] == 0x0003:
        fmt_sample_byte = 4
        pcm_type = PcmFormat.FLOAT32
        value_type = _ValueType.FLOAT32
    elif fmt['encoding'] == 0x0001:
        fmt_sample_byte = fmt['sample_depth'] // 8
        pcm_type = int_pcm_type_table[fmt_sample_byte]
        if fmt_sample_byte == 1:
            value_type = _ValueType.SINT8
        elif fmt_sample_byte == 2:
            value_type = _ValueType.SINT16
        elif fmt_sample_byte == 3:
            value_type = _ValueType.SINT24
        elif fmt_sample_byte == 4:
            value_type = _ValueType.SINT32
        else:
            return None

    data_chunk, _ = _split_chunk(maybe_data, b'data')
    num_elements = len(data_chunk) // fmt_sample_byte
    interleaved_pcms = _read_array(data_chunk, value_type, num_elements)
    if interleaved_pcms is None:
        return None
    pcms = []
    for ch in range(fmt['num_channels']):
        pcms.append(interleaved_pcms[ch::fmt['num_channels']])
    return pcms, fmt['sampling_rate'], pcm_type, fmt['num_channels']


def _interleave_pcms(pcms: list[list[int or float]]) -> list[int or float]:
    frames = [frame for frame in zip(*pcms)]
    interleaved_pcms = []
    for frame in frames:
        interleaved_pcms.extend(frame)
    return interleaved_pcms


def _serialize_wave(pcms: list[list[int or float]], sampling_rate: int, pcm_type: PcmFormat) -> bytes or None:
    sample_byte_length_table = [1, 2, 3, 4, 4]
    nch = len(pcms)
    num_samples = len(pcms[0])
    sample_byte_length = sample_byte_length_table[pcm_type.value]
    data_body_length = nch * num_samples * sample_byte_length
    data_chunk_length = 8 + data_body_length
    fmt__body_length = 16
    fmt__chunk_length = 8 + fmt__body_length
    riff_body_length = len(b'WAVE') + fmt__chunk_length + data_chunk_length
    riff_chunk_length = 8 + riff_body_length
    riff_header = struct.pack('4si', b'RIFF', riff_body_length)
    fmt__header = struct.pack('4si', b'fmt ', fmt__body_length)
    data_header = struct.pack('4si', b'data', data_body_length)

    fmt_encoding = 0x0003 if pcm_type == PcmFormat.FLOAT32 else 0x0001
    fmt_num_channels = nch
    fmt_sampling_rate = sampling_rate
    fmt_byte_par_sec = sampling_rate * nch * sample_byte_length
    fmt_frame_size = nch * sample_byte_length
    fmt_sample_bit_depth = sample_byte_length * 8
    fmt__body = struct.pack('hhiihh', fmt_encoding, fmt_num_channels, fmt_sampling_rate, fmt_byte_par_sec, fmt_frame_size, fmt_sample_bit_depth)

    interleaved_pcms = _interleave_pcms(pcms)
    if pcm_type.value == PcmFormat.SINT8.value:
        data_body = _serialize_sint8_array(interleaved_pcms)
    elif pcm_type.value == PcmFormat.SINT16.value:
        data_body = _serialize_sint16_array(interleaved_pcms)
    elif pcm_type.value == PcmFormat.SINT24.value:
        data_body = _serialize_sint24_array(interleaved_pcms)
    elif pcm_type.value == PcmFormat.SINT32.value:
        data_body = _serialize_sint32_array(interleaved_pcms)
    else:
        print(pcm_type.value, PcmFormat.SINT16)

    wave_file_bytes = riff_header + b'WAVE' + fmt__header + fmt__body + data_header + data_body
    if len(wave_file_bytes) != riff_chunk_length:
        return None
    return wave_file_bytes


def fetch(input_wave_file_path: str) -> tuple[int, PcmFormat, int, int]:
    """ Fetch Wave file header

    : arg input_wave_file_path: Fetch target Wave file path.
    """

    with open(input_wave_file_path, 'rb') as wave_file:
        wave_image = wave_file.read()
    pcms, sampling_rate, pcm_type, nch = _read_wave(wave_image)
    num_samples = len(pcms[0])
    return sampling_rate, pcm_type, nch, num_samples,


def load(input_wave_file_path: str) -> tuple[list[list[int or float]], int, PcmFormat, int] or None:
    """ Waveファイルの読み込み

    指定したWaveファイルを読み込み、チャンネル毎のPCM配列とサンプリングレート、
    PCMフォーマット、チャンネル数のタプルを返します。
    失敗した場合はNoneを返します。

    PCMのデータ構造は、PCM配列をチャンネル数分持つ二次元配列として定義しています。
    チャンネル数を得るには、配列のトップレベルに対してlen()を呼び出してください。
    サンプル数を得るには、いずれかのチャンネルのPCM配列に対してlen()を呼び出してください。
    具体的には以下の通りです。

    ```
    pcms, Fs, pcm_format, nch = simplewave.load('test.wav')
    len(pcms) # チャンネル数
    len(pcms[0]) # サンプル数
    ```

    : param str input_wave_file_path: 読み込み対象のWaveファイルパス
    : rtype: tuple[list[list[int or float]], int, PcmType, int] or None
    : return:
        読み込めたPCMのチャンネル毎の配列、サンプリングレート、PCMフォーマット、チャンネル数をまとめたタプル。
        失敗した場合はNoneを返す。
    """
    with open(input_wave_file_path, 'rb') as wave_file:
        wave_image = wave_file.read()
    pcms, sampling_rate, pcm_type, nch = _read_wave(wave_image)
    return pcms, sampling_rate, pcm_type, nch


def save(output_wave_file_path: str, pcms: list[list[int or float]], sampling_rate: int, pcm_type: PcmFormat) -> bool:
    """ Waveファイルへの保存

    指定したWaveファイル名でPCMを保存します。

    PCMのデータ構造は、PCM配列をチャンネル数分持つ二次元配列として定義しています。
    定義上、pcmsの要素数がチャンネル数になるため、本関数は保存するチャンネル数を引数に持ちません。
    同様に、PCM配列の要素数がそのままサンプル数になるため、本関数は保存するサンプル数を引数に持ちません。

    pcm_typeにはファイルへ保存する際のPCMフォーマットを指定してください。
    pcmsの実際の型が何であるかによらず、本関数は指定されたフォーマットに従い、
    pcmsを一切変換せずにファイルへ書き込みます。

    : param str output_wave_file_path: 保存先のWaveファイルパス
    : param list[list[int or float]] pcms: 保存するPCMデータ
    : param int sampling_rate: 保存時のサンプリングレート
    : param PcmType pcm_type: 保存時のサンプルフォーマット
    : rtype: bool
    : return: 保存に成功した場合はTrueを、失敗した場合はFalseを返します。
    """
    wave_bytes = _serialize_wave(pcms, sampling_rate, pcm_type)
    if wave_bytes is None:
        return False
    with open(output_wave_file_path, 'wb') as wave_file:
        wave_file.write(wave_bytes)

    return True


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
