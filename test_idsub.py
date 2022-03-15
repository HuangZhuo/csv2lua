import unittest

import idsub


class TestIDSub(unittest.TestCase):
    def test_main(self):
        idsub.process('./csv_idsub/caiquanrankaward.csv')

    def test_startEdit(self):
        idsub.startEdit('./csv_idsub/caiquanrankaward.csv')
        print('finished!')

    def test_what_the_fuck_shell(self):
        from os import environ
        print(environ['SHELL'])

    def test_subprocess(self):
        import os
        import subprocess
        file = os.path.abspath('./csv_idsub/caiquanrankaward.csv')
        cmd = r'.\opencsv.cmd "' + file + '"'
        subprocess.run(cmd)
        print('fin')

    def test_os_system(self):
        import os
        bat = os.path.abspath('./opencsv.cmd')
        file = os.path.abspath('./csv_idsub/caiquanrankaward.csv')
        cmd = bat + ' "' + file + '"'
        os.system(cmd)  # also works well!
        print('fin')
