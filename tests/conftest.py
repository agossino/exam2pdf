import os
from pathlib import Path
from itertools import chain
import random
import subprocess

import pytest

import quest2pdf


@pytest.fixture
def dummy_exam():
    q1, q2, q3, q4, q5 = (
        quest2pdf.Question("q1 text", "q1 subject", Path("a.png"), 1),
        quest2pdf.Question("q2 text", "q2 subject", Path("b.png"), 2),
        quest2pdf.Question("q3 text", "q3 subject", Path("c.png"), 3),
        quest2pdf.Question("q4 text", "q4 subject", Path("a.png"), 4),
        quest2pdf.Question("q5 text", "q5 subject", Path("b.png"), 5),
    )

    q1.answers = (quest2pdf.Answer("q1 a1"), quest2pdf.Answer("q1 a2"))
    q1.correct_index = 1
    q2.answers = (quest2pdf.Answer("q2 a1"), quest2pdf.Answer("q2 a2"))

    return quest2pdf.Exam(q1, q2, q3, q4, q5)


@pytest.fixture
def dummy_exam_with_img(tmp_path, dummy_exam):
    image_folder = Path("tests/unit/resources")
    image_tmp_folder = tmp_path / image_folder.name
    image_tmp_folder.mkdir()

    for file in chain(image_folder.glob("*.png"), image_folder.glob("*.jpg")):
        data = file.read_bytes()
        copied_file = tmp_path / image_folder.name / file.name
        copied_file.write_bytes(data)

    dummy_exam.add_path_parent(image_tmp_folder)

    return dummy_exam


@pytest.fixture
def mix_dummy_exam():
    q1 = quest2pdf.Question("question 1: correct is n. 2", "subject 1", Path("a.png"))
    a1 = quest2pdf.Answer("answer 1", Path("b.png"))
    a2 = quest2pdf.Answer("answer 2", Path("c.png"))
    a3 = quest2pdf.Answer("answer 3", Path("a.png"))
    q1.answers = (a1, a2, a3)
    q1.correct_option = "B"

    q2 = quest2pdf.Question("question 2: correct is n. 1", "subject 1", Path("a.png"))
    a1 = quest2pdf.Answer("answer 1")
    a2 = quest2pdf.Answer("answer 2")
    a3 = quest2pdf.Answer("answer 3")
    q2.answers = (a1, a2, a3)

    q3 = quest2pdf.TrueFalseQuest("question 3: correct is True (first)")
    a1 = quest2pdf.TrueFalseAnswer(True)
    a2 = quest2pdf.TrueFalseAnswer(False)
    q3.answers = (a1, a2)

    q4 = quest2pdf.Question("question 4: no answer", "subject 2", Path("b.png"))

    q5 = quest2pdf.TrueFalseQuest("question 5: correct is False (first))")
    a1 = quest2pdf.TrueFalseAnswer(False)
    a2 = quest2pdf.TrueFalseAnswer(True)
    q5.answers = (a1, a2)

    q6 = quest2pdf.Question("question 6: correct is n. 3", "subject 4", Path("c.png"))
    a1 = quest2pdf.Answer("answer 1")
    a2 = quest2pdf.Answer("answer 2")
    a3 = quest2pdf.Answer("answer 3")
    a4 = quest2pdf.Answer("answer 4")
    q6.add_answer(a1)
    q6.add_answer(a2)
    q6.add_answer(a3, is_correct=True)
    q6.add_answer(a4)
    dummy_ex = quest2pdf.Exam(q1, q2, q3, q4, q5, q6)

    return dummy_ex


