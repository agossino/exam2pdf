import pathlib
import pytest
import os
from pathlib import Path
import subprocess
import random
from itertools import chain
import quest2pdf
from quest2pdf.exam import SerializeExam
from quest2pdf.utility import Item, ItemLevel
from unit_helper import save_empty_question, save_question_data, save_tf_question


def fd_input(prompt):
    with os.fdopen(os.dup(1), "w") as stdout:
        stdout.write(f"\n{prompt}? ")

    with os.fdopen(os.dup(2), "r") as stdin:
        return stdin.readline()


@pytest.fixture
def fake_exam():
    q1, q2, q3, q4, q5 = (
        quest2pdf.Question("q1 text", "q1 subject", pathlib.Path("q1 image"), 1),
        quest2pdf.Question("q2 text", "q2 subject", pathlib.Path("q2 image"), 2),
        quest2pdf.Question("q3 text", "q3 subject", pathlib.Path("q3 image"), 3),
        quest2pdf.Question("q4 text", "q4 subject", pathlib.Path("q4 image"), 4),
        quest2pdf.Question("q5 text", "q5 subject", pathlib.Path("q5 image"), 5),
    )

    q1.answers = (quest2pdf.Answer("q1 a1"), quest2pdf.Answer("q1 a2"))
    q1.correct_index = 1
    q2.answers = (quest2pdf.Answer("q2 a1"), quest2pdf.Answer("q2 a2"))

    return quest2pdf.Exam(q1, q2, q3, q4, q5)


@pytest.fixture
def fake_mix_exam():
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


def test_exam():
    """test Exam with no args
    """
    ex = quest2pdf.Exam()

    assert ex.questions == tuple()


def test_exam_init():
    """test Exam with one and two arguments
    """
    q1, q2 = (
        quest2pdf.question.Question("q1 text", "q1 image"),
        quest2pdf.question.Question("q2 text", "q2 image"),
    )
    ex1 = quest2pdf.Exam(q1)
    ex2 = quest2pdf.Exam(q1, q2)

    assert ex1.questions == (q1,)
    assert ex2.questions == (q1, q2)


def test_exam_questions_setter0():
    """test question set
    """
    q1, q2 = (
        quest2pdf.question.Question("q1 text", "q1 image"),
        quest2pdf.question.Question("q2 text", "q2 image"),
    )
    ex = quest2pdf.Exam()
    ex.add_question(q1)
    ex.add_question(q2)

    assert q1 in ex.questions
    assert q2 in ex.questions


def test_exam_questions_setter1():
    """test question set; question added before overwritten
    """
    q1, q2 = (
        quest2pdf.Question("q1 text", "q1 image"),
        quest2pdf.Question("q2 text", "q2 image"),
    )
    ex = quest2pdf.Exam()
    ex.add_question(q1)
    ex.questions = (q2,)

    assert q1 not in ex.questions
    assert q2 in ex.questions


def test_exam_attribute_selector1():
    """test attribute_selector default value"""
    ex = quest2pdf.Exam()

    assert ex.attribute_selector == ()


def test_exam_attribute_selector2():
    """test attribute_selector set and type conversion
    """
    ex = quest2pdf.Exam()
    expected = ("hello", "2", "times")
    ex.attribute_selector = (expected[0], int(expected[1]), expected[2])

    assert ex.attribute_selector == expected


def test_exam_add_path_parent1(tmp_path):
    """test with a file path
    """
    image = Path("images/image.png")
    file_path = tmp_path / "A.txt"
    file_path.touch()
    q1 = quest2pdf.Question("q1 text", "")
    q1.answers = (
        quest2pdf.Answer("a1 text", image),
        quest2pdf.Answer("a2 text", image),
    )
    q2 = quest2pdf.Question("q2 text", "", image)
    q2.add_answer(quest2pdf.Answer("a3 text"))
    ex = quest2pdf.Exam(q1, q2)
    ex.add_path_parent(file_path)

    assert ex.questions[0].image == Path()
    assert ex.questions[0].answers[0].image == file_path.parent / image
    assert ex.questions[0].answers[1].image == file_path.parent / image
    assert ex.questions[1].image == file_path.parent / image
    assert ex.questions[1].answers[0].image == Path()


