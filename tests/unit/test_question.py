import pytest
from pathlib import Path
import random
import quest2pdf
from quest2pdf.utility import safe_int


def test_answer_load0():
    """test empty iterator without attribute:
    StopIteration must not be raised
    """
    a = quest2pdf.Answer()
    a.load_sequentially(iter(tuple()))

    assert True


def test_answer_load1():
    """test empty iterator;
    one attribute is expected
    """
    a = quest2pdf.Answer()
    a._attr_load_sequence = ("A",)
    a._type_caster_sequence = (str,)
    try:
        a.load_sequentially(iter(tuple()))
    except StopIteration:
        pass


def test_answer_load2():
    """test iterator with one item and one
    attribute is expected
    """
    a = quest2pdf.Answer()
    a._attr_load_sequence = ("A",)
    a._type_caster_sequence = (int,)
    test_tuple = ("2",)
    iterator = iter(test_tuple)

    a.load_sequentially(iterator)

    assert a.A == int(test_tuple[0])

    with pytest.raises(StopIteration):
        next(iterator)


def test_answer_load3():
    """test iterator with one item and two
    attribute is expected
    """
    a = quest2pdf.question.Answer()
    a._attr_load_sequence = ("A", "B")
    a._type_caster_sequence = (int, str)
    test_tuple = ("2",)
    iterator = iter(test_tuple)

    with pytest.raises(StopIteration):
        a.load_sequentially(iterator)

    assert a.A == int(test_tuple[0])


def test_answer_load4():
    """test iterator with two items and one
    attribute is expected;
    test last item left in the iterator
    """
    a = quest2pdf.question.Answer()
    a._attr_load_sequence = ("A",)
    a._type_caster_sequence = (int,)
    test_tuple = ("2", "abc")
    iterator = iter(test_tuple)

    a.load_sequentially(iterator)

    assert a.A == int(test_tuple[0])
    assert next(iterator) == test_tuple[1]


def test_answer_load5():
    """test iterator with wrong type
    """
    a = quest2pdf.question.Answer()
    a._attr_load_sequence = ("A",)
    a._type_caster_sequence = (int,)
    iterator = iter("a")

    with pytest.raises(ValueError):
        a.load_sequentially(iterator)


def test_multichoiceanswer_init0():
    """test default arguments
    """
    a = quest2pdf.question.MultiChoiceAnswer()

    assert a.text == ""
    assert a.image == Path()


def test_multichoiceanswer_init1():
    """Test init assignment
    """
    text = "text"
    image = Path("my_pic.jpg")
    a = quest2pdf.question.MultiChoiceAnswer(text, image)

    assert a.text == text
    assert a.image == image


def test_multichoiceanswer_init2():
    """Test wrong arguments
    """
    image = Path()

    with pytest.raises(TypeError):
        quest2pdf.question.MultiChoiceAnswer(image)


def test_multichoiceanswer_init3():
    """Test wrong arguments
    """
    text = "text"
    with pytest.raises(TypeError):
        quest2pdf.question.MultiChoiceAnswer(image=text)


def test_multichoiceanswer_attribute():
    """Test attribute
    """
    a = quest2pdf.question.MultiChoiceAnswer()
    expected_attr_load_sequence = ("text", "image")
    expected_type_caster_sequence = (str, Path)

    assert a.attr_load_sequence == expected_attr_load_sequence
    assert a.type_caster_sequence == expected_type_caster_sequence


@pytest.mark.parametrize(
    "attribute, expected",
    [
        ("test", "abc"),
        pytest.param("text", 0.1, marks=pytest.mark.xfail),
        ("image", Path(r"\home")),
        pytest.param("image", r"\image.png", marks=pytest.mark.xfail),
    ],
)
def test_multichoiceanswer_set(attribute, expected):
    a = quest2pdf.question.MultiChoiceAnswer()
    try:
        setattr(a, attribute, expected)
    except TypeError:
        assert False

    assert getattr(a, attribute) == expected


