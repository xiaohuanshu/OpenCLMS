'''
    main patch

    usage: add `import <module.path.to.perform_patches>` to your code

    you can perform any of them to your code, the comments in these are:
        1. first appearance of "bug" in current source code
        2. the solution from

    for some error messages "ModuleNotFoundError: No module named 'constant'"
    from something like "from constant import *", a easy way to fix is
    executing the command below under OpenCLMS/:
        `find . -name '*.py' |xargs sed -i -E 's/^from <pkg> import/from .<pkg> import/g'`
    which:
        <pkg> is something like constant, models, etc..
'''

from . import django4compat, python3compat
