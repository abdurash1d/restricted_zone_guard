from zones.zones import point_in_polygon


def test_point_in_polygon_square():
    square = [(0, 0), (10, 0), (10, 10), (0, 10)]
    assert point_in_polygon((5, 5), square) is True
    assert point_in_polygon((0, 0), square) is True  # vertex
    assert point_in_polygon((10, 5), square) is True  # edge
    assert point_in_polygon((11, 5), square) is False


def test_point_in_polygon_triangle():
    tri = [(0, 0), (10, 0), (5, 10)]
    assert point_in_polygon((5, 5), tri) is True
    assert point_in_polygon((8, 9), tri) is False
