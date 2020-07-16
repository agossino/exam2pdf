from pathlib import Path
from typing import Iterator
from .rlwrapper import PDFDoc
from .utility import ItemLevel, Item


class RLInterface:
    def __init__(self, input_generator: Iterator[Item], output_file: Path, **kwargs):
        """This class print a two nesting level series of items in pdf.
        """
        file_name: Path = kwargs.get("destination", Path(".")) / output_file
        self._input = input_generator
        page_heading: str = kwargs.get("heading", "")
        page_footer: str = kwargs.get("footer", "")
        self._doc = PDFDoc(
            file_name, page_heading=page_heading, page_footer=page_footer, **kwargs
        )

    def build(self) -> None:
        try:
            item = next(self._input)
            assert item.item_level == ItemLevel.top, "The first ItemLevel must be top"
            self._doc.add_item(item)
            while True:
                item = next(self._input)
                if item.item_level == ItemLevel.top:
                    self._doc.add_item(item)
                else:
                    self._doc.add_sub_item(item)
        except StopIteration:
            self._doc.build()
