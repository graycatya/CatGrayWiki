"""Regression checks for vector occlusion; run with numpy and shapely installed."""
import unittest

import numpy as np
from shapely.geometry import box, Polygon
from shapely.ops import unary_union

from export_all_lottie import Model, occlusion_cuts, projected


class OcclusionTests(unittest.TestCase):
    def test_crossing_planes_keep_both_visible_halves(self):
        polygons = np.array([box(0, 0, 10, 10), box(0, 0, 10, 10)], dtype=object)
        cuts = occlusion_cuts(polygons, np.array([[1, 0, -5], [0, 0, 0]]))
        visible = [p.difference(unary_union(cuts[i])) for i, p in enumerate(polygons)]
        self.assertAlmostEqual(visible[0].area, 50)
        self.assertAlmostEqual(visible[1].area, 50)
        self.assertTrue(visible[0].equals(box(5, 0, 10, 10)))
        self.assertTrue(visible[1].equals(box(0, 0, 5, 10)))
        self.assertAlmostEqual(unary_union(visible).area, 100)

    def test_parallel_and_coplanar_planes(self):
        polygons = np.array([box(0, 0, 10, 10)]*2, dtype=object)
        self.assertEqual(occlusion_cuts(polygons, np.zeros((2, 3))), {})
        cuts = occlusion_cuts(polygons, np.array([[0, 0, 1], [0, 0, 0]]))
        self.assertNotIn(0, cuts)
        self.assertAlmostEqual(unary_union(cuts[1]).area, 100)

    def test_motion_frames_preserve_projected_silhouette(self):
        # Capture the source faces at the occlusion boundary, then compare their
        # union with the exported paths. These frames previously lost whole tiles.
        import export_all_lottie as exporter
        from unittest.mock import patch
        model = Model()
        original = occlusion_cuts
        source = []

        def capture(polygons, planes):
            source[:] = [unary_union(polygons)]
            return original(polygons, planes)

        for name, frame, head_only in [('Walk_InPlace', 0, False),
                                       ('Walk_InPlace', 24, False),
                                       ('Head_Turn', 24, True)]:
            with self.subTest(name=name, frame=frame):
                animation = next(a for a in model.g['animations'] if a['name'] == name)
                with patch.object(exporter, 'occlusion_cuts', capture):
                    faces = projected(model, animation, frame, head_only)
                polygons = [Polygon(rings[0], rings[1:]) for _, _, rings in faces]
                self.assertTrue(all(p.is_valid for p in polygons))
                visible = unary_union(polygons)
                self.assertLess(source[0].difference(visible).area, .05)
                for p in polygons:
                    self.assertFalse(p.exterior.is_ccw)
                    self.assertTrue(all(r.is_ccw for r in p.interiors))


if __name__ == '__main__':
    unittest.main()
