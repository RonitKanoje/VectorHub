from langsmith import traceable


@traceable(name="TEST_CHILD")
def test_child():
    return "hello"


if __name__ == "__main__":
    test_child()