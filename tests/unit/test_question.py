import pytest
from pathlib import Path
import random
import quest2pdf
from quest2pdf.utility import safe_int


def test_answer_load_empty():
    """test empty iterator
    """
    a = quest2pdf.Answer()
    a._attr_load_sequence = ("A",)
    a._type_caster_sequence = (str,)
    try:
        a.load_sequentially(iter(tuple()))
    except StopIteration:
        pass


def test_answer_load_one_item0():
    """test iterator with one item
    """
    a = quest2pdf.Answer()
    a._attr_load_sequence = ("text",)
    a._type_caster_sequence = (str,)
    test_tuple = ("x",)
    iterator = iter(test_tuple)

    a.load_sequentially(iterator)

    assert a.text == str(test_tuple[0])

    with pytest.raises(StopIteration):
        next(iterator)


def test_answer_load_one_item1():
    """test iterator with one item,
    two attributes
    """
    a = quest2pdf.Answer()
    a._attr_load_sequence = ("text", "image")
    a._type_caster_sequence = (str, Path)
    test_tuple = ("x",)
    iterator = iter(test_tuple)

    with pytest.raises(StopIteration):
        a.load_sequentially(iterator)

    assert a.text == str(test_tuple[0])


def test_answer_load_two_items0():
    """test iterator with two items,
     one attribute; test last item left in the iterator
    """
    a = quest2pdf.Answer()
    a._attr_load_sequence = ("text",)
    a._type_caster_sequence = (str,)
    test_tuple = ("a", "abc")
    iterator = iter(test_tuple)

    a.load_sequentially(iterator)

    assert a.text == str(test_tuple[0])
    assert next(iterator) == test_tuple[1]


def test_answer_init_default():
    """test default arguments
    """
    a = quest2pdf.Answer()

    assert a.text == ""
    assert a.image == Path()


def test_answer_init():
    """Test init assignment
    """
    text = "text"
    image = Path("my_pic.jpg")
    a = quest2pdf.Answer(text, image)

    assert a.text == text
    assert a.image == image


def test_answer_init_wrong_test():
    """Test wrong arguments
    """
    image = Path()

    with pytest.raises(TypeError):
        quest2pdf.Answer(image)


def test_answer_init_wrong_image():
    """Test wrong arguments
    """
    text = "text"
    with pytest.raises(TypeError):
        quest2pdf.Answer(image=text)


def test_answer_attributes():
    """Test sequence attributes
    """
    a = quest2pdf.Answer()
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
def test_answer_set(attribute, expected):
    a = quest2pdf.Answer()
    try:
        setattr(a, attribute, expected)
    except TypeError:
        assert False

    assert getattr(a, attribute) == expected


def test_answer_load():
    a = quest2pdf.Answer()
    test_tuple = ("text",)

    with pytest.raises(StopIteration):
        a.load_sequentially(iter(test_tuple))
    assert a.text == test_tuple[0]
    assert a.image == Path()


def test_answer_print():
    a = quest2pdf.Answer()
    text = "Answer text"
    image = "home/mydir/image.jpg"
    i = iter((text, image))
    a.load_sequentially(i)

    assert f"text: {text}" in a.__str__()
    assert f"image: {image}" in a.__str__()


def test_truefalse_answer_empty():
    a = quest2pdf.TrueFalseAnswer()

    assert a.boolean is False
    assert a.text == "False"


def test_truefalse_answer_init_two_args():
    a = quest2pdf.TrueFalseAnswer(True, Path())

    assert a.boolean is True
    assert a.text == "True"
    assert a.image == Path()


def test_truefalse_answer_init_one_arg():
    a = quest2pdf.TrueFalseAnswer(True)
    a.boolean = False

    assert a.boolean is False
    assert a.text == "False"


def test_truefalse_answer_init_num_arg():
    a = quest2pdf.TrueFalseAnswer(1)

    assert a.boolean is True
    assert a.text == "True"


def test_truefalse_answer_init_num_arg0():
    a = quest2pdf.TrueFalseAnswer(0)

    assert a.boolean is False
    assert a.text == "False"


def test_truefalse_answer_attribute():
    a = quest2pdf.TrueFalseAnswer(True)
    expected_attr_load_sequence = ("boolean", "image")
    expected_type_caster_sequence = (bool, Path)

    assert a.attr_load_sequence == expected_attr_load_sequence
    assert a.type_caster_sequence == expected_type_caster_sequence


def test_question_default():
    """Test default arguments
    """
    q = quest2pdf.Question()
    expected = ""

    assert q.text == expected


