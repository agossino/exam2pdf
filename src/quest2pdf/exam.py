#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TODO
# Question attribute type_of_question
# open_ended, yes_no, multi_choice
# based on number of alternative answers provided

from pathlib import Path
from typing import (Tuple, List, Optional, Iterator, Iterable,
                    Any, Sequence)
import logging
import csv
from random import shuffle


LOGNAME = "quest2pdf." + __name__
LOGGER = logging.getLogger(LOGNAME)
LETTER_A = "A"

class Answer:
    """An answer with optional image.
    """
    def __init__(self, text: str = ""):
        self.text: str = text
        self.image: Path = Path(".")

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        """Text is the answer.
        """
        if isinstance(text, str):
            self._text = text
        else:
            raise TypeError(f"{text} is not a string")

    @property
    def image(self) -> Path:
        return self._image

    @image.setter
    def image(self, file_path: Path) -> None:
        """Image can help or can be the answer.
        """
        if isinstance(file_path, Path):
            self._image = file_path
        else:
            raise TypeError(f"{file_path} is not a Path")


class Question:
    """Question is the question with the correct answer. Optionally it can
    have image, the subject (math, science ...), an integer representing
    the level of difficulty.
    """
    def __init__(self, text: str = ""):
        self.text: str = text
        self.image: Path = Path(".")
        self.subject: str = ""
        self.level: int = 0
        self._answers: List[Answer] = []
        self._correct_answer: Optional[Answer] = None  # setter bypassed
        self._correct_index: Optional[int] = None  # setter bypassed
        self._correct_letter: Optional[str] = None  # setter bypassed

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str) -> None:
        """Text is the question.
        """
        if isinstance(text, str):
            self._text = text
        else:
            raise TypeError(f"{text} in not a string")

    @property
    def image(self) -> Path:
        return self._image

    @image.setter
    def image(self, file_path: Path) -> None:
        """Image cha help or can be the question itself.
        """
        if isinstance(file_path, Path):
            self._image = file_path
        else:
            raise TypeError(f"{file_path} is not a Path")

    @property
    def subject(self) -> str:
        return self._subject

    @subject.setter
    def subject(self, name: str) -> None:
        """The subject of the question.
        """
        if isinstance(name, str):
            self._subject = name
        else:
            raise TypeError(f"{name} is not a string")

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, value: int) -> None:
        """The level of difficulty.
        """
        if isinstance(value, int):
            self._level = value
        else:
            raise TypeError(f"{value} is not an int")

    @property
    def answers(self) -> Tuple[Answer, ...]:
        return tuple(self._answers)

    def add_answer(self, answer: Answer, is_correct: bool = False) -> None:
        """Add an Answer. As side effect, correct answer is set.
        The first answer is the correct one: successive answers
        are set accordingly to is_correct argument.
        """
        if isinstance(answer, Answer):
            correct_answer = self._get_correct_answer(answer, is_correct)
            self._answers.append(answer)
            self.correct_answer = correct_answer
        else:
            raise TypeError(f"{answer} is not an Answer")

    @property
    def correct_answer(self) -> Optional[Answer]:
        """Set the given answer as the correct one.
        """
        return self._correct_answer

    @correct_answer.setter
    def correct_answer(self, value: Answer) -> None:
        if value in self._answers:
            self._correct_answer = value
        else:
            raise ValueError(f"{value} is not already added")
        pointer = self._answers.index(self._correct_answer)
        self._correct_index = pointer
        self._correct_letter = chr(ord(LETTER_A) + pointer)

    @property
    def correct_index(self) -> Optional[int]:
        return self._correct_index

    @correct_index.setter
    def correct_index(self, value: int) -> None:
        """Set the correct answer given its index.
        """
        try:
            self._correct_answer = self._answers[value]
        except IndexError as index_error:
            raise ValueError(f"no answer with index {value}") from index_error
        self._correct_index = value
        self._correct_letter = chr(ord(LETTER_A) + value)

    @property
    def correct_letter(self) -> Optional[str]:
        return self._correct_letter

    @correct_letter.setter
    def correct_letter(self, value: str) -> None:
        """Set the correct answer according to the given letter,
        where the first answer added is labeled A"""
        try:
            pointer = ord(value) - ord(LETTER_A)
            self._correct_answer = self._answers[pointer]
        except IndexError as index_error:
            raise ValueError(f"no answer with letter {value}") from index_error
        self._correct_index = pointer
        self._correct_letter = chr(ord(LETTER_A) + pointer)

    def _get_correct_answer(self, answer: Answer, is_correct: bool) -> Answer:
        """Return the correct answer: if no other answers are already added
        or the given is_correct is True, the given answer is returned,
        otherwise the stored correct answer is returned."""
        if self._correct_answer is None or is_correct:
            return answer
        else:
            return self._correct_answer

    def shuffle(self) -> None:
        """Shuffle the answers.
        """
        if self._correct_answer:
            shuffle(self._answers)
            pointer = self._answers.index(self._correct_answer)
            self._correct_index = pointer
            self._correct_letter = chr(ord(LETTER_A) + pointer)

    def load_sequentially(self, iterator: Iterator[Any]) -> None:
        """Load all the attribute sequentially
        from iterator. Not string value are casted.
        """
        try:
            self.text = next(iterator)
            self.subject = next(iterator)
            self.image = Path(next(iterator))
            self.level = int(next(iterator))
            while True:
                answer = Answer()
                answer.text = next(iterator)
                self.add_answer(answer)
                answer.image = Path(next(iterator))
        except StopIteration:
            pass


class Exam:
    """Exam is a sequence of Question managed as a whole.
    """
    def __init__(self, *args):
        self._questions: List[Question] = list()
        list(map(self.add_question, args))
        self._attribute_selection: Sequence = ()

    @property
    def questions(self) -> Tuple[Question]:
        return tuple(self._questions)

    @questions.setter
    def questions(self, values: Iterable[Question]) -> None:
        """Set all the questions given a sequence of them.
        """
        list(map(self.add_question, values))

    def add_question(self, question: Question) -> None:
        """Add one question to the sequence.
        """
        if isinstance(question, Question):
            self._questions.append(question)
        else:
            raise TypeError(f"{question} is not a Question")

    def set_selection(self, selection: Sequence[str]) -> None:
        self._attribute_selection = selection

    def _loader(self, row):
        quest = Question()
        iterator = (row[key] for key in self._attribute_selection)
        quest.load_sequentially(iterator)
        return quest

    def from_csv(self, file_path: Path):
        with file_path.open() as csv_file:
            reader = csv.DictReader(csv_file)
            self._questions = list(map(self._loader, reader))

    def __str__(self):
        output: List[str] = []
        for q in self._questions:
            output.append(f"domanda: {q.text}\nsoggetto: {q.subject}")
            output.append(f"\nimmagine: {q.image}\nlivello: {q.level}")
            output.append(f"\ncorretta: {q.correct_letter}")
            for i, a in enumerate(q.answers):
                letter = chr(ord("A") + i)
                output.append(f"\nrisposta {letter}: {a.text}")
                output.append(f"\nimmagine: {a.image}")
        return "".join(output)