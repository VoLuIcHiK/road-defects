import time
import sqlite3
import ros2_numpy
import open3d as o3d


from rosidl_runtime_py.utilities import get_message
from rclpy.serialization import deserialize_message

class BagFileParser():
    def __init__(self, bag_file, every_n_frame):
        self.conn = sqlite3.connect(bag_file)
        self.cursor = self.conn.cursor()
        self.every_n_frame = every_n_frame
        
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
        
        query = "SELECT timestamp, data FROM messages WHERE topic_id = {} AND ROWID % {} = 0 ORDER BY timestamp"
        
        # Get from the db
        self.cursor.execute(query.format(topic_id, self.every_n_frame))

        # rows = self.cursor.execute("PRAGMA table_info(messages)").fetchall()
        # Deserialise all and timestamp them
        while True:
            row = self.cursor.fetchmany(1)
            if len(row):
                for timestamp, data in row:
                    data = deserialize_message(data, self.topic_msg_message[topic_name])
                    yield (timestamp, data)
                    
            else:
                break

class PointCloudConverter:

    @staticmethod
    def write2pcd(messages):
        for mess in messages:
            pcd = o3d.geometry.PointCloud()
            pc_npy  = ros2_numpy.point_cloud2.point_cloud2_to_array(mess)['xyz']
            pcd.points = o3d.utility.Vector3dVector(pc_npy)
            o3d.io.write_point_cloud("points_all.pcd", pcd)
    
    @staticmethod
    def msg2cloud(msg):
        pc_npy  = ros2_numpy.point_cloud2.point_cloud2_to_array(msg)['xyz']
        pcd = o3d.geometry.PointCloud()
        pcd.points = o3d.utility.Vector3dVector(pc_npy)
        return pcd

if __name__ == "__main__":
    bag_file = '/mnt/c/Hack/Dataset/1/rosbag2_2023_09_04-11_56_58_0.db3'

    parser = BagFileParser(bag_file, 5)
    
    t1 = time.time()
    for i, (timestamp, msg) in enumerate(parser.get_messages("/points")):
        pass
    print(i, time.time() - t1)