@pytest.mark.parametrize(
    "text, subject, image, level", [("text", "subject", Path(), 0)]
)
def test_question_init(text, subject, image, level):
    """Test arguments assignments
    """
    q = quest2pdf.Question(text, subject=subject, image=image, level=level)

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
    q = quest2pdf.Question(text)

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
    q = quest2pdf.Question()
    try:
        setattr(q, attribute, expected)
    except TypeError:
        assert False

    assert getattr(q, attribute) == expected


def test_question_answer_add_one():
    """Test one answer addition
    and correctness
    """
    q = quest2pdf.Question("Who are you?")
    a = quest2pdf.Answer()
    q.add_answer(a)

    assert a in q.answers
    assert q.correct_answer == a
    assert q.correct_index == 0


def test_question_answer_add_two():
    """Test two answers addition
    and correctness
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer()
    a2 = quest2pdf.Answer()
    q.add_answer(a1)
    q.add_answer(a2)

    assert q.answers == (a1, a2)
    assert q.correct_answer == a1
    assert q.correct_index == 0


def test_question_answer_setter():
    """Test tuple addition, overwriting
    previous addition and
    correctness
    """
    q = quest2pdf.Question("Who are you?")
    a = quest2pdf.Answer()
    q.add_answer(a)
    b = quest2pdf.Answer()
    c = quest2pdf.Answer()
    q.answers = (b, c)

    assert a not in q.answers
    assert b in q.answers
    assert c in q.answers
    assert q.correct_answer == b
    assert q.correct_index == 0


def test_question_answer_correct_set():
    """Test correctness of the last
    answer added when set correct
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer()
    a2 = quest2pdf.Answer()
    q.add_answer(a2)
    q.add_answer(a1, True)

    assert q.correct_answer == a1
    assert q.correct_index == 1


def test_question_answer_correct_false():
    """Test ineffectiveness of correct setting
    for the first answer added
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer()
    q.add_answer(a1, False)

    assert q.correct_answer == a1


def test_question_correct_answer_set():
    """Test set correct answer
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer()
    a2 = quest2pdf.Answer()
    q.add_answer(a1)
    q.add_answer(a2)
    q.correct_answer = a2

    assert q.correct_answer == a2
    assert q.correct_index == 1


def test_question_correct_index_set():
    """Test set correct answer index
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer()
    a2 = quest2pdf.Answer()
    q.add_answer(a1)
    q.add_answer(a2)
    q.correct_index = 1

    assert q.correct_answer == a2
    assert q.correct_index == 1


def test_question_correct_answer_invalid():
    """Test set invalid correct answer
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer()
    a2 = quest2pdf.Answer()
    a3 = quest2pdf.Answer()
    q.add_answer(a1)
    q.add_answer(a2)
    with pytest.raises(ValueError):
        q.correct_answer = a3


