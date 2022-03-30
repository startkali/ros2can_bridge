import can_bridge
from multiprocessing import Process

def main():
    can_bridge.can_init_dev("can0", "500000")
    process0asyn = Process(target=can_bridge.can_process, args=("can0", 1))
    process0 = Process(target=can_bridge.can_process, args=("can0", 0))
    can_bridge.can_init_dev("can1", "500000")
    process1asyn = Process(target=can_bridge.can_process, args=("can1", 1))
    process1 = Process(target=can_bridge.can_process, args=("can1", 0))

    process0asyn.start()
    process0.start()
    process1asyn.start()
    process1.start()

    process0asyn.join()
    process0.join()
    process1asyn.join()
    process1.join()


main()