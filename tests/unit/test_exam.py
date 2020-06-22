import pytest
from pathlib import Path
import random

import quest2pdf
from quest2pdf.exam import SerializeExam
from quest2pdf.utility import ItemLevel


def test_exam():
    """test Exam with no args
    """
    ex = quest2pdf.Exam()

    assert ex.questions == tuple()


def test_exam_init():
    """test Exam with one and two arguments
    """
    q1, q2 = (
        quest2pdf.Question("q1 text", "q1 image"),
        quest2pdf.Question("q2 text", "q2 image"),
    )
    ex1 = quest2pdf.Exam(q1)
    ex2 = quest2pdf.Exam(q1, q2)

    assert ex1.questions == (q1,)
    assert ex2.questions == (q1, q2)


def test_exam_questions_setter0():
    """test question set
    """
    q1, q2 = (
        quest2pdf.Question("q1 text", "q1 image"),
        quest2pdf.Question("q2 text", "q2 image"),
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
    q1 = quest2pdf.Question("q1 text", "")
    q1.answers = (
        quest2pdf.Answer("a1 text", image),
        quest2pdf.Answer("a2 text", image),
    )
    q2 = quest2pdf.Question("q2 text", "", image)
    q2.add_answer(quest2pdf.Answer("a3 text"))
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


def test_questions_shuffle(dummy_exam):
    """GIVEN exam with five questions
    WHEN questions_shuffle is called (questions order is mixed)
    THEN questions order is changed
    """
    expected_text = ("q3 text", "q4 text", "q5 text", "q1 text", "q2 text")

    ex = dummy_exam
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


def test_exam_question():
    question1 = quest2pdf.Question("mc quest1 text", "subject")
    question1.answers = (
        quest2pdf.Answer("Q1 A1"),
        quest2pdf.Answer("Q1 A2"),
        quest2pdf.Answer("Q1 A3"),
    )
    question2 = quest2pdf.Question("mc quest2 text", "subject")
    question2.answers = (
        quest2pdf.Answer("Q2 A1"),
        quest2pdf.Answer("Q2 A2"),
        quest2pdf.Answer("Q2 A3"),
    )

    ex = quest2pdf.Exam(question1, question2)

    assert ex.questions[0].answers[1].image == Path()
    assert ex.questions[0].correct_answer.text == "Q1 A1"
    assert ex.questions[1].text == "mc quest2 text"


def test_exam_truefalse_question():
    question1 = quest2pdf.TrueFalseQuest("mc quest1 text", "subject")
    question1.answers = (
        quest2pdf.TrueFalseAnswer(True),
        quest2pdf.TrueFalseAnswer(False),
    )
    question2 = quest2pdf.Question("mc quest2 text", "subject")
    question2.answers = (
        quest2pdf.TrueFalseAnswer(False),
        quest2pdf.TrueFalseAnswer(True),
    )

    ex = quest2pdf.Exam(question1, question2)

    assert ex.questions[0].answers[1].image == Path()
    assert ex.questions[0].correct_answer.boolean is True
    assert ex.questions[1].text == "mc quest2 text"
    assert ex.questions[1].correct_answer.text == "False"


def test_exam_mix_question():
    question = quest2pdf.Question("mc quest1 text", "subject")
    question.answers = (
        quest2pdf.Answer("Q1 A1"),
        quest2pdf.Answer("Q1 A2"),
        quest2pdf.Answer("Q1 A3"),
    )
    truefalse_quest = quest2pdf.TrueFalseQuest("mc quest2 text", "subject")
    truefalse_quest.answers = (
        quest2pdf.TrueFalseAnswer(False),
        quest2pdf.TrueFalseAnswer(True),
    )

    ex = quest2pdf.Exam(question, truefalse_quest)

    assert ex.questions[0].answers[1].image == Path()
    assert ex.questions[0].correct_option == "A"
    assert ex.questions[1].text == "mc quest2 text"
    assert ex.questions[1].correct_answer.text == "False"


def test_from_csv0(empty_question_file):
    ex = quest2pdf.Exam()
    with pytest.raises(quest2pdf.Quest2pdfException):
        ex.from_csv(empty_question_file)


def test_from_csv1(tmp_path, question_data_file):
    ex = quest2pdf.Exam()
    ex.from_csv(question_data_file)

    assert len(ex.questions) == 1
    assert ex.questions[0].text == "Q"
    assert len(ex.questions[0].answers) == 3
    assert ex.questions[0].answers[2].image == tmp_path / "ci"


def test_from_csv2(truefalse_question_file):
    ex = quest2pdf.Exam()
    ex.attribute_selector = ("question", "void", "void", "void", "A", "void", "B")
    ex.from_csv(truefalse_question_file)

    assert ex.questions[0].correct_option == False


def test_copy_exam(dummy_exam):
    """GIVEN an exam
    WHEN a copy is made
    THEN the new one is identical"""
    ex = dummy_exam
    new_ex = ex.copy()

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


def test_copy_exam_add_question(dummy_exam):
    """GIVEN a exam  copy
    WHEN a question is added to the copy
    THEN the original number of questions does not change"""
    ex = dummy_exam
    ex_questions_len = len(ex.questions)
    new_ex = ex.copy()
    new_ex.add_question(quest2pdf.Question("new"))

    assert len(ex.questions) == ex_questions_len


def test_copy_mix_exam_add_question(mix_dummy_exam):
    ex = mix_dummy_exam
    ex_questions_len = len(ex.questions)
    new_ex = ex.copy()
    new_ex.add_question(quest2pdf.Question("new"))

    assert len(ex.questions) == ex_questions_len


def test_copy_exam_add_answer(dummy_exam):
    ex = dummy_exam
    question_1_answers_len = len(ex.questions[0].answers)
    new_ex = ex.copy()
    new_ex.questions[0].add_answer(quest2pdf.Answer("q1 a3"))

    assert len(ex.questions[0].answers) == question_1_answers_len


def test_copy_exam_set_correct_answer(dummy_exam):
    ex = dummy_exam
    question_1_correct_index = ex.questions[1].correct_index
    new_ex = ex.copy()
    new_ex.questions[1].correct_index = question_1_correct_index + 1

    assert ex.questions[1].correct_index == question_1_correct_index


def test_copy_exam_shuffle_answers(dummy_exam):
    ex = dummy_exam
    ex_correct_answers = tuple(question.correct_index for question in ex.questions)
    new_ex = ex.copy()
    new_ex.answers_shuffle()

    assert (
        tuple(question.correct_index for question in ex.questions) == ex_correct_answers
    )


def test_copy_exam_shuffle_questions(dummy_exam):
    ex = dummy_exam
    ex_questions = tuple(question.text for question in ex.questions)
    new_ex = ex.copy()
    new_ex.questions_shuffle()

    assert tuple(question.text for question in ex.questions) == ex_questions


def test_print_exam(tmp_path):
    pdf_magic_no = b"PDF"
    file_path = tmp_path / "Exam"
    ex = quest2pdf.Exam()
    ex.print(file_path)

    try:
        data = file_path.read_bytes()
    except FileNotFoundError:
        assert False, "File not found"

    assert data.find(pdf_magic_no) == 1


def test_print_one_exam(tmp_path, dummy_exam_with_img):
    pdf_magic_no = b"PDF"
    file_path = tmp_path / "Exam.pdf"
    ex = dummy_exam_with_img
    ex.print(file_path)

    try:
        data = file_path.read_bytes()
    except FileNotFoundError:
        assert False, "File not found"

    assert data.find(pdf_magic_no) == 1


def test_print_one_exam_with_wrong_img(tmp_path, dummy_exam):
    file_path = tmp_path / "Exam.pdf"
    ex = dummy_exam
    with pytest.raises(OSError):
        ex.print(file_path)


def test_print_two_exams(tmp_path, dummy_exam_with_img):
    pdf_magic_no = b"PDF"
    file_path = tmp_path / "Exam.pdf"
    ex = dummy_exam_with_img
    n_copies = 2
    ex.print(file_path, n_copies=n_copies)

    for num in range(1, n_copies + 1):
        out_file = tmp_path / f"{file_path.name}_{num}_{n_copies}.{file_path.suffix}"

        try:
            data = out_file.read_bytes()
        except FileNotFoundError:
            assert False, "File not found"

        assert data.find(pdf_magic_no) == 1


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


def test_have_a_look(have_a_look, is_correct):
    """GIVEN a pdf file with some not shuffled question and a correction file
    WHEN they are displayed
    THEN is the layout correct?
    """
    answer = is_correct
    assert answer == "y\n"


def test_serialize_empty():
    ex = quest2pdf.Exam()
    serial = SerializeExam(ex)

    assert list(serial.assignment()) == []
    assert list(serial.correction()) == []


def test_serialize_assignment(dummy_exam):
    ex = dummy_exam
    serial = SerializeExam(ex)
    expected_sequence = [
        "q1 text",
        "q1 a1",
        "q1 a2",
        "q2 text",
        "q2 a1",
        "q2 a2",
        "q3 text",
        "q4 text",
        "q5 text",
    ]
    expected_sequence.reverse()

    for item in serial.assignment():
        assert item.text == expected_sequence.pop()


def test_serialize_assignment_shuffle_sub(big_dummy_exam):
    ex = big_dummy_exam
    serial = SerializeExam(ex, shuffle_sub=True)
    random.seed(0)
    expected_sub_sequence = [
        "1",
        "3",
        "2",
        "3",
        "2",
        "1",
        "True",
        "False",
        "True",
        "False",
        "1",
        "3",
        "2",
        "4",
    ]
    expected_sub_sequence.reverse()

    for item in serial.assignment():
        if item.item_level == ItemLevel.sub:
            assert expected_sub_sequence.pop() in item.text


def test_serialize_assignment_shuffle_top(dummy_exam):
    ex = dummy_exam
    serial = SerializeExam(ex, shuffle_item=True)
    random.seed(0)
    expected_top_sequence = ["3", "2", "1", "5", "4"]
    expected_top_sequence.reverse()

    for item in serial.assignment():
        if item.item_level == ItemLevel.top:
            assert expected_top_sequence.pop() in item.text


def test_serialize_assignment_shuffle_top_n_copies(dummy_exam):
    ex = dummy_exam
    n_copies = 3
    serial = SerializeExam(ex, shuffle_item=True)
    random.seed(0)
    expected_top_sequence = [
        "3",
        "2",
        "1",
        "5",
        "4",
        "1",
        "3",
        "2",
        "4",
        "5",
        "2",
        "1",
        "5",
        "3",
        "4",
    ]
    expected_top_sequence.reverse()

    for _ in range(n_copies):
        for item in serial.assignment():
            if item.item_level == ItemLevel.top:
                assert expected_top_sequence.pop() in item.text


def test_serialize_correction_one_copy(dummy_exam):
    ex = dummy_exam
    serial = SerializeExam(ex)
    for _ in serial.assignment():
        pass
    correction = serial.correction()

    item = next(correction)
    assert item.item_level == ItemLevel.top
    assert "correction" in item.text
    assert "1/1" in item.text


def test_serialize_correction_n_copies(dummy_exam):
    ex = dummy_exam
    n_copies = 4
    expected_num_sequence = list(range(n_copies, 0, -1))
    serial = SerializeExam(ex)
    for _ in range(n_copies):
        for _ in serial.assignment():
            pass

    for item in serial.correction():
        if item.item_level == ItemLevel.top:
            assert f"{expected_num_sequence.pop()}/{n_copies}" in item.text
