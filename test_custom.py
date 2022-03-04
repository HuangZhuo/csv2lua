import unittest
import custom


class TestCustom(unittest.TestCase):
    def test_mongen(self):
        custom.mongen('csv_custom/地图对应NPC.csv', 'csv_custom/mongen.csv')
        custom.write_bosstrial('csv_custom/mongen_tmp.csv', 'csv_custom/bosstrial.csv')
