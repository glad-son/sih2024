import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from px4_msgs.msg import ObstacleDistance
import numpy as np

class LidarToObstacleDistance(Node):
    def __init__(self):
        super().__init__('lidar_to_obstacle_distance')
        
        # Subscribe to the LiDAR topic
        self.scan_subscriber = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )
        
        # Publisher for PX4 obstacle_distance
        self.obstacle_distance_publisher = self.create_publisher(
            ObstacleDistance,
            '/fmu/in/obstacle_distance',
            10
        )
        
        # Parameters for obstacle_distance
        self.min_distance_cm = 20  # Minimum distance in cm
        self.max_distance_cm = 5000  # Maximum distance in cm
        self.num_sectors = 72  # Number of angular sectors (5° each)

    def scan_callback(self, scan: LaserScan):
        # Create ObstacleDistance message
        obstacle_msg = ObstacleDistance()
        obstacle_msg.timestamp = self.get_clock().now().to_msg().sec * 1_000_000_000
        
        # Convert scan ranges to obstacle_distance sectors
        distances = np.array(scan.ranges)
        distances = np.clip(distances * 100, self.min_distance_cm, self.max_distance_cm)  # Convert to cm
        
        # Divide distances into sectors
        sector_ranges = np.full(self.num_sectors, self.max_distance_cm, dtype=np.uint16)
        sector_angle = len(distances) // self.num_sectors
        
        for i in range(self.num_sectors):
            sector_data = distances[i * sector_angle: (i + 1) * sector_angle]
            sector_ranges[i] = np.min(sector_data) if len(sector_data) > 0 else self.max_distance_cm
        
        obstacle_msg.distances = sector_ranges
        obstacle_msg.frame = 0  # Assuming the default sensor frame
        
        # Publish the obstacle_distance message
        self.obstacle_distance_publisher.publish(obstacle_msg)
        self.get_logger().info(f'Published obstacle_distance: {obstacle_msg.distances}')

def main(args=None):
    rclpy.init(args=args)
    node = LidarToObstacleDistance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
