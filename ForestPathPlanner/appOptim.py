# import numpy as np
# import matplotlib.pyplot as plt
# from PIL import Image
# import time
# import pathfinder # pyright: ignore[reportMissingImports] # My C++ based path finding module
# from threshold import IsoGrayThresh

# def main():
#     # --- Configuration ---
#     IMAGE_PATH = 'img3.jpeg'  # <--- CHANGE THIS TO WHATEVER IMAGE YOU WANT I SWEAR I WILL ADD A NEATER METHOD FOR INPUT LATER 
#     START_PIXEL = (0, 0) # <--- WHATEVER START PIXEL YOU WANT AS LONG AS ITS WITHIN THE DIMENSIONS OF THE IMAGE 
    
#     # --- Load Image ---
#     try:
#         # Open the image and convert to grayscale
#         img = plt.imread(IMAGE_PATH)
#         img = IsoGrayThresh(img)
#         img = Image.fromarray(img).convert('L')
#         img_array = np.array(img)
        
#         # Define target based on image dimensions
#         rows, cols = img_array.shape
#         target_pixel = (rows - 1, cols - 1)

#     except FileNotFoundError:
#         print(f"Error: Image not found at {IMAGE_PATH}")
#         # Create a dummy image for demonstration if not found
#         print("Creating a dummy gradient image for demonstration.")
#         rows, cols = 400, 600
#         target_pixel = (rows - 1, cols - 1)
#         x = np.linspace(0, 255, cols)
#         y = np.linspace(0, 255, rows)
#         xv, yv = np.meshgrid(x, y)
#         img_array = (xv + yv).astype(np.uint8)
#         img = Image.fromarray(img_array)


#     # ---
#     # THE HEAVY LIFTING IS DONE HERE!
#     # ---
#     # 1. Create an instance of our C++ class
#     path_calculator = pathfinder.OptimalPathing()

#     # 2. Call the C++ function to compute the path
#     time1 = time.time()
#     print("Computing path using C++ module...")
#     # The C++ function takes the numpy array and the start/target tuples
#     shortest_path = path_calculator.compute_path(img_array, START_PIXEL, target_pixel)
#     print("Path computation complete.")
#     print(f"in {time.time()-time1} seconds")
#     if not shortest_path:
#         print("No path was found.")
#         return

#     # --- Visualization ---
#     print(f"Path found with {len(shortest_path)} points. Visualizing...")
#     x_coords, y_coords = zip(*shortest_path)  # Extract x, y coordinates

#     plt.figure(figsize=(15, 10))
#     plt.imshow(img, cmap='gray')
#     # Note: plt.plot uses (x, y) which corresponds to (col, row)
#     plt.plot(y_coords, x_coords, color='cyan', linewidth=2.5, label='Optimal Path')
    
#     # Mark start and end points
#     plt.scatter([START_PIXEL[1]], [START_PIXEL[0]], color='lime', s=100, zorder=5, label='Start')
#     plt.scatter([target_pixel[1]], [target_pixel[0]], color='red', s=100, zorder=5, label='Target')

#     plt.title('Optimal Path found by C++ Module')
#     plt.legend()
#     plt.show()

# if __name__ == '__main__':
#     main()


# import numpy as np
# from PIL import Image, ImageDraw
# import time
# import pathfinder  # pyright: ignore[reportMissingImports] # Your C++ module
# from threshold import IsoGrayThresh

# def main_with_return(image=None, start=(0, 0), end=None):
#     """
#     Compute optimal path using ForestPathPlanner and return results as a dict.
#     This is designed for Streamlit integration.
#     """

#     # --- Load image ---
#     if image is None:
#         image_path = 'img3.jpeg'
#         image = Image.open(image_path)
#     img_array = np.array(image.convert('RGB'))
    
#     # Apply threshold from threshold.py
#     binary_img = IsoGrayThresh(img_array)

