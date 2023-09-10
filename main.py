from src.clusterization import seed_everything
from src.clusterization import Clusters
from src.db3_messages import BagFileParser, PointCloudConverter

if __name__ == '__main__':
    bag_file = '/mnt/c/Users/knnag/Downloads/hack/cleardata/rosbag2_2023_09_04-11_56_58_0.db3'
    parser = BagFileParser(bag_file, 5)
    
    clusters = Clusters()
    for i, (ROWID, timestamp, data) in enumerate(parser.get_messages("/points")):
        pcd = PointCloudConverter.data2pcd(data)
        clusters.run(pcd)