def test_question_correct_index_invalid():
    """Test set invalid correct answer index
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer()
    a2 = quest2pdf.Answer()
    q.add_answer(a1)
    q.add_answer(a2)
    with pytest.raises(ValueError):
        q.correct_index = 2


A1 = quest2pdf.Answer()
A2 = quest2pdf.Answer()
A3 = quest2pdf.Answer()
A4 = quest2pdf.Answer()


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
    q = quest2pdf.Question("Who are you?")
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
    quest = quest2pdf.Question("question text", image=Path())
    image_path = Path("image1.png")
    answer_1 = quest2pdf.Answer()
    answer_1.image = image_path
    answer_2 = quest2pdf.Answer()
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
    quest = quest2pdf.Question("question text", image=image_path)
    answer_1 = quest2pdf.Answer()
    answer_1.image = Path()
    answer_2 = quest2pdf.Answer()
    answer_2.image = image_path
    quest.answers = (answer_1, answer_2)
    quest.add_parent_path(folder_path)

    assert quest.image == folder_path / image_path
    assert quest.answers[0].image == Path()
    assert quest.answers[1].image == folder_path / image_path


def test_question_load_empty():
    """Empty iterator.
    """
    test_tuple = ()
    quest = quest2pdf.Question()
    quest.load_sequentially(iter(test_tuple))

    assert quest.text == ""
    assert quest.subject == ""
    assert quest.image == Path()
    assert quest.level == 0
    assert quest.answers == ()


def test_question_load_partial():
    """load question text and subject; check for default image, level;
    no answer.
    """
    test_tuple = ("t1", "s1")
    quest = quest2pdf.Question()
    quest.load_sequentially(iter(test_tuple))

    assert quest.text == test_tuple[0]
    assert quest.subject == test_tuple[1]
    assert quest.image == Path()
    assert quest.level == 0
    assert quest.answers == ()


def test_question_load_full():
    """load a complete question;
    no answer.
    """
    test_tuple = ("t1", "s1", "p1", "1")
    quest = quest2pdf.Question()
    quest.load_sequentially(iter(test_tuple))

    assert quest.text == test_tuple[0]
    assert quest.subject == test_tuple[1]
    assert quest.image == Path(test_tuple[2])
    assert quest.level == int(test_tuple[3])
    assert quest.answers == ()


def test_question_load_partial_answer(monkeypatch):
    """load a complete question and one more item
    for partly fill an answer
    """

    class MonkeyAnswer(quest2pdf.Answer):
        def __init__(self):
            super().__init__()
            self._attr_load_sequence = ("text", "image")
            self._type_caster_sequence = (str, str)

    test_tuple = ("t1", "s1", "p1", "1", "a1")
    quest = quest2pdf.Question()
    monkeypatch.setattr(quest, "_answer_type", MonkeyAnswer)
    quest.load_sequentially(iter(test_tuple))

    assert quest.text == test_tuple[0]
    assert quest.subject == test_tuple[1]
    assert quest.image == Path(test_tuple[2])
    assert quest.level == int(test_tuple[3])
    assert quest.answers[0].text == test_tuple[4]


def test_question_load_full_answer(monkeypatch):
    """load a complete question and answer
    """

    class MonkeyAnswer(quest2pdf.Answer):
        def __init__(self):
            super().__init__()
            self._attr_load_sequence = ("text",)
            self._type_caster_sequence = (str,)

    test_tuple = ("t1", "s1", "p1", "1", "a1")
    quest = quest2pdf.Question()
    monkeypatch.setattr(quest, "_answer_type", MonkeyAnswer)
    quest.load_sequentially(iter(test_tuple))

    assert quest.text == test_tuple[0]
    assert quest.subject == test_tuple[1]
    assert quest.image == Path(test_tuple[2])
    assert quest.level == int(test_tuple[3])
    assert quest.answers[0].text == test_tuple[4]


def test_question_load_two_answer(monkeypatch):
    """load a complete question and two answers
    """

    class MonkeyAnswer(quest2pdf.Answer):
        def __init__(self):
            super().__init__()
            self._attr_load_sequence = ("text", "image")
            self._type_caster_sequence = (str, Path)

    test_tuple = ("t1", "s1", "p1", "1", "a00", Path("a01"), "a10")
    quest = quest2pdf.Question()
    monkeypatch.setattr(quest, "_answer_type", MonkeyAnswer)
    quest.load_sequentially(iter(test_tuple))

    assert quest.text == test_tuple[0]
    assert quest.subject == test_tuple[1]
    assert quest.image == Path(test_tuple[2])
    assert quest.level == int(test_tuple[3])
    assert quest.answers[0].text == test_tuple[4]
    assert quest.answers[0].image == test_tuple[5]
    assert quest.answers[1].text == test_tuple[6]


def test_question_print():
    """test __str__ method
    """
    quest = quest2pdf.Question()
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


def test_question_init_empty():
    """test init with no answer
    """
    q = quest2pdf.Question()

    assert q.text == ""
    assert q.subject == ""
    assert q.image == Path()
    assert q.level == 0


def test_question_init_all_args():
    """test init with no answer
    """
    text, subject, image, level = ("q text", "q subject", Path("image.png"), 2)
    q = quest2pdf.Question(text, subject, image, level)

    assert q.text == text
    assert q.subject == subject
    assert q.image == image
    assert q.level == level


def test_question_add_one_answer():
    """Test add answer
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer("That's me.")
    q.add_answer(a1)

    assert q.correct_answer == a1
    assert q.correct_index == 0
    assert q.correct_option == "A"


def test_question_add_two_answers():
    """Test add answer
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer("That's me.")
    a2 = quest2pdf.Answer("That's you.")
    q.add_answer(a1), q.add_answer(a2)
    q.correct_option = "B"

    assert q.correct_answer == a2
    assert q.correct_index == 1
    assert q.correct_option == "B"


def test_question_correct_option():
    """Test add answer
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer("That's me.")
    a2 = quest2pdf.Answer("That's you.")
    q.add_answer(a1), q.add_answer(a2)

    with pytest.raises(ValueError):
        q.correct_option = "X"