@pytest.fixture
def big_dummy_exam():
    q1 = quest2pdf.Question("question 1: correct is n. 2", "subject 1", Path("a.png"))
    a1 = quest2pdf.Answer("answer 1", Path("b.png"))
    a2 = quest2pdf.Answer("answer 2", Path("c.png"))
    a3 = quest2pdf.Answer("answer 3", Path("a.png"))
    q1.answers = (a1, a2, a3)
    q1.correct_option = "B"

    q2 = quest2pdf.Question("question 2: correct is n. 1", "subject 1", Path("a.png"))
    a1 = quest2pdf.Answer("answer 1")
    a2 = quest2pdf.Answer("answer 2")
    a3 = quest2pdf.Answer("answer 3")
    q2.answers = (a1, a2, a3)

    q3 = quest2pdf.TrueFalseQuest("question 3: correct is True (first)")
    a1 = quest2pdf.TrueFalseAnswer(True)
    a2 = quest2pdf.TrueFalseAnswer(False)
    q3.answers = (a1, a2)

    q4 = quest2pdf.Question("question 4: no answer", "subject 2", Path("b.png"))

    q5 = quest2pdf.TrueFalseQuest("question 5: correct is False (first))")
    a1 = quest2pdf.TrueFalseAnswer(False)
    a2 = quest2pdf.TrueFalseAnswer(True)
    q5.answers = (a1, a2)

    q6 = quest2pdf.Question("question 6: correct is n. 3", "subject 4", Path("c.png"))
    a1 = quest2pdf.Answer("answer 1")
    a2 = quest2pdf.Answer("answer 2")
    a3 = quest2pdf.Answer("answer 3")
    a4 = quest2pdf.Answer("answer 4")
    q6.add_answer(a1)
    q6.add_answer(a2)
    q6.add_answer(a3, is_correct=True)
    q6.add_answer(a4)
    dummy_ex = quest2pdf.Exam(q1, q2, q3, q4, q5, q6)

    return dummy_ex


def save_app_configuration(file_path):
    text = "[Default]\n"
    file_path.write_text(text)


def save_app_configuration_set(file_path):
    text = "[Default]\nnumber = 3\nexam = Exam from conf.ini\n"
    file_path.write_text(text)


def save_log_configuration(file_path):
    text = """{
    "disable_existing_loggers": false,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "file": {
             "level": "DEBUG",
             "class": "logging.handlers.RotatingFileHandler",
             "formatter": "default",
             "filename": "application.log",
             "maxBytes": 1024000,
             "backupCount": 3
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": true
        }
    },
    "version": 1
}"""
    file_path.write_text(text)


@pytest.fixture
def empty_question_file(tmp_path):
    file_path = tmp_path / "question.csv"
    text = "question,subject,image,level,A,Ai,B,Bi,C,Ci\n "
    file_path.write_text(text)
    return file_path


@pytest.fixture
def truefalse_question_file(tmp_path):
    file_path = tmp_path / "question.csv"
    text = """Question type,question,A,B,void
TrueFalse,Q,,1,"""
    file_path.write_text(text)
    return file_path


@pytest.fixture
def question_data_file(tmp_path):
    file_path = tmp_path / "question.csv"

    text = "question,subject,image,level,A,Ai,B,Bi,C,Ci\nQ,S,I,1,a,ai,b,bi,c,ci"
    file_path.write_text(text)

    return file_path


@pytest.fixture
def have_a_look(tmp_path, big_dummy_exam):
    image_folder = Path("tests/unit/resources")
    image_tmp_folder = tmp_path / image_folder.name
    image_tmp_folder.mkdir()
    for file in chain(image_folder.glob("*.png"), image_folder.glob("*.jpg")):
        data = file.read_bytes()
        copied_file = tmp_path / image_folder.name / file.name
        copied_file.write_bytes(data)

    random.seed()

    exam_file_path = tmp_path / "Exam"
    correction_file_path = tmp_path / "Correction"
    ex = big_dummy_exam
    ex.add_path_parent(image_tmp_folder)
    ex.print(exam_file_path, correction_file_name=correction_file_path, heading="Not shuffled exam")

    subprocess.Popen(["evince", str(exam_file_path)])
    subprocess.Popen(["evince", str(correction_file_path)])

    yield


@pytest.fixture
def is_correct():
    prompt = "Is it correct (y/n)?"
    with os.fdopen(os.dup(1), "w") as std_out:
        std_out.write(f"\n{prompt} ")

    with os.fdopen(os.dup(2), "r") as std_in:
        answer = std_in.readline()

    return answer
