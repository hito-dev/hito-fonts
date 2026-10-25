"""Rebuild the 800 parent instance from the pinned Inter axis and GroundState recipe."""
from pathlib import Path
import shutil, sys, tempfile
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "source"))
import groundstate_heavy_build as parent

with tempfile.TemporaryDirectory() as folder:
    parent.ROOT = Path(folder)
    (parent.ROOT / "source").mkdir()
    (parent.ROOT / "fonts").mkdir()
    parent.SOURCE = ROOT / "source/Inter-variable.ttf"
    parent.WEIGHTS = [(800, "ExtraBold")]
    parent.build()
    shutil.copyfile(parent.ROOT / "fonts/GroundStateSans-ExtraBold.ttf",
                    ROOT / "source/GroundStateSans-ExtraBold.ttf")