def test_question_shuffle_one_answer():
    """Test shuffle with one answer added
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer("That's me.")
    q.add_answer(a1)
    random.seed(1)
    q.shuffle()

    assert q.correct_answer == a1
    assert q.correct_index == 0
    assert q.correct_option == "A"


def test_question_shuffle_more_answers():
    """Test shuffle with more answers added
    """
    q = quest2pdf.Question("Who are you?")
    a1 = quest2pdf.Answer("That's me.")
    a2 = quest2pdf.Answer("That's not me.")
    a3 = quest2pdf.Answer("That's him")
    a4 = quest2pdf.Answer("That's her.")
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


def test_question_load_two_answers():
    """load question and two answers.
    """
    tupl = ("t", "s", "i", 1, "a1", "ai1", "a", "ai2")
    quest = quest2pdf.Question()
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


def test_question_load_partial_answer():
    """load question and only answer text;
    answer image checked for default value.
    """
    quest = quest2pdf.Question()
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


def test_question_load_empty_answer():
    """load question and only some empty answers;
    check empty answers are not loaded.
    """
    quest = quest2pdf.Question()
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


def test_truefalse_question_init_emtpy():
    quest = quest2pdf.TrueFalseQuest()

    assert quest.text == ""
    assert quest.subject == ""
    assert quest.image == Path()
    assert quest.level == 0


def test_truefalse_question_init_full():
    """test init with no answer
    """
    text, subject, image, level = ("q text", "q subject", Path("image.png"), 2)
    quest = quest2pdf.TrueFalseQuest(text, subject, image, level)

    assert quest.text == text
    assert quest.subject == subject
    assert quest.image == image
    assert quest.level == level


def test_truefalse_quest_add_one_answer():
    """test add an answer
    """
    answer = quest2pdf.TrueFalseAnswer(True)
    quest = quest2pdf.TrueFalseQuest()
    quest.add_answer(answer)

    assert quest.answers == (answer,)
    assert quest.correct_answer == answer
    assert quest.correct_index == 0
    assert quest.correct_option == answer.boolean


def test_truefalse_quest_add_two_answers():
    """test add 2 answers
    """
    true_answer = quest2pdf.TrueFalseAnswer(True)
    false_answer = quest2pdf.TrueFalseAnswer(False)
    quest = quest2pdf.TrueFalseQuest()
    quest.answers = (true_answer, false_answer)

    assert quest.answers == (true_answer, false_answer)
    assert quest.correct_answer == true_answer
    assert quest.correct_index == 0
    assert quest.correct_option == true_answer.boolean


def test_truefalse_question_add_two_true():
    """test add true answers
    """
    true_answer_1 = quest2pdf.TrueFalseAnswer(True)
    true_answer_2 = quest2pdf.TrueFalseAnswer(True)
    quest = quest2pdf.TrueFalseQuest()
    quest.add_answer(true_answer_1)

    with pytest.raises(ValueError):
        quest.add_answer(true_answer_2)


def test_truefalse_question_add_answers_correct_set():
    """test add 2 answer
    """
    true_answer = quest2pdf.TrueFalseAnswer(True)
    false_answer = quest2pdf.TrueFalseAnswer(False)
    quest = quest2pdf.TrueFalseQuest()
    quest.add_answer(true_answer)
    quest.add_answer(false_answer, is_correct=True)

    assert quest.correct_answer == false_answer


def test_truefalse_question_add_three_answers():
    """test add 3 answer ... maybe redundant
    """
    true_answer_1 = quest2pdf.TrueFalseAnswer(True)
    false_answer = quest2pdf.TrueFalseAnswer(False)
    true_answer_2 = quest2pdf.TrueFalseAnswer(True)
    quest = quest2pdf.TrueFalseQuest()
    quest.add_answer(true_answer_1)

    with pytest.raises(ValueError):
        quest.answers = (true_answer_1, false_answer, true_answer_2)


def test_truefalse_question_shuffle_empty():
    """test shuffle without answer
    """
    quest = quest2pdf.TrueFalseQuest()

    quest.shuffle()

    assert True


def test_truefalse_question_shuffle():
    """test shuffle for true false question
    """
    false_answer = quest2pdf.TrueFalseAnswer(False)
    true_answer = quest2pdf.TrueFalseAnswer(True)
    quest = quest2pdf.TrueFalseQuest()
    quest.add_answer(false_answer)
    quest.add_answer(true_answer)

    assert quest.answers[1].boolean is True

    quest.shuffle()

    assert quest.answers[0] == true_answer


def test_truefalse_question_load0():
    """load question and two answers.
    """
    tupl = ("t", "s", "i", 1, "1", "image", "", "")
    quest = quest2pdf.TrueFalseQuest()
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
