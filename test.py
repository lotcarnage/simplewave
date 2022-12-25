#! /usr/local/bin/python3
import unittest
import simplewave
import os.path


def _compare(left_hand_file_path: str, right_hand_file_path: str) -> bool:
    with open(left_hand_file_path, 'rb') as lhf, open(right_hand_file_path, 'rb') as rhf:
        lf_bytes = lhf.read()
        rf_bytes = rhf.read()
    if len(lf_bytes) != len(rf_bytes):
        return False
    for lhv, rhv in zip(lf_bytes, rf_bytes):
        if lhv != rhv:
            return False
    return True


TEST_ROOT = os.path.dirname(__file__)


class TestSimpleWave(unittest.TestCase):
    def test_fetch_monoral_wave(self):
        src = f'{TEST_ROOT}/testdata/test_monoral_48000_16bit.wav'
        actual_Fs, actual_pcm_type, actual_nch, actual_num_samples = simplewave.fetch(src)
        self.assertEqual(actual_Fs, 48000)
        self.assertEqual(actual_pcm_type, simplewave.PcmFormat.SINT16)
        self.assertEqual(actual_nch, 1)
        self.assertEqual(actual_num_samples, 240000)

    def test_fetch_stereo_wave(self):
        src = f'{TEST_ROOT}/testdata/test_stereo_44100_16bit.wav'
        actual_Fs, actual_pcm_type, actual_nch, actual_num_samples = simplewave.fetch(src)
        self.assertEqual(actual_Fs, 44100)
        self.assertEqual(actual_pcm_type, simplewave.PcmFormat.SINT16)
        self.assertEqual(actual_nch, 2)
        self.assertEqual(actual_num_samples, 328704)

    def test_load_and_save_monoral(self):
        src = f'{TEST_ROOT}/testdata/test_monoral_48000_16bit.wav'
        dst = f'{TEST_ROOT}/testdata/test_monoral_48000_16bit.out.wav'
        self.assertTrue(simplewave.save(dst, *simplewave.load(src)[:3]))
        self.assertTrue(_compare(src, dst))

    def test_load_and_save_stereo(self):
        TEST_ROOT = os.path.dirname(__file__)
        src = f'{TEST_ROOT}/testdata/test_stereo_44100_16bit.wav'
        dst = f'{TEST_ROOT}/testdata/test_stereo_44100_16bit.out.wav'
        self.assertTrue(simplewave.save(dst, *simplewave.load(src)[:3]))
        self.assertTrue(_compare(src, dst))


if __name__ == '__main__':
    unittest.main()
