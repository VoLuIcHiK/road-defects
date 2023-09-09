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

def unit_vector(vector):
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.rad2deg(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))

class Clusters:
    def __init__(self) -> None:
        pass
    
    def _ransac(
            self,
            pcd,
            distance_threshold=0.05,
            ransac_n=3,
            num_iterations=10000
    ):
        
        angle = 100
        while angle > 30 and angle < 150:
            plane_model, inliers = pcd.segment_plane(
                distance_threshold = distance_threshold, 
                ransac_n = ransac_n, 
                num_iterations = num_iterations
            )
            normal = np.array(plane_model[:-1])
            angle = angle_between(normal, np.array([0., 0., -1.]))
            if angle > 30 and angle < 150:
                pcd = pcd.select_by_index(inliers, invert = True)
        
        plane_cloud = pcd.select_by_index(inliers)
        non_plane_cloud = pcd.select_by_index(inliers, invert = True)
        return plane_cloud, non_plane_cloud, plane_model
    
    def _height_filter(self, pcd, plane_model):
        np_pcd = np.asarray(pcd.points)
        height_filter = np.where(np_pcd @ plane_model[:-1] + plane_model[-1] < 0)[0]
        return pcd.select_by_index(height_filter)
    
    def _distance_filter(self, pcd, radius=20):
        distance_filter = distance_matrix(np.array([[0, 0, 0]]), np.asarray(pcd.points))[0]
        return pcd.select_by_index(np.where(distance_filter < radius)[0])
    
    def run(
        self,
        # pcd,
        voxel_size=0.00001,
        distance_threshold=0.05,
        ransac_n=3,
        num_iterations=10000,
        eps=1.5, 
        min_points=10,
        print_progress=True,
    ):
    
        pcd = o3d.io.read_point_cloud('points.pcd')
        
        # VISUALIZE THE POINT CLOUD
        o3d.visualization.draw_geometries([pcd])
        
        t1 = time.time()
        # VOXEL GRID AND DISTANCE DOWNSAMPLING
        print(f"Points before downsampling: {len(pcd.points)} ")
        downpcd = pcd.voxel_down_sample(voxel_size = voxel_size)
        downpcd = self._distance_filter(downpcd, radius=20)
        print(f"Points after downsampling: {len(downpcd.points)}")
        o3d.visualization.draw_geometries([downpcd])
        
        # RANSAC
        plane_cloud, non_plane_cloud, plane_model = self._ransac(downpcd, distance_threshold, ransac_n, num_iterations)

        # HEIGHT FILTERING
        non_plane_cloud = self._height_filter(non_plane_cloud, plane_model)
        
        plane_cloud.paint_uniform_color([1, 0, 0])
        non_plane_cloud.paint_uniform_color([0.6, 0.6, 0.6])
        
        o3d.visualization.draw_geometries([plane_cloud, non_plane_cloud])

        # CLUSTRIZATION
        clustring_points = non_plane_cloud
        with o3d.utility.VerbosityContextManager(o3d.utility.VerbosityLevel.Debug) as cm:
            labels = np.array(clustring_points.cluster_dbscan(eps=eps, min_points=min_points, print_progress=print_progress))

        max_label = labels.max()
        print(f"point cloud has {max_label + 1} clusters")
        print(len(labels))
        print(labels)
        colors = plt.get_cmap("tab20")(labels / (max_label if max_label > 0 else 1))
        colors[labels < 0] = 0
        clustring_points.colors = o3d.utility.Vector3dVector(colors[:, :3])
        o3d.visualization.draw_geometries([clustring_points])
        
        # DETECTION BOXES
        bounding_boxes = []
        # if len(labels_without_outliers) > 0:
        inds = pd.Series(range(len(labels))).groupby(labels, sort = True).apply(list).tolist()
        # else:
            # inds = [] 
        for i in range(1, len(inds)):
            cluster = clustring_points.select_by_index(inds[i])
            bb = cluster.get_axis_aligned_bounding_box()
            bb.color = (1,0,0)
            bounding_boxes.append(bb)

        visuals = []
        visuals.append(clustring_points)
        downpcd.paint_uniform_color([0.6, 0.6, 0.6])
        visuals.append(downpcd)
        visuals.extend(bounding_boxes)
        o3d.visualization.draw_geometries(visuals)
        
        print(time.time() - t1)        

if __name__ == "__main__":
    
    cluster = Clusters()
    cluster.run()