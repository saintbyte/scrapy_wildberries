from __future__ import absolute_import

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def run_from_argv(self, argv):
        self._argv = argv
        new_args = self._argv[:2]
        self._called_from_command_line = True
        parser = self.create_parser(new_args[0], new_args[1])
        options = parser.parse_args(new_args[2:])
        cmd_options = vars(options)
        self.execute(*new_args, **cmd_options)

    def handle(self, *args, **options):
        from scrapy.cmdline import execute

        execute(self._argv[1:])
