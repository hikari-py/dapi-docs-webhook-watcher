"""Development tasks implemented by Piped."""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path("./piped/python").absolute()))

from noxfile import *
