if __name__ == "__main__":

    a = dict()
    a["what"] = "what"
    a["who"] = "Who!"

    b = a.copy()

    print a

    del b["what"]
    print a
    print b