def run():
    import pygame
    import connection
    import time
    import queue
    pygame.init()
    pygame.mixer.init()
    pool = queue.SimpleQueue()
    is_playing_done = True
    playing_done_timestamp = 0
    SEND_DONE_WAITING = 1

    client = connection.Connection(dest=("127.0.0.1", 9528))
    while True:
        client.send_str("action&register")
        time.sleep(1)
        ack = client.get_str()[0]
        if ack == "action&ACK":
            break

    while True:
        time.sleep(0.01)

        if not pool.empty() and not pygame.mixer.music.get_busy():
            filepath = pool.get()
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            is_playing_done = False

        if pool.empty() and not pygame.mixer.music.get_busy() and not is_playing_done:
            is_playing_done = True
            playing_done_timestamp = time.time()

        msg, port = client.get_str()
        if msg is None:
            continue
        cmd = msg.split("|")
        if cmd[0].split("&")[1] == "play":
            filepath = cmd[1].split("&")[1]
            pool.put(filepath)
        elif cmd[0].split("&")[1] == "clear":
            pygame.mixer.music.stop()
            while not pool.empty():
                pool.get()
        elif cmd[0].split("&")[1] == "is_busy":
            if is_playing_done and time.time() - playing_done_timestamp > SEND_DONE_WAITING:
                client.send_str("False")
            else:
                client.send_str("True")
        elif cmd[0].split("&")[1] == "bye":
            exit(0)
