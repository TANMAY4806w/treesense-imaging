import base64
import heapq
import io
import math
import time
from typing import List, Tuple
import cv2
import numpy as np
from PIL import Image

from backend.app.schemas.pathfinding import PathResponse

class TerrainPathfinderService:
    def compute_optimal_path(
        self,
        image_bytes: bytes,
        start_pt: Tuple[int, int],
        end_pt: Tuple[int, int]
    ) -> PathResponse:
        t0 = time.time()
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        w, h = pil_img.size
        img_np = np.array(pil_img)

        # Vegetation thresholding for cost map
        # High green = high obstacle cost; open ground = lower cost
        g_channel = img_np[:, :, 1].astype(np.float32)
        r_channel = img_np[:, :, 0].astype(np.float32)
        b_channel = img_np[:, :, 2].astype(np.float32)

        # Simple green index mask
        green_mask = (g_channel > r_channel) & (g_channel > b_channel)
        green_cov = round((np.sum(green_mask) / (w * h)) * 100.0, 2)
        idle_cov = round(100.0 - green_cov, 2)

        # Build grid cost: normal ground = 1.0, dense canopy = 15.0
        # For fast path computation on 4K imagery, downsample grid to max 400x400 if needed
        scale = 1.0
        max_dim = max(w, h)
        if max_dim > 400:
            scale = 400.0 / max_dim
            grid_w, grid_h = int(w * scale), int(h * scale)
            small_mask = cv2.resize(green_mask.astype(np.uint8), (grid_w, grid_h), interpolation=cv2.INTER_NEAREST)
        else:
            grid_w, grid_h = w, h
            small_mask = green_mask.astype(np.uint8)

        cost_grid = np.where(small_mask > 0, 15.0, 1.0)

        # Scale start and end points to grid
        sx, sy = int(start_pt[0] * scale), int(start_pt[1] * scale)
        ex, ey = int(end_pt[0] * scale), int(end_pt[1] * scale)

        sx = max(0, min(grid_w - 1, sx))
        sy = max(0, min(grid_h - 1, sy))
        ex = max(0, min(grid_w - 1, ex))
        ey = max(0, min(grid_h - 1, ey))

        # A* Pathfinding (8 directions)
        path_grid, total_cost = self._a_star(cost_grid, (sx, sy), (ex, ey))

        # Rescale waypoints back to original resolution
        waypoints: List[Tuple[int, int]] = []
        if path_grid:
            for gx, gy in path_grid:
                ox = int(gx / scale)
                oy = int(gy / scale)
                waypoints.append((ox, oy))

        # Render path on image
        annotated = img_np.copy()
        if len(waypoints) > 1:
            pts = np.array(waypoints, np.int32).reshape((-1, 1, 2))
            cv2.polylines(annotated, [pts], isClosed=False, color=(0, 255, 255), thickness=3, lineType=cv2.LINE_AA)

        # Draw Start (Green) and End (Red) circles
        cv2.circle(annotated, start_pt, 8, (0, 255, 0), -1)
        cv2.circle(annotated, end_pt, 8, (255, 0, 0), -1)

        # Base64 encoding
        _, buffer = cv2.imencode(".jpg", cv2.cvtColor(annotated, cv2.COLOR_RGB2BGR))
        path_b64 = f"data:image/jpeg;base64,{base64.b64encode(buffer).decode('utf-8')}"

        elapsed = round((time.time() - t0) * 1000.0, 2)
        path_len = round(float(len(waypoints)), 2)

        return PathResponse(
            success=True,
            path_found=len(waypoints) > 0,
            path_length_px=path_len,
            total_cost=round(float(total_cost), 2),
            elapsed_time_ms=elapsed,
            green_coverage_pct=green_cov,
            idle_coverage_pct=idle_cov,
            waypoints=waypoints,
            path_image=path_b64
        )

    def _a_star(self, cost_grid: np.ndarray, start: Tuple[int, int], end: Tuple[int, int]):
        h, w = cost_grid.shape
        sx, sy = start
        ex, ey = end

        # 8 directions: dx, dy, step_cost
        dirs = [
            (1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
            (1, 1, math.sqrt(2)), (-1, 1, math.sqrt(2)),
            (1, -1, math.sqrt(2)), (-1, -1, math.sqrt(2))
        ]

        def heuristic(x, y):
            return math.hypot(x - ex, y - ey)

        # Open set heap: (f_score, g_score, x, y)
        open_set = []
        heapq.heappush(open_set, (heuristic(sx, sy), 0.0, sx, sy))

        came_from = {}
        g_scores = { (sx, sy): 0.0 }
        closed_set = set()

        while open_set:
            f, g, cx, cy = heapq.heappop(open_set)

            if (cx, cy) == (ex, ey):
                # Reconstruct path
                path = [(cx, cy)]
                while (cx, cy) in came_from:
                    cx, cy = came_from[(cx, cy)]
                    path.append((cx, cy))
                path.reverse()
                return path, g

            if (cx, cy) in closed_set:
                continue
            closed_set.add((cx, cy))

            for dx, dy, step_weight in dirs:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < w and 0 <= ny < h:
                    if (nx, ny) in closed_set:
                        continue
                    edge_cost = cost_grid[ny, nx] * step_weight
                    tentative_g = g + edge_cost
                    if tentative_g < g_scores.get((nx, ny), float('inf')):
                        came_from[(nx, ny)] = (cx, cy)
                        g_scores[(nx, ny)] = tentative_g
                        f_score = tentative_g + heuristic(nx, ny)
                        heapq.heappush(open_set, (f_score, tentative_g, nx, ny))

        return [], 0.0

pathfinder_service = TerrainPathfinderService()
