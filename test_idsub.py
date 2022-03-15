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
        '''使用批处理对命令进行包装'''
        import os

        # bat = './opencsv.cmd'
        bat = os.path.abspath('./opencsv.cmd')
        file = os.path.abspath('./csv_idsub/caiquanrankaward.csv')
        cmd = bat + ' "' + file + '"'
        os.system(cmd)  # also works well!
        print('fin')

    def test_os_system2(self):
        '''命令带空格的情况'''
        import os
        import subprocess
        exe = r"C:\Program Files (x86)\WPS Office\11.1.0.11365\office6\et.exe"
        file = os.path.abspath('./csv_idsub/caiquanrankaward.csv')
        cmd = f'"{exe}" "{file}" /n'
        print(cmd)
        # os.system(cmd)
        subprocess.run(cmd)
        print('fin')
