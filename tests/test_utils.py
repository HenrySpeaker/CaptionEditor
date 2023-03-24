import webvtt


def check_identical_vtt_files(file1, file2):
    file1_reader = webvtt.read(file1)
    file2_reader = webvtt.read(file1)

    if len(file1_reader) != len(file2_reader):
        return False

    for i in range(len(file1_reader)):
        if file1_reader[i].text != file2_reader[i].text:
            return False

        if file1_reader[i].start != file2_reader[i].start:
            return False

        if file1_reader[i].end != file2_reader[i].end:
            return False

    return True

    # with open(file1, "r", encoding="utf8") as f1:
    #     file1_contents = f1.read()

    # with open(file2, "r", encoding="utf8") as f2:
    #     file2_contents = f2.read()

    # return file1_contents == file2_contents


def check_identical_contents(file1, file2):
    with open(file1, "r", encoding="utf8") as f1:
        f1_contents = f1.read()

    with open(file2, "r", encoding="utf8") as f2:
        f2_contents = f2.read()

    return f1_contents == f2_contents