def test_multichoiceanswer_load():
    a = quest2pdf.question.MultiChoiceAnswer()
    tupl = ("text",)

    with pytest.raises(StopIteration):
        a.load_sequentially(iter(tupl))
    assert a.text == tupl[0]
    assert a.image == Path()


def test_multichoiceanswer_print():
    a = quest2pdf.question.MultiChoiceAnswer()
    text = "Answer text"
    image = "home/mydir/image.jpg"
    i = iter((text, image))
    a.load_sequentially(i)

    assert f"text: {text}" in a.__str__()
    assert f"image: {image}" in a.__str__()


def test_truefalse_init0():
    a = quest2pdf.question.TrueFalseAnswer()

    assert a.boolean is False
    assert a.text == "False"


def test_truefalse_init1():
    a = quest2pdf.question.TrueFalseAnswer(True, Path())

    assert a.boolean is True
    assert a.text == "True"
    assert a.image == Path()


def test_truefalse_init2():
    a = quest2pdf.question.TrueFalseAnswer(True)
    a.boolean = False

    assert a.boolean is False
    assert a.text == "False"


def test_truefalse_init3():
    a = quest2pdf.question.TrueFalseAnswer(1)

    assert a.boolean is True
    assert a.text == "True"


def test_truefalse_init4():
    a = quest2pdf.question.TrueFalseAnswer(0)

    assert a.boolean is False
    assert a.text == "False"


def test_truefalse_attribute():
    a = quest2pdf.question.TrueFalseAnswer(True)
    expected_attr_load_sequence = ("boolean", "image")
    expected_type_caster_sequence = (bool, Path)

    assert a.attr_load_sequence == expected_attr_load_sequence
    assert a.type_caster_sequence == expected_type_caster_sequence


def test_question_init0():
    """Test default arguments
    """
    q = quest2pdf.question.Question()
    expected = ""

    assert q.text == expected


@pytest.mark.parametrize(
    "text, subject, image, level", [("text", "subject", Path(), 0)]
)
def test_question_init2(text, subject, image, level):
    """Test arguments assignments
    """
    q = quest2pdf.question.Question(text, subject=subject, image=image, level=level)

    assert q.text == text
    assert q.subject == subject
    assert q.image == image
    assert q.level == level


@pytest.mark.parametrize(
    "attribute, expected",
    [
        ("image", Path()),
        ("subject", ""),
        ("level", 0),
        ("answers", tuple()),
        ("correct_answer", None),
        ("attr_load_sequence", ("text", "subject", "image", "level")),
        ("_type_caster_sequence", (str, str, Path, safe_int)),
    ],
)
def test_question_get(attribute, expected):
    """Test default attribute values
    """
    text = "What's your name?"
    q = quest2pdf.question.Question(text)

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
    q = quest2pdf.question.Question()
    try:
        setattr(q, attribute, expected)
    except TypeError:
        assert False

    assert getattr(q, attribute) == expected


def test_question_answer_add0():
    """Test one answer addition
    and correctness
    """
    q = quest2pdf.question.Question("Who are you?")
    a = quest2pdf.question.Answer()
    q.add_answer(a)

    assert a in q.answers
    assert q.correct_answer == a
    assert q.correct_index == 0


def test_question_answer_add1():
    """Test two answers addition
    and correctness
    """
    q = quest2pdf.question.Question("Who are you?")
    a1 = quest2pdf.question.Answer()
    a2 = quest2pdf.question.Answer()
    q.add_answer(a1)
    q.add_answer(a2)

    assert q.answers == (a1, a2)
    assert q.correct_answer == a1
    assert q.correct_index == 0


def test_question_answer_setter0():
    """Test tuple addition, overwriting
    previous addition and
    correctness
    """
    q = quest2pdf.question.Question("Who are you?")
    a = quest2pdf.question.Answer()
    q.add_answer(a)
    b = quest2pdf.question.Answer()
    c = quest2pdf.question.Answer()
    q.answers = (b, c)

    assert a not in q.answers
    assert b in q.answers
    assert c in q.answers
    assert q.correct_answer == b
    assert q.correct_index == 0