def test_exam_add_path_parent2(tmp_path):
    image = Path("images/image.png")
    folder_path = tmp_path
    q1 = quest2pdf.question.Question("q1 text", "")
    q1.answers = (
        quest2pdf.question.Answer("a1 text", image),
        quest2pdf.question.Answer("a2 text", image),
    )
    q2 = quest2pdf.question.Question("q2 text", "", image)
    q2.add_answer(quest2pdf.question.Answer("a3 text"))
    ex = quest2pdf.Exam(q1, q2)
    ex.add_path_parent(folder_path)

    assert ex.questions[0].image == Path()
    assert ex.questions[0].answers[0].image == folder_path / image
    assert ex.questions[0].answers[1].image == folder_path / image
    assert ex.questions[1].image == folder_path / image
    assert ex.questions[1].answers[0].image == Path()


def test_exam_load0():
    """test empty iterable
    """
    ex = quest2pdf.Exam()
    ex.load(iter(()))

    assert ex.questions == tuple()


def test_exam_load1():
    """test without setting _attribute_selector
    2 rows -> 2 questions with 2 answers each but second answer image is not provided
    """
    data = (
        dict(
            [
                ("text", "ab"),
                ("subject", "ac"),
                ("image", "ad"),
                ("level", "1"),
                ("a0 text", "ae"),
                ("a0 image", "af"),
                ("a1 text", "ag"),
            ]
        ),
        dict(
            [
                ("text", "ba"),
                ("subject", "bc"),
                ("image", "bd"),
                ("level", "2"),
                ("a0 text", "be"),
                ("a0 image", "bf"),
                ("a1 text", "bg"),
            ]
        ),
    )
    ex = quest2pdf.Exam()
    ex.load(data)

    for i in (0, 1):
        assert ex.questions[i].text == data[i]["text"]
        assert ex.questions[i].subject == data[i]["subject"]
        assert ex.questions[i].image == Path(data[i]["image"])
        assert ex.questions[i].level == int(data[i]["level"])
        assert ex.questions[i].answers[0].text == data[i]["a0 text"]
        assert ex.questions[i].answers[0].image == Path(data[i]["a0 image"])
        assert ex.questions[i].answers[1].text == data[i]["a1 text"]
        assert ex.questions[i].answers[1].image == Path()  # default value

    # third answer of second question is not provided
    with pytest.raises(IndexError):
        _ = ex.questions[1].answers[2]

    # third question is not provided
    with pytest.raises(IndexError):
        _ = ex.questions[2]


def test_exam_load2():
    """test without setting _attribute_selector
    and missing row
    """
    ex = quest2pdf.Exam()
    reader = (dict([]), dict([("A", "What?"), ("B", "topic")]))
    ex.load(reader)

    print(ex)

    assert ex.questions[0].text == "What?"
    assert ex.questions[0].subject == "topic"


def test_exam_load3():
    """test setting _attribute_selector
    """
    data = (
        dict(
            [
                ("A text", "A"),
                ("B text", "B"),
                ("text", "T"),
                ("C text", "A3"),
                ("D text", "A4"),
                ("subject", "S"),
                ("level", 2),
                ("void", ""),
            ]
        ),
    )
    ex = quest2pdf.Exam()
    ex.attribute_selector = (
        "text",
        "subject",
        "void",
        "level",
        "A text",
        "void",
        "B text",
        "void",
        "C text",
    )
    ex.load(data)

    assert ex.questions[0].text == data[0]["text"]
    assert ex.questions[0].subject == data[0]["subject"]
    assert ex.questions[0].image == Path()
    assert ex.questions[0].level == data[0]["level"]
    assert ex.questions[0].answers[0].text == data[0]["A text"]
    assert ex.questions[0].answers[0].image == Path()
    assert ex.questions[0].answers[1].text == data[0]["B text"]
    assert ex.questions[0].answers[1].image == Path()
    assert ex.questions[0].answers[2].text == data[0]["C text"]
    assert ex.questions[0].answers[2].image == Path()

    # no further elements loaded
    with pytest.raises(IndexError):
        _ = ex.questions[0].answers[3]
    with pytest.raises(IndexError):
        _ = ex.questions[1].answers[2]


def test_exam_load4():
    """test setting _attribute_selector
    """
    data = (dict([("text", "T"), ("subject", "S"), ("XXX level", 2), ("void", "")]),)
    ex = quest2pdf.Exam()
    ex.attribute_selector = ("text", "subject", "void", "level")

    with pytest.raises(quest2pdf.Quest2pdfException):
        ex.load(data)


