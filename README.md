# Tile Generator
To use ML and mood to generate tile

1. Optimize Tile moving with optical flow & bounce back Physics (Bill) [Next weed]
2. `interactive_pattern_numbered.py`return a dict with tile point positions [Done!]
3. Tile Maths & **Algorithms** Description (Zhilong) [Next Week]
4. Color Postpocessing using OF (Zhilong) [Next Weekend]
5. Sub-partition (Zhilong) [Next Week]
6. Cam -> mood -> word -> BGM Generation [AI Pipeline] (Zhilong) [...]
7. Cam -> mood -> word -> BGM Generation [AI Pipeline] (Bill) [Done!]
8. Check `py5.push_matrix()` (Zhilong)
9. 二叉树 data structure(Zhilong)
10. multiprocessing (Bill) [Next week]

# Run Process
```command
python data_generation.py
python draw_grid.py 
python draw_tile.py 
``` 

## Step 2 format
```python
tile_dict = {
    "1": [(x1, y1), (x2, y2), (x3, y3)],
    "2": [(x1, y1), (x2, y2), (x3, y3)],
}

of_dict = {
    "(x1, y1)": (a1, a2),
    "(x2, y2)": (a1, a2),
}

# 多的在外头
for i in tile_dict.keys(): 
    for j in of_dict.keys():
        pass
```