def test_question_answer_correct0():
    """Test correctness of the last
    answer added when is set to correct
    """
    q = quest2pdf.question.Question("Who are you?")
    a1 = quest2pdf.question.Answer()
    a2 = quest2pdf.question.Answer()
    q.add_answer(a2)
    q.add_answer(a1, True)

    assert q.correct_answer == a1
    assert q.correct_index == 1


def test_question_answer_correct1():
    """Test ineffectiveness of correct setting
    for the first answer added
    """
    q = quest2pdf.question.Question("Who are you?")
    a1 = quest2pdf.question.Answer()
    q.add_answer(a1, False)

    assert q.correct_answer == a1


def test_question_correct_answer_set0():
    """Test set correct answer
    """
    q = quest2pdf.question.Question("Who are you?")
    a1 = quest2pdf.question.Answer()
    a2 = quest2pdf.question.Answer()
    q.add_answer(a1)
    q.add_answer(a2)
    q.correct_answer = a2

    assert q.correct_answer == a2
    assert q.correct_index == 1


def test_question_correct_answer_set1():
    """Test set correct answer index
    """
    q = quest2pdf.question.Question("Who are you?")
    a1 = quest2pdf.question.Answer()
    a2 = quest2pdf.question.Answer()
    q.add_answer(a1)
    q.add_answer(a2)
    q.correct_index = 1

    assert q.correct_answer == a2
    assert q.correct_index == 1


def test_question_correct_answer_set_invalid():
    """Test set invalid correct answer
    """
    q = quest2pdf.question.Question("Who are you?")
    a1 = quest2pdf.question.Answer()
    a2 = quest2pdf.question.Answer()
    a3 = quest2pdf.question.Answer()
    q.add_answer(a1)
    q.add_answer(a2)
    with pytest.raises(ValueError):
        q.correct_answer = a3


def test_question_correct_index_set_invalid():
    """Test set invalid correct answer index
    """
    q = quest2pdf.question.Question("Who are you?")
    a1 = quest2pdf.question.Answer()
    a2 = quest2pdf.question.Answer()
    q.add_answer(a1)
    q.add_answer(a2)
    with pytest.raises(ValueError):
        q.correct_index = 2


A1 = quest2pdf.question.Answer()
A2 = quest2pdf.question.Answer()
A3 = quest2pdf.question.Answer()
A4 = quest2pdf.question.Answer()


@pytest.mark.parametrize(
    "attribute_set, expected, attribute1_get, expected1",
    [
        ("correct_answer", A2, "correct_index", 1),
        ("correct_index", 0, "correct_answer", A1),
        ("correct_index", 2, "correct_answer", A3),
    ],
)
def test_question_set_correct(attribute_set, expected, attribute1_get, expected1):
    """Test correct set by answer and index
    """
    q = quest2pdf.question.Question("Who are you?")
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


def test_question_add_path_parent0():
    """Test whether not existing file path is added to Answer.image
    """
    path = Path("home/my_home/file.txt")
    quest = quest2pdf.question.Question("question text", image=Path())
    image_path = Path("image1.png")
    answer_1 = quest2pdf.question.Answer()
    answer_1.image = image_path
    answer_2 = quest2pdf.question.Answer()
    answer_2.image = Path()
    quest.answers = (answer_1, answer_2)
    quest.add_parent_path(path)

    assert quest.image == Path()
    assert quest.answers[0].image == path.parent / image_path
    assert quest.answers[1].image == Path()


def test_question_add_path_parent1(tmp_path):
    """Test whether existing folder path is added to Answer.image and
    Question.image
    """
    folder_path = tmp_path / "home"
    folder_path.mkdir()
    image_path = Path("image1.png")
    quest = quest2pdf.question.Question("question text", image=image_path)
    answer_1 = quest2pdf.question.Answer()
    answer_1.image = Path()
    answer_2 = quest2pdf.question.Answer()
    answer_2.image = image_path
    quest.answers = (answer_1, answer_2)
    quest.add_parent_path(folder_path)

    assert quest.image == folder_path / image_path
    assert quest.answers[0].image == Path()
    assert quest.answers[1].image == folder_path / image_path


