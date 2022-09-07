def play_command(_player, _recorder, _tts, _cmd):
    _recorder.mute()
    cmd_list = _cmd.split("|")
    for i in cmd_list:
        cmd = i.split("&")
        if cmd[0] == "text":
            filepath = _tts.run(cmd[1])
            _player.play(filepath)
        elif cmd[0] == "wav":
            _player.play(cmd[1])
        elif cmd[0] == "clear":
            _player.clear()
        else:
            raise (SyntaxError, "崩了")


def play_text(_player, _recorder, _tts, _text):
    _recorder.mute()
    _filepath = _tts.run(_text)
    _player.play(_filepath)


def run():
    VERSION = "XiaoMeiYong Alpha Version 2022-04-12 20:34"

    import time
    import winsound
    import devices
    from log import Log
    log = Log()

    STT_ACTIVE_TIME = 30
    stt_network_active_timestamp = 0

    virt_devices = devices.VirtDevices()
    recorder = devices.Recorder()
    player = devices.Player()
    ui = devices.UiServer()
    while True:
        recorder.update()
        player.update()
        if recorder.is_online() and player.is_online():
            time.sleep(1)  # 确保client处理ACK完成
            player.play(virt_devices.tts.run("初始化完成"))
            break
        time.sleep(0.05)
    log.write(VERSION)
    log.write("初始化完成")

    while True:
        filepath = recorder.update()
        if filepath is not None:
            if time.time() - stt_network_active_timestamp > STT_ACTIVE_TIME:
                is_keyword = virt_devices.stt_local.is_keyword(filepath)
                if is_keyword:
                    log.write("检测到关键词")
                    stt_network_active_timestamp = time.time()
            if time.time() - stt_network_active_timestamp < STT_ACTIVE_TIME:
                if virt_devices.stt_network.is_available():
                    text = virt_devices.stt_network.run(filepath)
                else:
                    log.write("stt_network不可用", level="warn")
                    text = virt_devices.stt_local.run(filepath)
                if text is not None and len(text) != 0:
                    log.write("语音识别结果：%s" % text)
                    ans = virt_devices.core.run(text)
                    if ans is not None and len(ans) != 0:
                        log.write("小没用回答：%s" % ans)
                        play_command(player, recorder, virt_devices.tts, ans)
                        stt_network_active_timestamp = time.time()

        ans = virt_devices.core.update()
        if ans is not None and len(ans) != 0:
            log.write("小没用触发：%s" % ans)
            play_command(player, recorder, virt_devices.tts, ans)
            stt_network_active_timestamp = time.time()

        msg, port = ui.update()
        if msg is not None:
            try:
                ans = ""
                if msg == "hello":
                    ans = "hello"
                elif msg.startswith("fake_input&"):
                    input_msg = msg.split("&")[1]
                    log.write('%s模拟输入"%s"' % (str(port), input_msg))
                    ans = virt_devices.core.run(input_msg)
                    if ans is not None and len(ans) != 0:
                        log.write("小没用回答：%s" % ans)
                        play_command(player, recorder, virt_devices.tts, ans)
                elif msg.startswith("fake_input_no_play&"):
                    input_msg = msg.split("&")[1]
                    log.write('%s模拟输入(不播放)"%s"' % (str(port), input_msg))
                    ans = virt_devices.core.run(input_msg)
                    if ans is not None and len(ans) != 0:
                        log.write("小没用回答：%s" % ans)
                elif msg.startswith("just_play&"):
                    input_msg = msg.split("&")[1]
                    log.write('%s直接播放语音"%s"' % (str(port), input_msg))
                    filepath = virt_devices.tts.run(input_msg)
                    winsound.PlaySound(filepath, winsound.SND_FILENAME)
                elif msg.startswith("play_with_no_recorder&"):
                    input_msg = msg.split("&")[1]
                    log.write('%s播放语音"%s"' % (str(port), input_msg))
                    play_text(player, recorder, virt_devices.tts, input_msg)
                elif msg == "kill":
                    recorder.kill()
                    player.kill()
                    ui.reply("bye")
                    log.write("程序退出")
                    exit(0)
                else:
                    ans = "未知命令"
                ui.reply(ans)
            except Exception as e:
                print(e)
                log.write('%s消息处理报错，消息："%s"' % (str(port), msg))

        is_mute = recorder.is_mute()
        is_busy = player.is_busy()
        if is_mute and not is_busy:
            recorder.unmute()
        if not is_mute and is_busy:
            recorder.mute()

        time.sleep(0.01)
