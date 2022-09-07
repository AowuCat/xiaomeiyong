import multiprocessing as mp

import router
import recorder_client
import player_client


if __name__ == "__main__":
    # 先启动router，router会初始化所有虚拟设备和recorder、player的服务端接口。
    p_router = mp.Process(target=router.run)
    p_recorder_client = mp.Process(target=recorder_client.run)
    p_player_client = mp.Process(target=player_client.run)

    p_router.start()
    p_recorder_client.start()
    p_player_client.start()
    p_router.join()
    p_recorder_client.join()
    p_player_client.join()
