import time


def recorder(conn, filepath):
    import pyaudio
    import wave
    import numpy as np

    channels = 1
    rate = 16000
    chunk = 480
    high_threshold = 1000
    low_threshold = 1000
    recording_stop_after_silent = 0.5
    recording_max_time = 10
    recording_min_time = 0.8
    silent_timestamp = 0
    buffered_time = 0.2

    while True:
        try:
            frames = []
            is_recording = False
            recording_pause = False
            recording_start_timestamp = 0

            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

            while True:
                if conn.poll():
                    conn.recv()
                    recording_pause = True
                    break
                if not is_recording:
                    frames.clear()
                data = None
                for i in range(0, int(rate // chunk * buffered_time)):
                    data = stream.read(chunk)
                    frames.append(data)
                volume_data = np.abs(np.frombuffer(data, dtype=np.short))
                volume_max = np.max(volume_data)
                # print("ave: %f max: %f" % (np.average(volume_data), np.max(volume_data)))
                if volume_max > high_threshold and not is_recording:
                    is_recording = True
                    recording_start_timestamp = time.time()
                    # print("开始录音")
                if is_recording:
                    # 录音超过设定时间就结束
                    if time.time() - recording_start_timestamp > recording_max_time:
                        # print("录音超时结束")
                        break
                    if volume_max < low_threshold:
                        if silent_timestamp == 0:
                            silent_timestamp = time.time()
                        elif time.time() - silent_timestamp > recording_stop_after_silent:
                            # print("录音正常结束")
                            break
                    else:
                        silent_timestamp = 0
            stream.stop_stream()
            stream.close()
            p.terminate()
            if recording_pause:
                while not conn.poll():
                    time.sleep(0.01)
                conn.recv()
                continue
            recording_last = time.time() - recording_start_timestamp
            if recording_last < recording_min_time:
                continue
            wf = wave.open(filepath, 'wb')
            wf.setnchannels(channels)
            wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            conn.send("OK")
        except OSError as e:
            print("[error] 录音系统错误！错误原因：" + str(e))
            time.sleep(5)
            print("[info] 尝试重新启动录音系统……")


def run():
    import multiprocessing as mp
    import connection

    filepath = "cache/_recorder_cache.wav"
    conn, conn2 = mp.Pipe()
    p = mp.Process(target=recorder, args=(conn2, filepath))
    p.start()
    is_mute = False

    client = connection.Connection(dest=("127.0.0.1", 9527))
    while True:
        client.send_str("action&register")
        time.sleep(1)
        ack = client.get_str()[0]
        if ack == "action&ACK":
            break

    while True:
        time.sleep(0.01)

        if conn.poll():
            conn.recv()
            msg = "action&new_record|filepath&" + filepath
            client.send_str(msg)

        msg, port = client.get_str()
        if msg is None:
            continue
        cmd = msg.split("|")
        if cmd[0].split("&")[1] == "mute":
            if not is_mute:
                conn.send("1")
                is_mute = True
                # print("mute")
        elif cmd[0].split("&")[1] == "unmute":
            if is_mute:
                conn.send("1")
                is_mute = False
                # print("unmute")
        elif cmd[0].split("&")[1] == "is_mute":
            if is_mute:
                client.send_str("True")
            else:
                client.send_str("False")
        elif cmd[0].split("&")[1] == "bye":
            p.terminate()
            exit(0)
