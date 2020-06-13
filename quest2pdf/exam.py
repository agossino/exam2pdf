from pathlib import Path
import csv
import random
from typing import Tuple, List, Iterable, Any, Mapping, Generator, Dict, Optional
import logging
from .question import Question, MultiChoiceQuest, TrueFalseQuest
from .utility import ItemLevel, Item, Quest2pdfException
from .export import RLInterface


LOGNAME = "quest2pdf." + __name__
LOGGER = logging.getLogger(LOGNAME)


class Exam:
    """Exam is a sequence of Question managed as a whole.
    """

    def __init__(self, *args: Question):
        self._questions = list()
        self._question_type_key: str = "Question type"
        list(map(self.add_question, args))
        self._attribute_selector: Tuple[str, ...] = ()

    @property
    def questions(self) -> Tuple[Question, ...]:
        return tuple(self._questions)

    @questions.setter
    def questions(self, values: Iterable[Question]) -> None:
        """Set questions given a sequence of them, overriding any
        previous data.
        """
        # Reset
        self._questions = []

        list(map(self.add_question, values))

    @property
    def attribute_selector(self) -> Tuple[str, ...]:
        return self._attribute_selector

    @attribute_selector.setter
    def attribute_selector(self, selection: Iterable[str]) -> None:
        self._attribute_selector = tuple(str(item) for item in selection)

    def add_question(self, question: Question) -> None:
        """Add one question to the sequence.
        """
        # if isinstance(question, Question):
        #     self._questions.append(question)
        # else:
        #     raise TypeError(f"{question} is not a Question")
        self._questions.append(question)

    def add_path_parent(self, file_path: Path):
        for question in self._questions:
            question.add_parent_path(file_path)

    def load(self, iterable: Iterable[Mapping[str, Any]]) -> None:
        questions_classes = {
            "MultiChoice": MultiChoiceQuest,
            "TrueFalse": TrueFalseQuest,
        }
        default_key = "MultiChoice"
        for row in iterable:
            quest = questions_classes[row.get(self._question_type_key, default_key)]()
            if self._attribute_selector:
                try:
                    data = [row[key] for key in self._attribute_selector]
                except KeyError:
                    raise Quest2pdfException("Key mismatch in cvs file")
            else:
                data = [row[key] for key in row]
            if data:
                self.add_question(quest)
                iterator = iter(data)
                quest.load_sequentially(iterator)

    def from_csv(self, file_path):
        """Read from csv file a series of questions.
        """
        with file_path.open(encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file, delimiter=",")
            rows: List[Dict[str, str]] = [row for row in reader]

        self.load(rows)
        self.add_path_parent(file_path)

    def print(
        self,
        exam_file_name: Path,
        correction_file_name: Optional[Path] = None,
        shuffle: bool = True,
        destination: Path = Path(),
        heading: str = "",
        footer: str = "",
    ) -> None:
        """Print in PDF all the questions and correction
        """
        if shuffle:
            self.answers_shuffle()

        questions_serialized = SerializeExam(self.questions)

        interface = RLInterface(
            questions_serialized.assignment(),
            exam_file_name,
            destination=destination,
            heading=heading,
            footer=footer,
        )
        interface.build()

        if correction_file_name is not None:
            interface = RLInterface(
                questions_serialized.correction(),
                correction_file_name,
                destination=destination,
                heading=heading,
                footer=footer,
                top_item_bullet_type="A",
                sub_item_bullet_type="1",
            )
            interface.build()

    def answers_shuffle(self):
        for question in self._questions:
            question.shuffle()

    def questions_shuffle(self):
        random.shuffle(self._questions)

    def __str__(self) -> str:
        output: List[str] = []
        for question in self._questions:
            output.append(question.__str__())
        return "".join(output)


class SerializeExam:
    """Serialize questions, made of text and image, and
    answers, made of text and image.
    """

    def __init__(self, serial_data: Iterable):
        self._serial_data: Iterable = serial_data

    def assignment(self) -> Generator[Item, None, None]:
        for question in self._serial_data:
            yield Item(ItemLevel.top, question.text, question.image)
            for answer in question.answers:
                yield Item(ItemLevel.sub, answer.text, answer.image)

    def correction(self) -> Generator[Item, None, None]:
        if self._serial_data != ():
            yield Item(ItemLevel.top, f"correction", Path("."))
        for question in self._serial_data:
            yield Item(ItemLevel.sub, f"{question.correct_option}", Path("."))
