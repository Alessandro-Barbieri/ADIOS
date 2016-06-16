import unittest as ut
import adios as ad
import numpy as np
from common import TempFile
from common import Slicee

class AdiosTestCase(ut.TestCase):
    temp = None ## TempFile

    def setUp(self):
        ad.init_noxml()
        ad.allocate_buffer (ad.BUFFER_ALLOC_WHEN.NOW, 10)

    def tearDown(self):
        ad.finalize()

    def test_simple1(self):
        self.temp = TempFile()

        NX = 10
        size = 2
        t = np.array(list(range(NX*size)), dtype=np.float64)
        tt = t.reshape((size, NX))

        fw = ad.writer(self.temp.path)
        fw.declare_group('group', method='POSIX1')

        fw['NX'] = NX
        fw['size'] = size
        fw['temperature'] = tt
        fw.attrs['/temperature/description'] = "Global array written from 'size' processes"
        fw.attrs["/someSubGroup/anOtherGroup/anOtherAttribute"] = 99
        fw["/someSubGroup/anOtherGroup/anOtherVariable"] = 77
        fw.close()

        f = ad.file(self.temp.path)
        t = f["temperature"]
        # here t could have a member dictionary attr(s) again
        # which looks up all attributes starting with t.name

        # now match: f.attrs["/temperature/description"]
        self.assertEqual(t.attrs["description"], f.attrs["/temperature/description"])

        # the same should be possible for groups
        g = f["/someSubGroup/anOtherGroup"]

        # now match: f.attrs["/someSubGroup/anOtherGroup/anOtherAttribute"]
        self.assertEqual(g.attrs["anOtherAttribute"], f.attrs["/someSubGroup/anOtherGroup/anOtherAttribute"])

        # now match: f["/someSubGroup/anOtherGroup/anOtherVariable"]
        self.assertEqual(g["anOtherVariable"], f["/someSubGroup/anOtherGroup/anOtherVariable"])

        # Missing '/'
        g = f["someSubGroup/anOtherGroup"]

        # now match: f.attrs["/someSubGroup/anOtherGroup/anOtherAttribute"]
        self.assertEqual(g.attrs["anOtherAttribute"], f.attrs["/someSubGroup/anOtherGroup/anOtherAttribute"])

        # now match: f["/someSubGroup/anOtherGroup/anOtherVariable"]
        self.assertEqual(g["anOtherVariable"], f["/someSubGroup/anOtherGroup/anOtherVariable"])

    def test_simple2(self):
        self.temp = TempFile()

        NX = 10
        size = 2
        t = np.array(list(range(NX*size)), dtype=np.float64)
        tt = t.reshape((size, NX))

        fw = ad.writer(self.temp.path)
        fw.declare_group('mygroup', method='POSIX1')

        fw['/data/0/fields/FieldE/x'] = tt
        fw['/data/0/fields/FieldE/y'] = tt*2

        fw['/data/0/particles/i/globalCellIdx/x'] = t
        fw['/data/0/particles/i/globalCellIdx/y'] = t*2

        fw.attrs['/data/0/fields/FieldE/x/sim_unit'] = 77
        fw.attrs['/data/0/fields/FieldE/y/sim_unit'] = 99

        fw.attrs['/data/0/iteration'] = 33
        fw.attrs['/data/0/sim_slides'] = 55
        fw.close()

        f = ad.file(self.temp.path)
        g = f["data/0"]
        self.assertTrue((g['fields/FieldE/x'][...] == tt).all())
        self.assertEqual(g['fields/FieldE/y/sim_unit'][...], 99)
        self.assertEqual(g['iteration'][...], 33)

        g1 = f["/data/0"]
        self.assertTrue((g1['fields/FieldE/x'][...] == tt).all())
        self.assertEqual(g1['fields/FieldE/y/sim_unit'][...], 99)
        self.assertEqual(g1['iteration'][...], 33)

        g = f["data"]
        g = f["/data"]
        g = f["/data/"]
        g = f["data/0/"]
        g = f["/data/0"]

if __name__ == '__main__':
    ut.main()