def test_shuffle():
    data = (
        dict(
            [
                ("question", " Q1"),
                ("A", "A1"),
                ("B", "B1"),
                ("C", "C1"),
                ("D", "D1"),
                ("E", "E1"),
                ("void", ""),
            ]
        ),
        dict(
            [
                ("question", "Q2"),
                ("A", "A2"),
                ("B", "B2"),
                ("C", "C2"),
                ("D", "D2"),
                ("E", "E2"),
                ("void", ""),
            ]
        ),
    )
    correct_values = ("D", "A")
    ex = quest2pdf.Exam()
    ex.attribute_selector = (
        "question",
        "void",
        "void",
        "void",
        "A",
        "void",
        "B",
        "void",
        "C",
        "void",
        "D",
        "void",
        "E",
    )
    ex.load(data)
    random.seed(1)
    ex.answers_shuffle()

    for question, value in zip(ex.questions, correct_values):
        assert question.correct_option == value


def test_questions_shuffle(fake_exam):
    """GIVEN exam with five questions
    WHEN questions_shuffle is called (questions order is mixed)
    THEN questions order is changed
    """
    expected_text = ("q3 text", "q4 text", "q5 text", "q1 text", "q2 text")

    ex = fake_exam
    random.seed(1)
    ex.questions_shuffle()

    for i, question in enumerate(ex.questions):
        assert question.text == expected_text[i]


def test_exam_print():
    data = (
        dict(
            [
                ("field A", "A1"),
                ("field B", "A2"),
                ("field C", "T"),
                ("field D", "A3"),
                ("field E", "A4"),
                ("field F", "S"),
                ("field G", 2),
                ("void", ""),
            ]
        ),
    )
    text, q_image, level, a_image = f"text: A1", f"image: .", f"level: 2", f"image: S"
    ex = quest2pdf.Exam()
    ex.attribute_selector = ("field A", "void", "void", "field G", "void", "field F")
    ex.load(data)

    assert text in ex.__str__()
    assert q_image in ex.__str__()
    assert level in ex.__str__()
    assert a_image in ex.__str__()


def test_exam_mcquestion():
    mcquestion1 = quest2pdf.question.Question("mc quest1 text", "subject")
    mcquestion1.answers = (
        quest2pdf.question.Answer("Q1 A1"),
        quest2pdf.question.Answer("Q1 A2"),
        quest2pdf.question.Answer("Q1 A3"),
    )
    mcquestion2 = quest2pdf.question.Question("mc quest2 text", "subject")
    mcquestion2.answers = (
        quest2pdf.question.Answer("Q2 A1"),
        quest2pdf.question.Answer("Q2 A2"),
        quest2pdf.question.Answer("Q2 A3"),
    )

    ex = quest2pdf.Exam(mcquestion1, mcquestion2)

    assert ex.questions[0].answers[1].image == Path()
    assert ex.questions[0].correct_answer.text == "Q1 A1"
    assert ex.questions[1].text == "mc quest2 text"


def test_exam_tfquestion():
    tfquestion1 = quest2pdf.question.Question("mc quest1 text", "subject")
    tfquestion1.answers = (
        quest2pdf.question.TrueFalseAnswer(True),
        quest2pdf.question.TrueFalseAnswer(False),
    )
    tfquestion2 = quest2pdf.question.Question("mc quest2 text", "subject")
    tfquestion2.answers = (
        quest2pdf.question.TrueFalseAnswer(False),
        quest2pdf.question.TrueFalseAnswer(True),
    )

    ex = quest2pdf.Exam(tfquestion1, tfquestion2)

    assert ex.questions[0].answers[1].image == Path()
    assert ex.questions[0].correct_answer.boolean is True
    assert ex.questions[1].text == "mc quest2 text"
    assert ex.questions[1].correct_answer.text == "False"


def test_exam_mixquestion():
    mcquestion = quest2pdf.question.Question("mc quest1 text", "subject")
    mcquestion.answers = (
        quest2pdf.question.Answer("Q1 A1"),
        quest2pdf.question.Answer("Q1 A2"),
        quest2pdf.question.Answer("Q1 A3"),
    )
    tfquestion = quest2pdf.question.Question("mc quest2 text", "subject")
    tfquestion.answers = (
        quest2pdf.question.TrueFalseAnswer(False),
        quest2pdf.question.TrueFalseAnswer(True),
    )

    ex = quest2pdf.Exam(mcquestion, tfquestion)

    assert ex.questions[0].answers[1].image == Path()
    assert ex.questions[0].correct_option == "A"
    assert ex.questions[1].text == "mc quest2 text"
    assert ex.questions[1].correct_answer.text == "False"