#     rows, cols = binary_img.shape
#     if end is None:
#         end = (rows-1, cols-1)

#     # --- Path calculation ---
#     path_calculator = pathfinder.OptimalPathing()
#     time1 = time.time()
#     shortest_path = path_calculator.compute_path(binary_img, start, end)
#     elapsed_time = time.time() - time1

#     if not shortest_path:
#         shortest_path = []

#     # --- Visualization ---
#     img_copy = image.convert('RGB')
#     draw = ImageDraw.Draw(img_copy)
#     if shortest_path:
#         # Draw path on image
#         draw.line([(y, x) for x, y in shortest_path], fill='cyan', width=3)

#     # Dummy metrics (replace with your own if available)
#     total_cost = np.sum(binary_img)
#     green_coverage = np.mean(binary_img > 0) * 100
#     idle_coverage = 100 - green_coverage

#     return {
#         'path_image': img_copy,
#         'path_length': len(shortest_path),
#         'total_cost': total_cost,
#         'green_coverage': green_coverage,
#         'idle_coverage': idle_coverage,
#         'elapsed_time': elapsed_time
#     }

# # Optional: allow running standalone for testing
# if __name__ == '__main__':
#     result = main_with_return()
#     result['path_image'].show()


import numpy as np
from PIL import Image, ImageDraw
import time
import importlib.util
import sys
import os
from threshold import IsoGrayThresh

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))
pathfinder_path = os.path.join(current_dir, 'pathfinder.cp311-win_amd64.pyd')

# Try to load the pathfinder module
pathfinder = None
try:
    spec = importlib.util.spec_from_file_location("pathfinder", pathfinder_path)
    if spec is not None and spec.loader is not None:
        pathfinder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pathfinder)
        print("Pathfinder module loaded successfully")
    else:
        print("Could not create module spec for pathfinder")
except Exception as e:
    print(f"Error loading pathfinder module: {e}")
    pathfinder = None

def main_with_return(image=None, start=(0, 0), end=None):
    """
    Compute optimal path using ForestPathPlanner and return results as a dict.
    This is designed for Streamlit integration.
    """
    # Check if pathfinder module is available
    if pathfinder is None:
        raise ImportError("Pathfinder module is not available. Please check the installation.")

    # --- Load image ---
    if image is None:
        image_path = 'img3.jpeg'
        image = Image.open(image_path)
    img_array = np.array(image.convert('RGB'))
    
    # Apply threshold from threshold.py
    binary_img = IsoGrayThresh(img_array)

    rows, cols = binary_img.shape
    if end is None:
        end = (rows-1, cols-1)

    # Ensure start and end are integer tuples
    start = (int(start[0]), int(start[1]))
    end = (int(end[0]), int(end[1]))
    # Ensure binary_img is int32
    binary_img = binary_img.astype(np.int32)

    # --- Path calculation ---
    time1 = time.time()
    # Create an instance of the OptimalPathing class and call the correct function
    path_calculator = pathfinder.OptimalPathing()
    shortest_path = path_calculator.compute_path(binary_img, start, end)
    elapsed_time = time.time() - time1

    if not shortest_path:
        shortest_path = []

    # --- Visualization ---
    img_copy = image.convert('RGB')
    draw = ImageDraw.Draw(img_copy)
    if shortest_path:
        # Draw path on image
        draw.line([(y, x) for x, y in shortest_path], fill='cyan', width=3)

    # Dummy metrics (replace with your own if available)
    total_cost = np.sum(binary_img)
    green_coverage = np.mean(binary_img > 0) * 100
    idle_coverage = 100 - green_coverage

    return {
        'path_image': img_copy,
        'path_length': len(shortest_path),
        'total_cost': total_cost,
        'green_coverage': green_coverage,
        'idle_coverage': idle_coverage,
        'elapsed_time': elapsed_time
    }

# Optional: allow running standalone for testing
if __name__ == '__main__':
    result = main_with_return()
    result['path_image'].show()
