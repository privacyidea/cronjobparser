# -*- coding: utf-8 -*-

import logging
import unittest
import os
from .cronjobparser import CronJobParser, CronJob
log = logging.getLogger(__name__)

CRONTAB_TEST = "./testdata/crontab"
CRONTAB_TMP = "./testdata/tmpfile"


class TestCrontabParser(unittest.TestCase):

    def test_import_from_file(self):
        CP = CronJobParser(CRONTAB_TEST)
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
        CP = CronJobParser(CRONTAB_TEST)
        config = CP.config
        self.assertEqual(len(config), 2)
        self.assertTrue("assignments" in config)
        self.assertTrue("cronjobs" in config)

    def test_save(self):
        CP = CronJobParser(CRONTAB_TEST)
        config = CP.config
        self.assertEqual(len(config.get("cronjobs")), 6)
        cronj = config.get("cronjobs")[0]
        self.assertEqual(cronj.minute, "17")
        self.assertEqual(cronj.dow, "*")

        # now save it to a file
        CP.save(outfile=CRONTAB_TMP)
        # Read the file again!
        CP2 = CronJobParser(CRONTAB_TMP)
        config = CP2.config
        self.assertEqual(len(config.get("cronjobs")), 6)
        cronj = config.get("cronjobs")[0]
        self.assertEqual(cronj.minute, "17")
        self.assertEqual(cronj.dow, "*")

        # update the file and reread the cronjobs
        with open(CRONTAB_TMP, 'a') as f:
            f.write('1	2	3	4	5	foo	bär')

        CP2.read()
        self.assertEqual(len(CP2.config.get("cronjobs")), 7)
        self.assertEqual(CP2.config.get("cronjobs")[6].command, u'bär')

        # remove temporary file
        os.unlink(CRONTAB_TMP)

    def test_cronjob_api(self):
        CP = CronJobParser(CRONTAB_TEST)
        config = CP.config
        self.assertEqual(len(config.get("cronjobs")), 6)

        backup_job2 = config['cronjobs'][-1]
        self.assertEqual(backup_job2.command, "/usr/bin/privacyidea-backup")
        self.assertEqual(backup_job2.time, ("1", "10", "1", "*", "*"))
        self.assertEqual(backup_job2.get_time_comment(), "monthly")
        self.assertEqual(backup_job2.get_time_summary(), "monthly at time 10:01, "
                                                         "day of month: 1, month: "
                                                         "*, day of week: *")

        backup_copy = CronJob.from_time("/usr/bin/privacyidea-backup",
                                        "privacyidea", ("1", "10", "1"))
        self.assertEqual(str(backup_job2), str(backup_copy))

        cronjob = CronJob.from_time("foo", "user", ())
        assert cronjob.time == ("*",) * 5
        self.assertEqual(cronjob.get_time_summary(),
                         "time *:*, day of month: *, month: *, day of week: *")

        self.assertRaises(RuntimeError, CronJob.from_time, "foo", "user",
                          ("1", "2", "3", "4", "5", "6"))

        rm_cmd = "find /var/log/privacyidea -name privacyidea.log.* " \
                 "--exec 'rm' '-f' '{}' ';'"
        rm_job = CronJob.from_time(rm_cmd, "root", ('1', '2', '3', '4', '5'))
        self.assertEqual(rm_job.command, rm_cmd)
        self.assertEqual(rm_job.get_time_comment(), "yearly")
