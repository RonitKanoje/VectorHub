from langsmith import traceable

@traceable
def test():
    return "hello"



if __name__ == "__main__":
    test()