def test_question_load0():
    """Empty iterator.
    """
    tupl = ()
    quest = quest2pdf.question.Question()
    quest.load_sequentially(iter(tupl))

    assert quest.text == ""
    assert quest.subject == ""
    assert quest.image == Path()
    assert quest.level == 0
    assert quest.answers == ()


def test_question_load1():
    """load question text and subject; check for default image, level;
    no answer.
    """
    tupl = ("t1", "s1")
    quest = quest2pdf.question.Question()
    quest.load_sequentially(iter(tupl))

    assert quest.text == tupl[0]
    assert quest.subject == tupl[1]
    assert quest.image == Path()
    assert quest.level == 0
    assert quest.answers == ()


def test_question_load2():
    """load a complete question;
    no answer.
    """
    tupl = ("t1", "s1", "p1", "1")
    quest = quest2pdf.question.Question()
    quest.load_sequentially(iter(tupl))

    assert quest.text == tupl[0]
    assert quest.subject == tupl[1]
    assert quest.image == Path(tupl[2])
    assert quest.level == int(tupl[3])
    assert quest.answers == ()


def test_question_load3():
    """load a complete question; the last item is lost
    because answer does not have any attribute
    """
    tupl = ("t1", "s1", "p1", "1", "a1")
    quest = quest2pdf.question.Question()
    quest.load_sequentially(iter(tupl))

    assert quest.text == tupl[0]
    assert quest.subject == tupl[1]
    assert quest.image == Path(tupl[2])
    assert quest.level == int(tupl[3])
    assert quest.answers == ()


def test_question_load4(monkeypatch):
    """load a complete question and one more item
    for partly fill an answer
    """

    class MonkeyAnswer(quest2pdf.question.Answer):
        def __init__(self):
            super().__init__()
            self._attr_load_sequence = ("text", "image")
            self._type_caster_sequence = (str, str)

    tupl = ("t1", "s1", "p1", "1", "a1")
    quest = quest2pdf.question.Question()
    monkeypatch.setattr(quest, "_answer_type", MonkeyAnswer)
    quest.load_sequentially(iter(tupl))

    assert quest.text == tupl[0]
    assert quest.subject == tupl[1]
    assert quest.image == Path(tupl[2])
    assert quest.level == int(tupl[3])
    assert quest.answers[0].text == tupl[4]


def test_question_load5(monkeypatch):
    """load a complete question and answer
    """

    class MonkeyAnswer(quest2pdf.question.Answer):
        def __init__(self):
            super().__init__()
            self._attr_load_sequence = ("text",)
            self._type_caster_sequence = (str,)

    tupl = ("t1", "s1", "p1", "1", "a1")
    quest = quest2pdf.question.Question()
    monkeypatch.setattr(quest, "_answer_type", MonkeyAnswer)
    quest.load_sequentially(iter(tupl))

    assert quest.text == tupl[0]
    assert quest.subject == tupl[1]
    assert quest.image == Path(tupl[2])
    assert quest.level == int(tupl[3])
    assert quest.answers[0].text == tupl[4]


def test_question_load6(monkeypatch):
    """load a complete question and two answers
    """

    class MonkeyAnswer(quest2pdf.question.Answer):
        def __init__(self):
            super().__init__()
            self._attr_load_sequence = ("text", "image")
            self._type_caster_sequence = (str, str)

    tupl = ("t1", "s1", "p1", "1", "a00", "a01", "a10")
    quest = quest2pdf.question.Question()
    monkeypatch.setattr(quest, "_answer_type", MonkeyAnswer)
    quest.load_sequentially(iter(tupl))

    assert quest.text == tupl[0]
    assert quest.subject == tupl[1]
    assert quest.image == Path(tupl[2])
    assert quest.level == int(tupl[3])
    assert quest.answers[0].text == tupl[4]
    assert quest.answers[0].image == tupl[5]
    assert quest.answers[1].text == tupl[6]


