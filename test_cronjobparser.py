# -*- coding: utf-8 -*-


import logging
log = logging.getLogger(__name__)
import unittest
import os
from cronjobparser import CronJobParser, CronJob


class TestCrontabParser(unittest.TestCase):

    def test_import_from_file(self):
        CP = CronJobParser("./testdata/crontab")
        config_raw = CP.get()
        self.assertEqual(len(config_raw), 8)

        config = CP.config
        self.assertEqual(len(config), 2)
        self.assertTrue("assignments" in config)
        self.assertTrue("cronjobs" in config)

        self.assertEqual(len(config.get("cronjobs")), 6)

        self.assertTrue("PATH" in config.get("assignments"))
        self.assertTrue("SHELL" in config.get("assignments"))

    def test_from_config(self):
        CP = CronJobParser("./testdata/crontab")
        config = CP.config
        self.assertEqual(len(config), 2)
        self.assertTrue("assignments" in config)
        self.assertTrue("cronjobs" in config)

    def test_save(self):
        CP = CronJobParser("./testdata/crontab")
        config = CP.config
        self.assertEqual(len(config.get("cronjobs")), 6)
        cronj = config.get("cronjobs")[0]
        self.assertEqual(cronj.minute, "17")
        self.assertEqual(cronj.dow, "*")

        # now save it to a file

        CP.save(outfile="./testdata/tmpfile")
        # Read the file again!
        CP2 = CronJobParser("./testdata/tmpfile")
        config = CP2.config
        self.assertEqual(len(config.get("cronjobs")), 6)
        cronj = config.get("cronjobs")[0]
        self.assertEqual(cronj.minute, "17")
        self.assertEqual(cronj.dow, "*")
        os.unlink("./testdata/tmpfile")

    def test_cronjob_api(self):
        CP = CronJobParser("./testdata/crontab")
        config = CP.config
        self.assertEqual(len(config.get("cronjobs")), 6)

        backup_job2 = config['cronjobs'][-1]
        self.assertEqual(backup_job2.command, "/usr/bin/privacyidea-backup")
        self.assertEqual(backup_job2.time, ("1", "10", "1", "*", "*"))
        self.assertEqual(backup_job2.get_time_comment(), "monthly")
        self.assertEqual(backup_job2.get_time_summary(),
                         "monthly at time 10:01, day of month: 1, month: *, day of week: *")

        backup_copy = CronJob.from_time("/usr/bin/privacyidea-backup", "privacyidea", ("1", "10", "1"))
        self.assertEqual(str(backup_job2), str(backup_copy))

        cronjob = CronJob.from_time("foo", "user", ())
        assert cronjob.time == ("*",) * 5