def test_from_csv0(tmp_path):
    file_path = tmp_path / "question.csv"
    save_empty_question(file_path)

    ex = quest2pdf.Exam()
    with pytest.raises(quest2pdf.Quest2pdfException):
        ex.from_csv(file_path)


def test_from_csv1(tmp_path):
    file_path = tmp_path / "question.csv"
    save_question_data(file_path)

    ex = quest2pdf.Exam()
    ex.from_csv(file_path)

    assert len(ex.questions) == 1
    assert ex.questions[0].text == "Q"
    assert len(ex.questions[0].answers) == 3
    assert ex.questions[0].answers[2].image == tmp_path / "ci"


def test_from_csv2(tmp_path):
    file_path = tmp_path / "question.csv"
    save_tf_question(file_path)

    ex = quest2pdf.Exam()
    ex.attribute_selector = ("question", "void", "void", "void", "A", "void", "B")
    ex.from_csv(file_path)

    assert ex.questions[0].correct_option == False


def test_copy_exam(fake_exam):
    """GIVEN an exam
    WHEN a copy is made
    THEN the new one is identical"""
    ex = fake_exam
    new_ex = ex.copy()

    import logging

    logging.warning("ex and new ex \n%s\n%s", ex, new_ex)

    for ex_question, new_ex_question in zip(ex.questions, new_ex.questions):
        assert ex_question.text == new_ex_question.text
        assert ex_question.level == new_ex_question.level
        assert ex_question.correct_index == new_ex_question.correct_index
        assert ex_question.correct_option == new_ex_question.correct_option
        for ex_answer, new_ex_answer in zip(
            ex_question.answers, new_ex_question.answers
        ):
            assert ex_answer.text == new_ex_answer.text
            assert ex_answer.image == new_ex_answer.image


def test_copy_exam_add_question(fake_exam):
    """GIVEN a exam  copy
    WHEN a question is added to the copy
    THEN the original number of questions does not change"""
    ex = fake_exam
    ex_questions_len = len(ex.questions)
    new_ex = ex.copy()
    new_ex.add_question(quest2pdf.Question("new"))

    assert len(ex.questions) == ex_questions_len


def test_copy_mix_exam_add_question(fake_mix_exam):
    ex = fake_mix_exam
    ex_questions_len = len(ex.questions)
    new_ex = ex.copy()
    new_ex.add_question(quest2pdf.Question("new"))
    import logging

    assert len(ex.questions) == ex_questions_len


def test_copy_exam_add_answer(fake_exam):
    ex = fake_exam
    question_1_answers_len = len(ex.questions[0].answers)
    new_ex = ex.copy()
    new_ex.questions[0].add_answer(quest2pdf.Answer("q1 a3"))

    assert len(ex.questions[0].answers) == question_1_answers_len


def test_copy_exam_set_correct_answer(fake_exam):
    ex = fake_exam
    question_1_correct_index = ex.questions[1].correct_index
    new_ex = ex.copy()
    new_ex.questions[1].correct_index = question_1_correct_index + 1

    assert ex.questions[1].correct_index == question_1_correct_index


def test_copy_exam_shuffle_answers(fake_exam):
    ex = fake_exam
    ex_correct_answers = tuple(question.correct_index for question in ex.questions)
    new_ex = ex.copy()
    new_ex.answers_shuffle()

    assert (
        tuple(question.correct_index for question in ex.questions) == ex_correct_answers
    )


def test_copy_exam_shuffle_questions(fake_exam):
    ex = fake_exam
    ex_questions = tuple(question.text for question in ex.questions)
    new_ex = ex.copy()
    new_ex.questions_shuffle()

    assert tuple(question.text for question in ex.questions) == ex_questions


def test_print_exam0(tmp_path):
    pdf_magic_no = b"PDF"
    file_path = tmp_path / "Exam"
    ex = quest2pdf.Exam()
    ex.print(file_path)

    try:
        data = file_path.read_bytes()
    except FileNotFoundError:
        assert False, "File not found"

    assert data.find(pdf_magic_no) == 1


def test_print_exam1(tmp_path):
    pdf_magic_no = b"PDF"
    file_path = tmp_path / "Exam"
    q1 = quest2pdf.question.Question("q1 text", "")
    q1.answers = (
        quest2pdf.question.Answer("a1 text"),
        quest2pdf.question.Answer("a2 text"),
    )
    ex = quest2pdf.Exam(q1)
    ex.print(file_path)

    try:
        data = file_path.read_bytes()
    except FileNotFoundError:
        assert False, "File not found"

    assert data.find(pdf_magic_no) == 1


