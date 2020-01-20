import exam
import pytest
from pathlib import Path
import random
import csv


def test_answer_text1():
    a = exam.Answer()
    expected = ""

    assert a.text == expected


def test_answer_text2():
    text = "Roma"
    a = exam.Answer(text)

    assert a.text == text


def test_answer_get():
    text = "my answer"
    a = exam.Answer(text)
    expected_image = Path(".")
    expected_attr_load_sequence = ('text', 'image')
    expected_type_caster_sequence = (str, Path)

    assert a.image == expected_image
    assert a.attr_load_sequence == expected_attr_load_sequence
    assert a.type_caster_sequence == expected_type_caster_sequence


@pytest.mark.parametrize(
    "attribute, expected",
    [
        pytest.param("text", 0.1, marks=pytest.mark.xfail),
        ("image", Path(r"\home")),
        pytest.param("image", r"\home", marks=pytest.mark.xfail),
    ],
)
def test_answer_set(attribute, expected):
    a = exam.Answer()
    try:
        setattr(a, attribute, expected)
    except TypeError:
        assert False

    assert getattr(a, attribute) == expected


def test_answer_load0():
    a = exam.Answer()
    expected = tuple()
    i = iter(expected)
    try:
        a.load_sequentially(i)
    except StopIteration:
        pass

    assert a.text == ""
    assert a.image == Path(".")


def test_answer_load1():
    a = exam.Answer()
    expected = ("Answer text",)
    i = iter(expected)
    try:
        a.load_sequentially(i)
    except StopIteration:
        pass

    assert a.text == expected[0]
    assert a.image == Path(".")


def test_answer_load2():
    a = exam.Answer()
    expected = ("Answer text", r"home/mydir/image.jpg")
    i = iter(expected)
    a.load_sequentially(i)

    assert a.text == expected[0]
    assert a.image == Path(expected[1])


def test_answer_load3():
    a = exam.Answer()
    expected = ("Answer text", "home/mydir/image.jpg", "rest")
    i = iter(expected)
    a.load_sequentially(i)

    assert a.text == expected[0]
    assert a.image == Path(expected[1])
    assert next(i) == expected[2]


def test_question_get_text1():
    q = exam.Question()
    expected = ""

    assert q.text == expected


def test_question_set_text2():
    text = "How old are you?"
    q = exam.Question(text)

    assert q.text == text


@pytest.mark.parametrize(
    "attribute, expected",
    [
        ("image", Path(".")),
        ("subject", ""),
        ("level", 0),
        ("answers", tuple()),
        ("correct_answer", None),
        ("correct_index", None),
        ("correct_letter", None),
        ("attr_load_sequence", ("text", "subject", "image", "level")),
        ("type_caster_sequence", (str, str, Path, int))
    ],
)
def test_question_get(attribute, expected):
    """Test default attribute values
    """
    text = "What's your name?"
    q = exam.Question(text)

    assert getattr(q, attribute) == expected


@pytest.mark.parametrize(
    "attribute, expected",
    [
        pytest.param("text", 0.1, marks=pytest.mark.xfail),
        ("image", Path(r"\home")),
        pytest.param("image", r"\home", marks=pytest.mark.xfail),
        ("subject", "Math"),
        pytest.param("subject", 1000, marks=pytest.mark.xfail),
        ("level", 1000),
        pytest.param("level", 1000.01, marks=pytest.mark.xfail),
    ],
)
def test_question_set(attribute, expected):
    """Test set right and wrong attribute
    """
    q = exam.Question()
    try:
        setattr(q, attribute, expected)
    except TypeError:
        assert False

    assert getattr(q, attribute) == expected


def test_question_answer_add():
    """Test one answer addition
    """
    q = exam.Question("Who are you?")
    a = exam.Answer("That's me.")
    q.add_answer(a)

    assert a in q.answers


def test_question_answer_setter():
    q = exam.Question("Who are you?")
    a = exam.Answer("That's me.")
    q.add_answer(a)
    b = exam.Answer("I do not know.")
    c = exam.Answer("Somebody else.")
    q.answers = (b, c)

    assert a not in q.answers
    assert b in q.answers
    assert c in q.answers


def test_question_answer_correct1():
    """Test correctness of the only
    answer added
    """
    q = exam.Question("Who are you?")
    a = exam.Answer("That's me.")
    q.add_answer(a)

    assert q.correct_answer == a
    assert q.correct_index == 0
    assert q.correct_letter == "A"


def test_question_answer_add2():
    """Test two answers addition
    and correctness
    """
    q = exam.Question("Who are you?")
    a1 = exam.Answer("That's me.")
    a2 = exam.Answer("That's not me.")
    q.add_answer(a1)
    q.add_answer(a2)

    assert q.answers == (a1, a2)
    assert q.correct_index == 0
    assert q.correct_letter == "A"


def test_question_answer_correct2():
    """Test correctness of the last
    answer added when is set to correct
    """
    q = exam.Question("Who are you?")
    a1 = exam.Answer("That's me.")
    a2 = exam.Answer("That's not me.")
    q.add_answer(a2)
    q.add_answer(a1, True)

    assert q.correct_answer == a1


def test_question_answer_correct3():
    """Test ineffectiveness of correct setting
    for the first answer added
    """
    q = exam.Question("Who are you?")
    a1 = exam.Answer("That's me.")
    q.add_answer(a1, False)

    assert q.correct_answer == a1


A1 = exam.Answer("That's me.")
A2 = exam.Answer("That's not me.")
A3 = exam.Answer("That's him")
A4 = exam.Answer("That's her.")