def test_question_print():
    """test __str__ method
    """
    quest = quest2pdf.question.Question()
    quest_text = "Text"
    quest_subject = "Subject"
    quest_image = "dir/ec/tor/y"
    quest_level = 1
    iterator = iter((quest_text, quest_subject, quest_image, quest_level))
    quest.load_sequentially(iterator)

    assert f"text: {quest.text}" in quest.__str__()
    assert f"subject: {quest_subject}" in quest.__str__()
    assert f"image: {quest_image}" in quest.__str__()
    assert f"level: {quest_level}" in quest.__str__()


def test_mcquestion_init0():
    """test init with no answer
    """
    q = quest2pdf.question.MultiChoiceQuest()

    assert q.text == ""
    assert q.subject == ""
    assert q.image == Path()
    assert q.level == 0


def test_mcquestion_init1():
    """test init with no answer
    """
    text, subject, image, level = ("q text", "q subject", Path("image.png"), 2)
    q = quest2pdf.question.MultiChoiceQuest(text, subject, image, level)

    assert q.text == text
    assert q.subject == subject
    assert q.image == image
    assert q.level == level


def test_mcquestion_add():
    """Test add answer
    """
    q = quest2pdf.question.MultiChoiceQuest("Who are you?")
    a1 = quest2pdf.question.MultiChoiceAnswer("That's me.")
    q.add_answer(a1)

    assert q.correct_answer == a1
    assert q.correct_index == 0
    assert q.correct_option == "A"


def test_mcquestion_shuffle1():
    """Test shuffle with one question added
    """
    q = quest2pdf.question.MultiChoiceQuest("Who are you?")
    a1 = quest2pdf.question.MultiChoiceAnswer("That's me.")
    q.add_answer(a1)
    random.seed(1)
    q.shuffle()

    assert q.correct_answer == a1
    assert q.correct_index == 0
    assert q.correct_option == "A"


def test_mcquestion_shuffle2():
    """Test shuffle with more question added
    """
    q = quest2pdf.question.MultiChoiceQuest("Who are you?")
    a1 = quest2pdf.question.MultiChoiceAnswer("That's me.")
    a2 = quest2pdf.question.MultiChoiceAnswer("That's not me.")
    a3 = quest2pdf.question.MultiChoiceAnswer("That's him")
    a4 = quest2pdf.question.MultiChoiceAnswer("That's her.")
    q.add_answer(a1)
    q.add_answer(a2, True)
    q.add_answer(a3)
    q.add_answer(a4)
    random.seed(1)
    q.shuffle()

    assert q.answers == (a4, a1, a3, a2)
    assert q.correct_answer == a2
    assert q.correct_index == 3
    assert q.correct_option == "D"


def test_mcquestion_load0():
    """load question and two answers.
    """
    tupl = ("t", "s", "i", 1, "a1", "ai1", "a", "ai2")
    quest = quest2pdf.question.MultiChoiceQuest()
    quest.load_sequentially(iter(tupl))

    assert quest.text == tupl[0]
    assert quest.subject == tupl[1]
    assert quest.image == Path(tupl[2])
    assert quest.level == tupl[3]
    assert quest.answers != ()
    assert quest.answers[0].text == tupl[4]
    assert quest.answers[0].image == Path(tupl[5])
    assert quest.answers[1].text == tupl[6]
    assert quest.answers[1].image == Path(tupl[7])
    with pytest.raises(IndexError):
        _ = quest.answers[2]


def test_mcquestion_load1():
    """load question and only answer text;
    answer image checked for default value.
    """
    quest = quest2pdf.question.MultiChoiceQuest()
    sequence = ("Text", "Subject", "dir/ec/tor/y", 1, "Answer")
    iterator = iter(sequence)
    quest.load_sequentially(iterator)

    assert quest.text == sequence[0]
    assert quest.subject == sequence[1]
    assert quest.image == Path(sequence[2])
    assert quest.level == sequence[3]
    assert quest.answers[0].text == sequence[4]
    assert quest.answers[0].image == Path(".")
    with pytest.raises(IndexError):
        _ = quest.answers[1]


