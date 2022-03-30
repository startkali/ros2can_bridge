import asyncio
import can 
import rclpy
import os
import sys
import time
from rclpy.node import Node
from fs_msgs.msg import CanData
from rclpy.executors import ExternalShutdownException

class CanBridge(Node):
    def __init__(self, can_dev, asyn):
        super().__init__('can_bridge'+'_'+str(can_dev)+'_'+str(asyn))
        self._bus = can.interface.Bus(channel=can_dev, bustype="socketcan")

        if asyn == 1:#It is not easy to judge by the BOOL type, which will affect the creation of nodes
            self._can_pub = self.create_publisher(
                CanData,
                can_dev+"/recv",
                10
            )
        else:
            self._can_sub = self.create_subscription(
                CanData,
                can_dev+"/send",
                self.send_callback,
                10
            )

    def send_callback(self, msg):
        sendmsg = can.Message(arbitration_id=msg.arbitration_id, \
            data=list(msg.data), is_extended_id=msg.extended)
        self._bus.send(sendmsg)

    def recv_handle(self, msg):
        recvmsg = CanData()
        recvmsg.extended = msg.is_extended_id
        recvmsg.arbitration_id= msg.arbitration_id
        recvmsg.data = msg.data

        if msg is None:
            self.get_logger().warn("can recv_handle is none.")
        self._can_pub.publish(recvmsg)

    async def can_recv(self):
        reader = can.AsyncBufferedReader()

        notifier = can.Notifier(self._bus, [self.recv_handle, reader])

        await reader.get_message()

        notifier.stop()

def can_init_dev(can_dev, can_bitrate):
    ret = os.system('sudo ip link set '+can_dev+' type can bitrate '+can_bitrate)
    if ret != 0:
        os.system('sudo ifconfig '+can_dev+' down')
    os.system('sudo ip link set '+can_dev+' type can bitrate '+can_bitrate)
    os.system('sudo ifconfig '+can_dev+' up')
    os.system('sudo ifconfig '+can_dev+' txqueuelen 65536')
    time.sleep(2)

#The dev parameter, which represents the CAN device number; the asyn parameter, which represents whether it is an asynchronous receive
def can_process(dev, asyn):

    rclpy.init()
    try:
        can_bridge = CanBridge(dev,asyn)
        if asyn == 1:
            asyncio.run(can_bridge.can_recv())
        try:
            rclpy.spin(can_bridge)
        finally:
            can_bridge.destroy_node()
    except KeyboardInterrupt:
         pass
    except ExternalShutdownException:
        sys.exit(1)
    finally:
         rclpy.try_shutdown()


