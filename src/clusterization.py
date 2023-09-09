import open3d as o3d
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.spatial import distance_matrix
import time
import random
import os

def seed_everything(seed=42):
    os.environ['PYTHONHASHSEED'] = str(seed)
    random.seed(seed)
    np.random.seed(seed)

class Clusters:
    def __init__(self) -> None:
        pass

if __name__ == "__main__":
    
    # t1 = time.time()
    
    pcd = o3d.io.read_point_cloud('project/points_1.pcd')
    
    # VISUALIZE THE POINT CLOUD
    # o3d.visualization.draw_geometries([pcd])
    
    t1 = time.time()
    # VOXEL GRID AND DISTANCE DOWNSAMPLING
    print(f"Points before downsampling: {len(pcd.points)} ")
    downpcd = pcd.voxel_down_sample(voxel_size = 0.00001)
    # downpcd = pcd
    distance_filter = distance_matrix(np.array([[0, 0, 0]]), np.asarray(downpcd.points))[0]
    downpcd = downpcd.select_by_index(np.where(distance_filter < 20)[0])
    print(f"Points after downsampling: {len(downpcd.points)}")
    o3d.visualization.draw_geometries([downpcd])
    
    # RANSAC
    plane_model, inliers = downpcd.segment_plane(distance_threshold = 0.05, ransac_n = 3, num_iterations = 10000)
    plane_cloud = downpcd.select_by_index(inliers)
    non_plane_cloud = downpcd.select_by_index(inliers, invert = True)
    
    # HEIGHT FILTERING
    np_non_plane_cloud = np.asarray(non_plane_cloud.points)
    height_filter = np.where(np_non_plane_cloud @ plane_model[:-1] + plane_model[-1] < 0)[0]
    non_plane_cloud = non_plane_cloud.select_by_index(height_filter)
    
    plane_cloud.paint_uniform_color([1, 0, 0])
    non_plane_cloud.paint_uniform_color([0.6, 0.6, 0.6])
    
    o3d.visualization.draw_geometries([plane_cloud, non_plane_cloud])

    # CLUSTRIZATION
    clustring_points = non_plane_cloud
    with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug) as cm:
        labels = np.array(clustring_points.cluster_dbscan(eps=1.5, min_points=10, print_progress=True))

    max_label = labels.max()
    print(f"point cloud has {max_label + 1} clusters")
    colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
    colors[labels < 0] = 0
    clustring_points.colors = o3d.utility.Vector3dVector(colors[:, :3])
    o3d.visualization.draw_geometries([clustring_points])
    
    # DETECTION BOXES
    bounding_boxes = []
    inds =  pd.Series(range(len(labels))).groupby(labels, sort = False).apply(list).tolist()
    
    for i in range(len(inds)):
        cluster = clustring_points.select_by_index(inds[i])
        bb = cluster.get_axis_aligned_bounding_box()
        bb.color = (1,0,0)
        bounding_boxes.append(bb)

    visuals = []
    visuals.append(clustring_points)
    visuals.extend(bounding_boxes)
    o3d.visualization.draw_geometries(visuals)
    
    print(time.time() - t1)
    