from __future__ import annotations

from pathlib import Path
import csv
import random
from typing import Tuple, List, Iterable, Any, Mapping, Generator, Dict, Optional
import logging
from .question import Question, TrueFalseQuest
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
        questions_classes = {"MultiChoice": Question, "TrueFalse": TrueFalseQuest}
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

    def copy(self) -> Exam:
        questions = (question.copy() for question in self.questions)
        new_exam = Exam(*questions)
        return new_exam

    def print(
        self,
        exam_file_name: Path,
        correction_file_name: Optional[Path] = None,
        answers_shuffle: bool = False,
        questions_shuffle: bool = False,
        destination: Path = Path(),
        n_copies: int = 1,
        heading: str = "",
        footer: str = "",
    ) -> None:
        """Print in PDF all the questions and correction
        """
        questions_serialized = SerializeExam(
            self, shuffle_item=questions_shuffle, shuffle_sub=answers_shuffle
        )

        heading = exam_file_name.name if heading == "" else heading

        for number in range(1, n_copies + 1):
            interface = RLInterface(
                questions_serialized.assignment(),
                exam_file_name,
                destination=destination,
                heading=f"{heading} {number}/{n_copies}",
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
        for question in self.questions:
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

    def __init__(
        self, exam: Exam, shuffle_item: bool = False, shuffle_sub: bool = False
    ):
        self._exam: Exam = exam
        self._shuffle_item: bool = shuffle_item
        self._shuffle_sub: bool = shuffle_sub
        self._exams_sequence: List[Exam] = []
        self._correction_top_text: str = f"correction:"

    def assignment(self) -> Generator[Item, None, None]:
        exam = self._get_a_shuffled_copy()
        for question in exam.questions:
            yield Item(ItemLevel.top, question.text, question.image)
            for answer in question.answers:
                yield Item(ItemLevel.sub, answer.text, answer.image)

    def correction(self) -> Generator[Item, None, None]:
        total_copies = len(self._exams_sequence)
        for copy_number, exam in enumerate(self._exams_sequence, 1):
            if exam.questions != ():
                top_text = f"{self._correction_top_text} {copy_number}/{total_copies}"
                yield Item(ItemLevel.top, top_text, Path("."))
            for question in exam.questions:
                yield Item(ItemLevel.sub, f"{question.correct_option}", Path("."))

    def _get_a_shuffled_copy(self) -> Exam:
        exam = self._exam.copy()

        if self._shuffle_item:
            exam.questions_shuffle()

        if self._shuffle_sub:
            exam.answers_shuffle()

        self._exams_sequence.append(exam)

        return exam