quadtree = [
    {
        "depth": 0,
        "box": (0, 0, 8, 8),
        "color": 140,
        "children": [
            {
                "depth": 1,
                "box": (0, 0, 4, 4),
                "color": 115,
                "children": [
                    {"depth": 2, "box": (0, 0, 2, 2), "color": 100, "children": []},
                    {"depth": 2, "box": (2, 0, 4, 2), "color": 110, "children": []},
                    {"depth": 2, "box": (0, 2, 2, 4), "color": 120, "children": []},
                    {"depth": 2, "box": (2, 2, 4, 4), "color": 130, "children": []}
                ]
            },
            {
                "depth": 1,
                "box": (4, 0, 8, 4),
                "color": 215,
                "children": [
                    # Аналогичное деление
                ]
            },
            # Остальные квадранты
        ]
    }
]
