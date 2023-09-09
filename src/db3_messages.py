import ros2_numpy
from sensor_msgs.msg import PointCloud2
import open3d as o3d

import sqlite3
from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

class BagFileParser():
    def __init__(self, bag_file):
        self.conn = sqlite3.connect(bag_file)
        self.cursor = self.conn.cursor()

        ## create a message type map
        topics_data = self.cursor.execute("SELECT id, name, type FROM topics").fetchall()
        self.topic_type = {name_of:type_of for id_of,name_of,type_of in topics_data}
        self.topic_id = {name_of:id_of for id_of,name_of,type_of in topics_data}
        self.topic_msg_message = {name_of:get_message(type_of) for id_of,name_of,type_of in topics_data}

    def __del__(self):
        self.conn.close()

    # Return [(timestamp0, message0), (timestamp1, message1), ...]
    def get_messages(self, topic_name):
        
        topic_id = self.topic_id[topic_name]
        # Get from the db
        self.cursor.execute("SELECT timestamp, data FROM messages WHERE topic_id = {} ORDER BY timestamp".format(topic_id))
        # rows = self.cursor.execute("PRAGMA table_info(messages)").fetchall()
        # Deserialise all and timestamp them
        while True:
            row = self.cursor.fetchmany(1)
            if len(row):
                timestamp, data = row[0]
                yield (timestamp, deserialize_message(data, self.topic_msg_message[topic_name]))
            else:
                break

class PointCloud2Converter:
    def __init__(self):    
        self.pc_npy = None
        self.pcd = o3d.geometry.PointCloud()

    def callback_pcl(self, messages):
        for mess in messages:
            self.pc_npy  = ros2_numpy.point_cloud2.point_cloud2_to_array(mess)['xyz']
            self.pcd.points = o3d.utility.Vector3dVector(self.pc_npy)
            o3d.io.write_point_cloud("points_all.pcd", self.pcd)

if __name__ == "__main__":
    
    bag_file = '/mnt/c/Hack/Dataset/1/rosbag2_2023_09_04-11_56_58_0.db3'

    parser = BagFileParser(bag_file)

    import time
    
    t1 = time.time()
    
    for i, (timestamp, msg) in enumerate(parser.get_messages("/points")):
        pass
    
    print(time.time() - t1)
    # conv = PointCloud2Converter()
    # conv.callback_pcl(messages)