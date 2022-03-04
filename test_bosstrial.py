import unittest
import bosstrial


class TestBosstrial(unittest.TestCase):
    def test_mongen(self):
        bosstrial.mongen('csv_bosstrial/地图对应NPC.csv', 'csv_bosstrial/mongen.csv')
        bosstrial.write_bosstrial('csv_bosstrial/mongen_tmp.csv', 'csv_bosstrial/bosstrial.csv')
