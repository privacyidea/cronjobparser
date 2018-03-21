# -*- coding: utf-8 -*-
import codecs

from pyparsing import White, Word, alphanums, CharsNotIn
from pyparsing import Forward, Group, OneOrMore
from pyparsing import pythonStyleComment


class CronJob(object):

    def __init__(self, command, minute, user="root", hour="*", dom="*",
                 month="*", dow="*"):
        self.command = command
        self.minute = minute
        self.user = user
        self.hour = hour
        self.dom = dom
        self.month = month
        self.dow = dow

    @classmethod
    def from_time(cls, command, user, time):
        """
        Alternative method to instantiate CronJob.
        :param command: like in ``CronJob.__init__``
        :param user: like in ``CronJob.__init__``
        :param time: a list or tuple of at most five strings. Missing elements are set to "*".
        :return: a ``CronJob`` object
        """
        assert len(time) <= 5
        padded_time = tuple(time) + ('*',) * (5 - len(time))
        assert len(padded_time) == 5
        return cls(command, time[0], user, padded_time[1], padded_time[2], padded_time[3], padded_time[4])

    @property
    def time(self):
        """ Return the cronjob time as a tuple of five strings """
        return (self.minute,
                self.hour,
                self.dom,
                self.month,
                self.dow)

    def __str__(self):
        """
        This simply returns the CronJob so that it can be added to the crontab
        """
        cronjob = "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (self.minute, self.hour,
                                                  self.dom, self.month,
                                                  self.dow, self.user,
                                                  self.command)
        return cronjob

    def get_time_comment(self):
        """
        Return a human-readable comment describing the cronjob time, if possible.
        :return: a string, e.g. "hourly", "monthly", which may be empty if no description can be inferred.
        """
        comment = ""
        if self.minute != "*":
            comment = "hourly"
        if self.hour != "*":
            comment = "daily"
        if self.dow != "*":
            comment = "weekly"
        if self.dom != "*":
            comment = "monthly"
        if self.month != "*":
            comment = "yearly"
        return comment

    def get_time_summary(self):
        """
        Get a human-readable summary of the cronjob time.
        :return: a string of the form "Y at time hh:mm, day of month:x, month:x, day of week:x",
        where as Y is the comment returned by ``get_time_comment``. If no comment can be found,
        the "Y at" is omitted.
        """
        comment = self.get_time_comment()
        if comment:
            full_comment = "{} at ".format(comment)
        else:
            full_comment = ""
        hour = self.hour
        if hour != "*":
            hour = hour.zfill(2)
        minute = self.minute
        if minute != "*":
            minute = minute.zfill(2)
        return "{}time {}:{}, day of month: {}, month: {}, day of week: {}".format(
            full_comment,
            hour,
            minute,
            self.dom,
            self.month,
            self.dow
        )


class CronJobParser(object):
    
    dtime = Word("0123456789-*")
    command = CharsNotIn("{}\n#,")
    username = Word(alphanums)
    key = Word(alphanums)
    value = command
    space = White().suppress()
    comment = Word("#")
    equals = Word("=")
    assignment = Forward()
    assignment << Group(key
                        + equals.suppress()
                        + value)
    entry_block = Forward()
    entry_block << Group(dtime
                         + space.suppress()
                         + dtime
                         + space.suppress()
                         + dtime
                         + space.suppress()
                         + dtime
                         + space.suppress()
                         + dtime
                         + space.suppress()
                         + username
                         + space.suppress()
                         + command
                         )
    cron_file = OneOrMore(entry_block | assignment).ignore(pythonStyleComment)
    
    file_header = """# File parsed and saved by crontabparser.\n\n"""
    
    def __init__(self, infile="/etc/crontab"):
        self.file = infile
        self.read()

    def read(self):
        f = codecs.open(self.file, "r", "utf-8")
        self.content = f.read()
        f.close()
        data = self.get()
        self.assignments = {}
        self.cronjobs = []
        for entry in data:
            if len(entry) == 2:
                self.assignments[entry[0]] = entry[1]
            elif len(entry) == 7:
                self.cronjobs.append(CronJob(entry[6], entry[0],
                                        user=entry[5], hour=entry[1],
                                        dom=entry[2], month=entry[3],
                                        dow=entry[4]))

    @property
    def config(self):
        return {"assignments": self.assignments,
                "cronjobs": self.cronjobs}

    def get(self):
        """
        return the grouped config
        
        """
        # reread the file from dist
        if self.file:
            f = codecs.open(self.file, "r", "utf-8")
            self.content = f.read()
            f.close()
        config = self.cron_file.parseString(self.content)
        return config
    
    def format(self):
        """
        :return: The formatted data as it would be written to a file
        """
        output = ""
        output += self.file_header
        # write the assignments
        assignments = self.assignments
        for assignment in assignments:
            output += "%s=%s\n" % (assignment,
                                   assignments.get(assignment))
        # write the cronjobs
        output += "\n#m\th\tdom\tmon\tdow\tuser\tcommand\n"
        for cronjob in self.cronjobs:
            output += "%s\n" % cronjob
        return output

    def save(self, outfile):
        output = self.format()
        f = codecs.open(outfile, 'w', 'utf-8')
        for line in output.splitlines():
            f.write(line + "\n")
        f.close()
