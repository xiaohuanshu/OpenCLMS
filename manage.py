#!/usr/bin/env python
import os
import sys
import compatches.perform_patches

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "checkinsystem.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
