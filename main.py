from src.clusterization import seed_everything
from src.clusterization import Clusters
from src.db3_messages import BagFileParser, PointCloudConverter

if __name__ == '__main__':
    bag_file = '/mnt/c/Hack/Dataset/v1/rosbag2_2023_09_09-18_19_28_0.db3'
    parser = BagFileParser(bag_file, 5)
    
    clusters = Clusters()
    for i, (ROWID, timestamp, data) in enumerate(parser.get_messages("/points")):
        pcd = PointCloudConverter.data2pcd(data)
        clusters.run(pcd)