@pytest.mark.parametrize(
    "attribute_set, expected, attribute1_get, expected1, attribute2_get, expected2",
    [
        ("correct_answer", A2, "correct_index", 1, "correct_letter", "B"),
        ("correct_index", 0, "correct_answer", A1, "correct_letter", "A"),
        ("correct_letter", "C", "correct_index", 2, "correct_answer", A3)
    ],
)
def test_question_set_correct(attribute_set, expected,
                              attribute1_get, expected1,
                              attribute2_get, expected2):
    q = exam.Question("Who are you?")
    q.add_answer(A1)
    q.add_answer(A2)
    q.add_answer(A3)
    q.add_answer(A4)

    try:
        setattr(q, attribute_set, expected)
    except TypeError:
        assert False

    assert getattr(q, attribute_set) == expected
    assert getattr(q, attribute1_get) == expected1
    assert getattr(q, attribute2_get) == expected2


def test_question_shuffle():
    q = exam.Question("Who are you?")
    a1 = exam.Answer("That's me.")
    a2 = exam.Answer("That's not me.")
    a3 = exam.Answer("That's him")
    a4 = exam.Answer("That's her.")
    q.add_answer(a1)
    q.add_answer(a2, True)
    q.add_answer(a3)
    q.add_answer(a4)

    assert q.answers == (a1, a2, a3, a4)
    random.seed(1)
    q.shuffle()
    assert q.answers == (a4, a1, a3, a2)
    assert q.correct_answer == a2
    assert q.correct_index == 3
    assert  q.correct_letter == "D"


@pytest.mark.parametrize(
    "iterator, q_text, q_subject",
    [(iter(("q1", "s1")),
      "q1", "s1"),
     (iter(("", "s1")),
      "", "s1")
     ],
)
def test_question_load1(iterator, q_text, q_subject):
    quest = exam.Question()
    quest.load_sequentially(iterator)

    assert quest.text == q_text
    assert quest.subject == q_subject


@pytest.mark.parametrize(
    "iterator, q_text, q_subject, q_image, q_level, a1_text, a1_image, a2_text, a2_image",
    [(iter(("d1", "s1", "i1", 1, "a11", "ai11", "a12", "ai12")),
      "d1", "s1", Path("i1"), 1, "a11", Path("ai11"), "a12", Path("ai12")),
     (iter(("", "s1", "", 2, "a11", "ai11", "", "ai12")),
      "", "s1", Path("."), 2, "a11", Path("ai11"), "", Path("ai12"))
     ],
)
def test_question_load2(iterator, q_text, q_subject, q_image, q_level,
                        a1_text, a1_image, a2_text, a2_image):
    quest = exam.Question()
    quest.load_sequentially(iterator)
    print(quest.answers)

    assert quest.text == q_text
    assert quest.subject == q_subject
    assert quest.image == q_image
    assert quest.answers[0].text == a1_text
    assert quest.answers[0].image == a1_image
    assert quest.answers[1].text == a2_text
    assert quest.answers[1].image == a2_image


def test_question_load3():
    quest = exam.Question()
    sequence = ("Text", "Subject", "dir/ec/tor/y", 1, "Answer")
    iterator = iter(sequence)
    quest.load_sequentially(iterator)

    assert quest.text == sequence[0]
    assert quest.subject == sequence[1]
    assert quest.image == Path(sequence[2])
    assert quest.level == sequence[3]
    assert quest.answers[0].text == sequence[4]
    assert quest.answers[0].image == Path(".")


@pytest.fixture
def set_questions():
    return (exam.Question(),
            exam.Question("Who?"),
            exam.Question("What?"),
            exam.Question("When?"))


def test_exam(set_questions):
    ex = exam.Exam()

    assert ex.questions == tuple()


def test_exam_init(set_questions):
    ex1 = exam.Exam(set_questions[1])
    ex2 = exam.Exam(set_questions[1],
                    set_questions[2])

    assert ex1.questions == (set_questions[1],)
    assert ex2.questions == (set_questions[1],
                             set_questions[2])


def test_exam_add_question1(set_questions):
    ex = exam.Exam()
    ex.add_question(set_questions[0])

    assert ex.questions == (set_questions[0],)


def test_exam_add_question2(set_questions):
    ex = exam.Exam()
    ex.add_question(set_questions[2])
    ex.add_question(set_questions[3])

    assert ex.questions == (set_questions[2],
                            set_questions[3])


def test_exam_questions_setter(set_questions):
    ex = exam.Exam()
    ex.add_question(set_questions[1])
    ex.questions = (set_questions[2], set_questions[3])

    assert set_questions[1] not in ex.questions
    assert set_questions[2] in ex.questions
    assert set_questions[3] in ex.questions


def test_exam_load1():
    ex = exam.Exam()
    ex.load(iter(()))

    assert ex.questions == tuple()


def test_exam_load2():
    ex = exam.Exam()
    with open("tests/unit/questions.csv", "r") as fh:
        reader = csv.DictReader(fh)
        ex.load(reader)

    print(ex)
    assert ex.questions[0].text == "ab"
    assert ex.questions[0].subject == "ac"
    assert ex.questions[0].image == Path("ad")
    assert ex.questions[0].level == 1
    assert ex.questions[0].answers[0].text == "ae"
    assert ex.questions[0].answers[0].image == Path("af")
    assert ex.questions[0].answers[1].text == "ag"
    assert ex.questions[1].text == "ba"
    assert ex.questions[1].answers[1].text == "bg"
    assert ex.questions[1].answers[1].image == Path(".")
    with pytest.raises(IndexError):
        ex.questions[1].answers[2].text
    assert ex.questions[2].answers[1].text == "cg"
