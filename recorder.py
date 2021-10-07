import pyaudio
import wave
import numpy as np
import time
import multiprocessing
import os
import sys


def recorder(conn, filename):
    DEBUG = False
    channels = 1
    rate = 16000
    chunk = 480
    high_threshold = 1500
    low_threshold = 1500
    recording_stop_after_silent = 0.5
    recording_max_time = 10
    recording_min_time = 0.8
    silent_timestamp = 0
    buffered_time = 0.2

    print("[info] 收音参数：high_threshold: %d, low_threshold: %d" % (high_threshold, low_threshold))

    while True:
        try:
            frames = []
            is_recording = False
            recording_pause = False
            recording_start_timestamp = 0

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

            while True:
                if not is_recording:
                    frames.clear()
                data = None
                for i in range(0, int(rate // chunk * buffered_time)):
                    data = stream.read(chunk)
                    frames.append(data)
                volume_data = np.abs(np.frombuffer(data, dtype=np.short))
                volume_max = np.max(volume_data)
                if DEBUG:
                    print("ave: %f max: %f" % (np.average(volume_data), np.max(volume_data)))
                if volume_max > high_threshold and not is_recording:
                    is_recording = True
                    recording_start_timestamp = time.time()
                    # print("开始录音")
                if is_recording:
                    # 录音超过设定时间就结束
                    if time.time() - recording_start_timestamp > recording_max_time:
                        break
                    if volume_max < low_threshold:
                        if silent_timestamp == 0:
                            silent_timestamp = time.time()
                        elif time.time() - silent_timestamp > recording_stop_after_silent:
                            # print("录音结束")
                            break
                    else:
                        silent_timestamp = 0
                if conn.poll():
                    conn.recv()
                    recording_pause = True
                    break
            stream.stop_stream()
            stream.close()
            p.terminate()
            if recording_pause:
                while not conn.poll():
                    time.sleep(0.1)
                conn.recv()
                continue
            recording_last = time.time() - recording_start_timestamp
            if recording_last < recording_min_time:
                continue
            wf = wave.open(filename, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
            wf.close()
        except OSError as e:
            print("[error] 录音系统错误！错误原因：" + str(e))
            time.sleep(5)
            print("[info] 尝试重新启动录音系统……")


def get_noise_intensity():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=480)
    data = stream.read(8000)
    volume_data = np.abs(np.frombuffer(data, dtype=np.short))
    return np.average(volume_data), np.max(volume_data)


class Recorder:
    def __init__(self):
        self.filepath = "cache/_cache.wav"
        self._file_modify_time = 0
        if os.path.isfile(self.filepath):
            self._file_modify_time = int(os.path.getmtime(self.filepath))
        self._conn1, self._conn2 = multiprocessing.Pipe()
        self._p = multiprocessing.Process(target=recorder, args=(self._conn1, self.filepath))
        self._is_pause = False

    def run(self):
        self._p.start()

    def is_new_msg(self):
        if not os.access(self.filepath, os.R_OK) or os.path.getsize(self.filepath) == 0:
            return False
        t = int(os.path.getmtime(self.filepath))
        if t > self._file_modify_time:
            self._file_modify_time = t
            return True
        return False

    def pause(self):
        self._is_pause = not self._is_pause
        if self._is_pause:
            self._conn2.send("pause")
        else:
            self._conn2.send("pause_end")

    def is_pause(self):
        return self._is_pause
