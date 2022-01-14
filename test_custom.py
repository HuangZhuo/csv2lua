import unittest
import custom


class TestCustom(unittest.TestCase):
    def test_mongen(self):
        custom.mongen('csv/地图对应NPC.csv', 'csv/mongen.csv')
        custom.write_bosstrial('csv/mongen_tmp.csv', 'csv/bosstrial.csv')