def test_mcquestion_load2():
    """load question and only some empty answers;
    check empty answers are not loaded.
    """
    quest = quest2pdf.question.MultiChoiceQuest()
    sequence = (
        "Text",
        "Subject",
        "dir/ec/tor/y",
        1,
        "",
        "",
        "Answer",
        "",
        "",
        "",
        "",
        "image.png",
    )
    iterator = iter(sequence)
    quest.load_sequentially(iterator)

    assert quest.text == sequence[0]
    assert quest.subject == sequence[1]
    assert quest.image == Path(sequence[2])
    assert quest.level == sequence[3]
    assert quest.answers[0].text == sequence[6]
    assert quest.answers[0].image == Path(".")
    assert quest.answers[1].text == sequence[10]
    assert quest.answers[1].image == Path(sequence[11])
    with pytest.raises(IndexError):
        _ = quest.answers[2]


def test_tfquestion_init0():
    quest = quest2pdf.question.TrueFalseQuest()

    assert quest.text == ""
    assert quest.subject == ""
    assert quest.image == Path()
    assert quest.level == 0


def test_tfquestion_init1():
    """test init with no answer
    """
    text, subject, image, level = ("q text", "q subject", Path("image.png"), 2)
    quest = quest2pdf.question.TrueFalseQuest(text, subject, image, level)

    assert quest.text == text
    assert quest.subject == subject
    assert quest.image == image
    assert quest.level == level


def test_tfquestion_add0():
    """test add an answer
    """
    answer = quest2pdf.question.TrueFalseAnswer(True)
    quest = quest2pdf.question.TrueFalseQuest()
    quest.add_answer(answer)

    assert quest.answers == (answer,)
    assert quest.correct_answer == answer


def test_tfquestion_add1():
    """test add 2 answer
    """
    true_answer = quest2pdf.question.TrueFalseAnswer(True)
    false_answer = quest2pdf.question.TrueFalseAnswer(False)
    quest = quest2pdf.question.TrueFalseQuest()
    quest.answers = (true_answer, false_answer)

    assert quest.answers == (true_answer, false_answer)
    assert quest.correct_answer == true_answer


def test_tfquestion_add2():
    """test add 2 answer
    """
    true_answer_1 = quest2pdf.question.TrueFalseAnswer(True)
    true_answer_2 = quest2pdf.question.TrueFalseAnswer(True)
    quest = quest2pdf.question.TrueFalseQuest()
    quest.add_answer(true_answer_1)

    with pytest.raises(ValueError):
        quest.add_answer(true_answer_2)


def test_tfquestion_add3():
    """test add 3 answer ... maybe redundant
    """
    true_answer_1 = quest2pdf.question.TrueFalseAnswer(True)
    false_answer = quest2pdf.question.TrueFalseAnswer(False)
    true_answer_2 = quest2pdf.question.TrueFalseAnswer(True)
    quest = quest2pdf.question.TrueFalseQuest()
    quest.add_answer(true_answer_1)

    with pytest.raises(ValueError):
        quest.answers = (true_answer_1, false_answer, true_answer_2)


def test_tfquestion_load0():
    """load question and two answers.
    """
    tupl = ("t", "s", "i", 1, "1", "image", "", "")
    quest = quest2pdf.question.TrueFalseQuest()
    quest.load_sequentially(iter(tupl))

    assert quest.text == tupl[0]
    assert quest.subject == tupl[1]
    assert quest.image == Path(tupl[2])
    assert quest.level == tupl[3]
    assert quest.answers != ()
    assert quest.answers[0].boolean == bool(tupl[4])
    assert quest.answers[0].image == Path(tupl[5])
    assert quest.answers[1].boolean == bool(tupl[6])
    assert quest.answers[1].image == Path(tupl[7])
    with pytest.raises(IndexError):
        _ = quest.answers[2]
