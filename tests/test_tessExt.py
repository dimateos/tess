from tess import Container
from unittest import TestCase
from pytest import raises as assertException

# NOTE: there is no vector class imported for the tests, avoid deciding over Blender / numpy vectors / etc
#       however it is recommended using one instead of working with raw tuples and lists

class TestCase_ext(TestCase):
    """" General asserting utilities """

    def assertListAlmostEqual(self, first, second, places=None, msg=None, delta=None):
        """" Utility function to compare a pair of lists such as a vector """
        self.assertEqual(len(first), len(second), msg=msg)
        for v1, v2 in zip(first, second):
            self.assertAlmostEqual(v1, v2, places=places, msg=msg, delta=delta)

    def assertNestedListAlmostEqual(self, first, second, places=None, msg=None, delta=None):
        """" Utility function to compare list of vectors (single nesting) """
        self.assertEqual(len(first), len(second), msg=msg)
        for l1, l2 in zip(first, second):
            self.assertEqual(len(l1), len(l2), msg=msg)
            for v1, v2 in zip(l1, l2):
                self.assertAlmostEqual(v1, v2, places=places, msg=msg, delta=delta)

class TestCase_cubicCell():
    """" Cubic cell asserting utilities """

    def get_cubic_cell(self, r=0.5, c=(0,0,0)):
        """" return a cubic cell of side r centered at c """
        bb = [ [cc-r for cc in c], [cc+r for cc in c] ]
        cont = Container(points=[c], limits=bb)
        return cont[0]

    def assert_cubic_cell_basic(self, cell):
        id =                   0
        radius =               0.0

        self.assertEqual(id, cell.id)
        self.assertAlmostEqual(radius, cell.radius)

    def assert_cubic_cell_geo(self, cell):
        face_freq_table =      [0, 0, 0, 0, 6]
        face_orders =          [4, 4, 4, 4, 4, 4]
        face_vertices =        [[1, 3, 2, 0], [1, 5, 7, 3], [1, 0, 4, 5], [2, 6, 4, 0], [2, 3, 7, 6], [4, 6, 7, 5]]
        neighbors =            [-5, -2, -3, -1, -4, -6]
        normals =              [(-0.0, -0.0, -1.0), (1.0, -0.0, 0.0), (0.0, -1.0, 0.0), (-1.0, -0.0, -0.0), (0.0, 1.0, -0.0), (-0.0, 0.0, 1.0)]
        number_of_edges =      12.0
        number_of_faces =      6.0
        vertex_orders =        [3, 3, 3, 3, 3, 3, 3, 3]

        cell_face_freq_table = cell.face_freq_table()
        cell_face_orders = cell.face_orders()
        cell_face_vertices = cell.face_vertices()
        cell_neighbors = cell.neighbors()
        cell_normals = cell.normals()
        cell_number_of_edges = cell.number_of_edges()
        cell_number_of_faces = cell.number_of_faces()
        cell_vertex_orders = cell.vertex_orders()
        self.assertListAlmostEqual(face_freq_table, cell_face_freq_table)
        self.assertListAlmostEqual(face_orders, cell_face_orders)
        self.assertNestedListAlmostEqual(face_vertices, cell_face_vertices)
        self.assertListAlmostEqual(neighbors, cell_neighbors)
        self.assertNestedListAlmostEqual(normals, cell_normals)
        self.assertAlmostEqual(number_of_edges, cell_number_of_edges)
        self.assertAlmostEqual(number_of_faces, cell_number_of_faces)
        self.assertListAlmostEqual(vertex_orders, cell_vertex_orders)

    def assert_cubic_cell_scale(self, cell, r=0.5):
        # 1D relation on the edge dimension tranlates to 2D and 3D
        rel = r / 0.5
        rel2 = rel * rel
        rel3 = rel2 * rel

        face_areas =           [1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
        face_areas =           [ a*rel2 for a in face_areas ]
        face_perimeters =      [4.0, 4.0, 4.0, 4.0, 4.0, 4.0]
        face_perimeters =      [ p*rel for p in face_perimeters ]

        max_radius_squared =   3.0 * rel2
        surface_area =         6.0 * rel2
        total_edge_distance =  12.0 * rel
        volume =               1.0 * rel3

        cell_face_areas = cell.face_areas()
        cell_face_perimeters = cell.face_perimeters()
        cell_max_radius_squared = cell.max_radius_squared()
        cell_surface_area = cell.surface_area()
        cell_total_edge_distance = cell.total_edge_distance()
        cell_volume = cell.volume()
        self.assertListAlmostEqual(face_areas, cell_face_areas)
        self.assertListAlmostEqual(face_perimeters, cell_face_perimeters)
        self.assertAlmostEqual(max_radius_squared, cell_max_radius_squared)
        self.assertAlmostEqual(surface_area, cell_surface_area)
        self.assertAlmostEqual(total_edge_distance, cell_total_edge_distance)
        self.assertAlmostEqual(volume, cell_volume)

    def assert_cubic_cell_pos(self, cell, disp=0, r=0.5, c=(0,0,0)):
        pos =                  c
        centroid_local =       (0.0, 0.0, 0.0) # relative to c, same as vertices_local
        vertices_local =       [(-r, -r, -r), (r, -r, -r), (-r, r, -r), (r, r, -r), (-r, -r, r), (r, -r, r), (-r, r, r), (r, r, r)]

        centroid =             c
        vertices = [tuple( map(sum, zip(vert, c)) ) for vert in vertices_local]

        pos = tuple(x+disp for x in pos)
        centroid = tuple(x+disp for x in centroid)
        vertices = [tuple(x+disp for x in vert) for vert in vertices]

        cell_pos = cell.pos
        cell_centroid = cell.centroid()
        cell_centroid_local = cell.centroid_local()
        cell_vertices = cell.vertices()
        cell_vertices_local = cell.vertices_local()
        self.assertListAlmostEqual(pos, cell_pos)
        self.assertListAlmostEqual(centroid, cell_centroid)
        self.assertListAlmostEqual(centroid_local, cell_centroid_local)
        self.assertNestedListAlmostEqual(vertices, cell_vertices)
        self.assertNestedListAlmostEqual(vertices_local, cell_vertices_local)

class TestCase_container():
    """" Container asserting utilities """

    def get_cubic_cont(self, r=0.5, c=(0,0,0), walls=[]):
        """" return a cubic container of side r centered at c """
        bb = [ [cc-r for cc in c], [cc+r for cc in c] ]
        cont = Container(points=[c], limits=bb, walls=walls)
        return cont

    def assert_cubic_cell_geo(self, cont):
        blocks =               (1, 1, 1)
        limits =               ((-0.5, -0.5, -0.5), (0.5, 0.5, 0.5))

        cont_blocks = cont.blocks
        cont_limits = cont.get_limits()
        self.assertListAlmostEqual(blocks, cont_blocks)
        self.assertNestedListAlmostEqual(limits, cont_limits)


class TestCell(TestCase_ext, TestCase_cubicCell):
    def test_methods(self):
        """ Simple checks for the Cell method bindings """
        cell_positions = [[1., 1., 1.], [2., 2., 2.]]
        cell_radii = [0.2, 0.1]

        cells = Container(
            cell_positions, radii=cell_radii, limits=(3,3,3), periodic=False
        )

        for i, cell in enumerate(cells):
            assert cell.id == i
            self.assertListAlmostEqual(cell.pos, cell_positions[i])
            self.assertAlmostEqual(cell.radius, cell_radii[i])
            assert cell.volume() > 0.0
            assert cell.max_radius_squared() > 0.0
            assert cell.total_edge_distance() > 0.0
            assert cell.surface_area() > 0.0
            assert cell.number_of_faces() > 0
            assert cell.number_of_edges() > 0
            assert len(cell.centroid()) == 3
            assert len(cell.vertex_orders()) > 0
            assert len(cell.vertices()) > 0
            assert len(cell.face_areas()) > 0
            assert len(cell.face_orders()) > 0
            assert len(cell.face_freq_table()) > 0
            assert len(cell.face_vertices()) > 0
            assert len(cell.face_perimeters()) > 0
            assert len(cell.normals()) > 0
            assert len(cell.neighbors()) > 0
            assert str(cell) == repr(cell) == f"<Cell {i}>"

    def test_methods_data(self):
        # unit cube centered at the origin
        cell = self.get_cubic_cell()

        self.assert_cubic_cell_basic(cell)
        self.assert_cubic_cell_geo(cell)
        self.assert_cubic_cell_scale(cell)
        self.assert_cubic_cell_pos(cell)

    def test_methods_data_offcentered(self):
        # off centered cube
        r=0.5
        c=(1,1,1)
        cell = self.get_cubic_cell(r,c)

        self.assert_cubic_cell_basic(cell)
        self.assert_cubic_cell_geo(cell)
        self.assert_cubic_cell_scale(cell)
        self.assert_cubic_cell_pos(cell, 0, r, c)

    def test_methods_data_nonunit(self):
        # non unit cube
        r=2
        c=(1,1,1)
        cell = self.get_cubic_cell(r,c)

        self.assert_cubic_cell_basic(cell)
        self.assert_cubic_cell_geo(cell)
        self.assert_cubic_cell_pos(cell, 0, r, c)
        self.assert_cubic_cell_scale(cell, r)

        # Scale for non unit cube should fail
        with assertException(Exception):
            self.assert_cubic_cell_scale(cell)

    def test_container_bounds(self):
        r=0.5
        c=(0,0,0)
        bb = [ [cc-r for cc in c], [cc+r for cc in c] ]

        # point inside
        p_out= ( cc+r*0.99 for cc in c )
        cont = Container(points=[p_out], limits=bb)

        # point outside should raise except for now
        p_out= ( cc+r*5 for cc in c )
        with assertException(Exception):
            cont = Container(points=[p_out], limits=bb)

        # point outside should raise except for now
        p_out= ( cc+r for cc in c )
        with assertException(Exception):
            cont = Container(points=[p_out], limits=bb)


    def test_translate(self):
        # unit cube centered at the origin
        cell = self.get_cubic_cell()

        # translate some amount in all direction
        disp = 10
        cell.translate(disp, disp, disp)
        self.assert_cubic_cell_basic(cell)
        self.assert_cubic_cell_geo(cell)
        self.assert_cubic_cell_scale(cell)
        self.assert_cubic_cell_pos(cell, disp)

        # cell was translated so original pos test should fail
        with assertException(Exception):
            self.assert_cubic_cell_pos(cell)

        # test negative and each axis
        cell.translate(-disp, 0, 0)
        cell.translate(0, -disp, 0)
        cell.translate(0, 0, -disp)
        self.assert_cubic_cell_basic(cell)
        self.assert_cubic_cell_geo(cell)
        self.assert_cubic_cell_scale(cell)
        self.assert_cubic_cell_pos(cell, 0)


    def test_cut_plane_halfY(self):
        # unit cube centered at the origin
        cell = self.get_cubic_cell()

        # cut though the middle (remove positive Y halfspace)
        cell.cut_plane(0,1,0,0)
        self.assert_cubic_cell_basic(cell)

        # some neighbour wall index should be 0 referencing the cut plane
        # faces indices may get swapped too?, it is the case here
        with assertException(Exception):
            self.assert_cubic_cell_geo(cell)

        # cut so should have half the volume etc
        with assertException(Exception):
            self.assert_cubic_cell_scale(cell)

        # cut so should have shifted centroid and non positive Y vertices
        with assertException(Exception):
            self.assert_cubic_cell_pos(cell)

        # check proper magnitudes (some)
        volume =               0.5
        surface_area =         4.0
        total_edge_distance =  10.0
        cell_volume = cell.volume()
        cell_surface_area = cell.surface_area()
        cell_total_edge_distance = cell.total_edge_distance()
        self.assertAlmostEqual(volume, cell_volume)
        self.assertAlmostEqual(surface_area, cell_surface_area)
        self.assertAlmostEqual(total_edge_distance, cell_total_edge_distance)

        # check centroid and vertices (locals are the same, the cell was positioned at the origin)
        pos =                  (0.0, 0.0, 0.0)
        centroid =             (0.0, -0.25, 0.0)
        vertices =             [(-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (-0.5, 0.0, -0.5), (0.5, 0.0, -0.5), (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (-0.5, 0.0, 0.5), (0.5, 0.0, 0.5)]
        cell_pos = cell.pos
        cell_centroid = cell.centroid()
        cell_vertices = cell.vertices()
        self.assertListAlmostEqual(pos, cell_pos)
        self.assertListAlmostEqual(centroid, cell_centroid)
        self.assertListAlmostEqual(centroid, cell.centroid_local())
        self.assertNestedListAlmostEqual(vertices, cell_vertices)
        self.assertNestedListAlmostEqual(vertices, cell.vertices_local())

    def test_cut_plane_atDist(self):
        # cube with side of length 2 centered at the origin
        r=1
        cell = self.get_cubic_cell(r)

        # cut though Y=0.5
        if True:
            d = 0.5
            cell.cut_plane(0,d,0, d*d)
            self.assert_cubic_cell_basic(cell)
            # self.assert_cubic_cell_geo(cell)
            # self.assert_cubic_cell_pos(cell, 0, r)

            self.assertAlmostEqual(6, cell.volume())
            with assertException(Exception):
                self.assert_cubic_cell_scale(cell, r)

        # cube with side of length 10
        if True:
            # cut at Y=1 leaves 6/10 of the volume
            r=5
            cell = self.get_cubic_cell(r)
            d = 1
            cell.cut_plane(0,d,0, d*d)
            # self.assert_cubic_cell_pos(cell, 0, r)
            # self.assert_cubic_cell_scale(cell, r)
            self.assertAlmostEqual(600, cell.volume())

            # cut at Y=2 leaves 7/10 of the volume
            cell = self.get_cubic_cell(r)
            d = 2
            cell.cut_plane(0,d,0, d*d)
            self.assertAlmostEqual(700, cell.volume())

            # cut at Y=3 leaves 8/10 of the volume
            cell = self.get_cubic_cell(r)
            d = 3
            cell.cut_plane(0,d,0, d*d)
            self.assertAlmostEqual(800, cell.volume())

        # cut at a controlled distance, not just the tip of the vector
        if True:
            # cut at Y=2.5 by reducing vector lenSq dist
            cell = self.get_cubic_cell(r)
            d = 5
            cell.cut_plane(0,d,0, d*d *0.5)
            self.assertAlmostEqual(750, cell.volume())

            # cut at Y=4 by augmenting vector lenSq dist
            cell = self.get_cubic_cell(r)
            d = 2
            cell.cut_plane(0,d,0, d*d *2.0)
            self.assertAlmostEqual(900, cell.volume())

            # NORMALIZED vector cut at Y=2.5
            # NOTE: the API of cut_plane is confusing, will probably change n_lenSq to distance relative to normal length
            #       e.g. that is the case of n being a normalized vector, otherwise the user has to pass the lenSq
            cell = self.get_cubic_cell(r)
            d = 2.5
            cell.cut_plane(0,1,0, d)
            self.assertAlmostEqual(750, cell.volume())

            # NORMALIZED vector cut at NEGATIVE Y=-2.5
            cell = self.get_cubic_cell(r)
            d = -2.5
            cell.cut_plane(0,1,0, d)
            self.assertAlmostEqual(250, cell.volume())

    def test_cut_plane_diagEdge(self):
        def test_common_cut(cell, r):

            # additional face
            self.assertAlmostEqual(7, cell.number_of_faces())
            with assertException(Exception):
                self.assert_cubic_cell_geo(cell)

            # Cut a corner, so less volume etc
            self.assertAlmostEqual(7 * r*r*r, cell.volume())
            with assertException(Exception):
                self.assert_cubic_cell_scale(cell, r)

            # Cut a corner, so different vertices
            self.assertEqual(10, len(cell.vertices()))
            with assertException(Exception):
                self.assert_cubic_cell_pos(cell, 0, r)

        # cube with side of length 2 centered at the origin
        r=1
        cell = self.get_cubic_cell(r)
        # remove one edge of the cell with a single plane cut using a particle positioned at the edge
        cell.cut_plane_particle(r,r,0)
        test_common_cut(cell, r)
        # equivalent cut at half the distance to the edge
        cell = self.get_cubic_cell(r)
        cell.cut_plane(r,r,0, 0.5 * (r*r + r*r))
        test_common_cut(cell, r)

        # same but with cube with side of length 20 centered at the origin
        r=10
        cell = self.get_cubic_cell(r)
        cell.cut_plane_particle(r,r,0)
        test_common_cut(cell, r)
        cell = self.get_cubic_cell(r)
        # cell.cut_plane(r,r,0, 0.5 * (r*r + r*r))
        # rsq is the modulus of the vector, so careful when not normalizing (should be working with a vector class)
        r2 = r * 0.5
        cell.cut_plane(r2,r2,0, (r2*r2 + r2*r2)) # basically writting manually cell.cut_plane(vx,vy,vz, v.length2)
        test_common_cut(cell, r)

    def test_cut_plane_diagVert(self):
        # cube with side of length 2 centered at the origin
        r=1

        # cut out a vert
        cell = self.get_cubic_cell(r)
        cell.cut_plane_particle(r,r,r)
        # self.assert_cubic_cell_geo(cell)
        self.assertAlmostEqual(7, cell.number_of_faces())
        self.assertEqual(10, len(cell.vertices()))
        vol1 = cell.volume()

        # cut out a vert but using the same plane
        cell = self.get_cubic_cell(r)
        rsq = r*r + r*r + r*r
        cell.cut_plane(r,r,r, 0.5 * rsq)
        self.assertAlmostEqual(7, cell.number_of_faces())
        self.assertEqual(10, len(cell.vertices()))
        vol2 = cell.volume()
        self.assertAlmostEqual(vol1, vol2)

        # cut out in half the volume
        cell = self.get_cubic_cell(r)
        cell.cut_plane(r,r,r, 0)
        # self.assert_cubic_cell_basic(cell)
        # self.assert_cubic_cell_geo(cell)
        # self.assert_cubic_cell_scale(cell)
        # self.assert_cubic_cell_pos(cell)
        self.assertAlmostEqual(7, cell.number_of_faces())   # bisect of opposite vertices keeps adds a face
        self.assertEqual(10, len(cell.vertices()))
        self.assertAlmostEqual(4.0, cell.volume())          # but it does half the volume

    def test_cut_plane_index(self):
        # unit cube centered at the origin
        cell = self.get_cubic_cell()

        cell.cut_plane(0,1,0,0)
        assert 0 in cell.neighbors()
        cell.cut_plane(1,0,0,0, -10)
        assert -10 in cell.neighbors()
        self.assertAlmostEqual(0.25, cell.volume())


    def test_cut_particle(self):
        # unit cube centered at the origin
        r = 0.5
        cell = self.get_cubic_cell(r)

        # set a particle in the middle of the top face
        cell.cut_plane_particle(0,r,0)

        # diff neighborhood
        with assertException(Exception):
            self.assert_cubic_cell_geo(cell)

        self.assertAlmostEqual(0.75, cell.volume())
        with assertException(Exception):
            self.assert_cubic_cell_scale(cell, r)

        self.assertEqual(8, len(cell.vertices()))
        with assertException(Exception):
            self.assert_cubic_cell_pos(cell, 0, r)

    def test_cut_particle_octahedron(self):
        # unit cube centered at the origin
        r = 2
        cell = self.get_cubic_cell(r)

        # cut with a particle at each vertex
        rr = r * 0.5
        cell.cut_plane_particle(rr,rr,rr)
        cell.cut_plane_particle(-rr,rr,rr)
        cell.cut_plane_particle(rr,-rr,rr)
        cell.cut_plane_particle(-rr,-rr,rr)
        cell.cut_plane_particle(rr,rr,-rr)
        cell.cut_plane_particle(-rr,rr,-rr)
        cell.cut_plane_particle(rr,-rr,-rr)
        cell.cut_plane_particle(-rr,-rr,-rr)

        self.assertAlmostEqual(8.0, cell.number_of_faces())
        with assertException(Exception):
            self.assert_cubic_cell_geo(cell)

        self.assertLess(cell.volume(), 8)
        with assertException(Exception):
            self.assert_cubic_cell_scale(cell, r)

        self.assertEqual(6, len(cell.vertices()))
        with assertException(Exception):
            self.assert_cubic_cell_pos(cell, 0, r)

    def test_cut_particle_exception(self):
        # unit cube centered at the origin
        cell = self.get_cubic_cell()

        try:
            # actually raises execpt unline cut_plane
            cell.cut_plane_particle(0,0,0)
            raise self.failureException("Cell deleted entirely")
        except: pass

        # no influence
        cell.cut_plane_particle(0,2,0)
        self.assert_cubic_cell_basic(cell)
        self.assert_cubic_cell_geo(cell)
        self.assert_cubic_cell_scale(cell)
        self.assert_cubic_cell_pos(cell)

        # override the top plane?
        cell.cut_plane_particle(0,1,0)
        self.assert_cubic_cell_basic(cell)
        # self.assert_cubic_cell_geo(cell) # swapped faces indices + wall id overwritten
        self.assert_cubic_cell_scale(cell)
        self.assert_cubic_cell_pos(cell)

    def test_cut_particle_index(self):
        # unit cube centered at the origin
        cell = self.get_cubic_cell()

        cell.cut_plane_particle(0,1,0)
        assert 0 in cell.neighbors()
        cell.cut_plane_particle(0,1,0, -10)
        assert -10 in cell.neighbors()

class TestContainer(TestCase_ext, TestCase_container):
    def test_methods_data(self):
        # unit cube centered at the origin
        cont = self.get_cubic_cont()

        self.assert_cubic_cell_geo(cont)

    def test_wall_basic(self):
        # atm the walls must be defined before constructing the container
        walls = [ (0,1,0, 0.25) ]
        cont = self.get_cubic_cont(walls=walls)

        # check the wall set limited the volume
        cell = cont[0]
        volume = 0.75
        cell_volume = cell.volume()
        self.assertAlmostEqual(volume, cell_volume)
        assert -10 in cell.neighbors()

    def test_wall_basic_double(self):
        # atm the walls must be defined before constructing the container
        walls = [ (0,1,0, 0.25), (0,-1,0, 0.25) ]
        cont = self.get_cubic_cont(walls=walls)

        # check the wall set limited the volume
        cell = cont[0]
        volume = 0.5
        cell_volume = cell.volume()
        self.assertAlmostEqual(volume, cell_volume)
        assert -10 in cell.neighbors()
        assert -11 in cell.neighbors()
