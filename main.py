import numpy as np

from src.clusterization import seed_everything
from src.clusterization import Clusters
from src.db3_messages import BagFileParser, PointCloudConverter

seed_everything()

if __name__ == '__main__':
    bag_file = '/mnt/c/Users/knnag/Downloads/hack/cleardata/rosbag2_2023_09_04-11_56_58_0.db3'
    parser = BagFileParser(bag_file, 5)
    
    clusters = Clusters()
    bag_file_response = []
    for i, (ROWID, timestamp, data) in enumerate(parser.get_messages("/points")):
        pcd = PointCloudConverter.data2pcd(data)
        pothole_centroids = clusters.run(pcd)
        response = []
        for centroid in pothole_centroids:
            div = parser.nav_timestamps - np.array([timestamp])
            nearest_coord_idx = np.argmin(np.where(div > 0, div, np.inf))
            coordinates = parser.nav_pos[nearest_coord_idx]
            response.append({
                'coordinates': {
                    'latitude': coordinates.latitude,
                    'longitude': coordinates.longitude,
                    'altitude': coordinates.altitude
                },
                'type': 'pothole',
                'timestamp': timestamp
            })
        if len(response): bag_file_response.append(response)
    print(bag_file_response)