def test_print_exam2(tmp_path):
    """Test if shuttle argument in print, works
    """
    file_path = tmp_path / "Exam"
    q1 = quest2pdf.question.Question("q1 text", "")
    q1.answers = (
        quest2pdf.question.Answer("a1 text"),
        quest2pdf.question.Answer("a2 text"),
    )
    q2 = quest2pdf.question.Question("q2 text", "")
    q2.answers = (
        quest2pdf.question.Answer("a1 text"),
        quest2pdf.question.Answer("a2 text"),
        quest2pdf.question.Answer("a3 text"),
        quest2pdf.question.Answer("a4 text"),
    )
    ex = quest2pdf.Exam(q1, q2)
    ex.print(file_path, answers_shuffle=False)

    assert ex.questions[0].correct_index == 0
    assert ex.questions[1].correct_index == 0


def test_print_correction0(tmp_path):
    pdf_magic_no = b"PDF"
    exam_file_path = tmp_path / "Exam"
    correction_file_path = tmp_path / "Correction"
    ex = quest2pdf.Exam()
    ex.print(exam_file_path, correction_file_name=correction_file_path)

    try:
        correction_data = correction_file_path.read_bytes()
    except FileNotFoundError:
        assert False, "Correction file not found"

    assert correction_data.find(pdf_magic_no) == 1


def test_print_correction1(tmp_path):
    pdf_magic_no = b"PDF"
    exam_file_path = tmp_path / "Exam"
    correction_file_path = tmp_path / "Correction"
    q1 = quest2pdf.Question("q1 text", "")
    q1.answers = (quest2pdf.Answer("a1 text"), quest2pdf.Answer("a2 text"))
    ex = quest2pdf.Exam(q1)
    ex.print(exam_file_path, correction_file_name=correction_file_path)

    try:
        correction_data = correction_file_path.read_bytes()
    except FileNotFoundError:
        assert False, "Correction file not found"

    assert correction_data.find(pdf_magic_no) == 1


@pytest.fixture
def dummy_exam():
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


def test_print_have_a_look(tmp_path, dummy_exam):
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
    ex = dummy_exam
    folder = image_tmp_folder
    ex.add_path_parent(folder)
    ex.print(exam_file_path, correction_file_name=correction_file_path)

    subprocess.Popen(["evince", str(exam_file_path)])
    subprocess.call(["evince", str(correction_file_path)])

    answer = fd_input("Is it correct (y)? ")
    assert answer == "y\n"


def test_serialize_empty():
    ex = quest2pdf.Exam()
    serial = SerializeExam(ex)

    assert list(serial.assignment()) == []
    assert list(serial.correction()) == []


def test_serialize_assignment(fake_exam):
    ex = fake_exam
    serial = SerializeExam(ex)
    generator = serial.assignment()

    assert next(generator) == Item(ItemLevel.top, "q1 text", pathlib.Path("q1 image"))
    _ = next(generator)
    assert next(generator) == Item(ItemLevel.sub, "q1 a2", pathlib.Path())
    _ = (
        next(generator),
        next(generator),
        next(generator),
        next(generator),
        next(generator),
    )
    assert next(generator) == Item(ItemLevel.top, "q5 text", pathlib.Path("q5 image"))
    with pytest.raises(StopIteration):
        next(generator)


def test_serialize_assignment_shuffle_sub(fake_exam):
    ex = fake_exam
    serial = SerializeExam(ex, shuffle_sub=True)
    random.seed(0)
    generator = serial.assignment()

    assert next(generator) == Item(ItemLevel.top, "q1 text", pathlib.Path("q1 image"))
    assert next(generator) == Item(ItemLevel.sub, "q1 a1", pathlib.Path())
    assert next(generator) == Item(ItemLevel.sub, "q1 a2", pathlib.Path())
    assert next(generator) == Item(ItemLevel.top, "q2 text", pathlib.Path("q2 image"))
    assert next(generator) == Item(ItemLevel.sub, "q2 a1", pathlib.Path())
    assert next(generator) == Item(ItemLevel.sub, "q2 a2", pathlib.Path())


def test_serialize_correction(fake_exam):
    ex = fake_exam
    serial = SerializeExam(ex.questions)
