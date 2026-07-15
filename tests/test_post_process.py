import tempfile
import unittest
from pathlib import Path

from src import post_process


class LocalImagePathTest(unittest.TestCase):
    def test_encodes_spaces_in_local_image_paths_and_keeps_the_image_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            markdown = Path(tmp) / "manual.md"
            image = Path(tmp) / "images" / "截图 2.png"
            image.parent.mkdir()
            image.write_bytes(b"png")
            markdown.write_text("![截图](./images/截图 2.png)", encoding="utf-8")

            changed = post_process.encode_local_image_paths(markdown)
            missing = post_process.fix_missing_local_images(markdown)

            self.assertEqual(changed, 1)
            self.assertEqual(missing, 0)
            self.assertEqual(markdown.read_text(encoding="utf-8"), "![截图](./images/截图%202.png)")


if __name__ == "__main__":
    unittest.main()
