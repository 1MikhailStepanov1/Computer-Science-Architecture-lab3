# import re
#
# def main():
#     pattern = r"[a-zA-Z]+[\s]*=[\s]*((([a-zA-Z]+|[0-9]+)[\s]*(\%|\\|\+|\-|\*)[\s]*([a-zA-Z]+|[0-9]+))|[0-9]+|[a-zA-Z]+);"
#     str = "n = n + 20;"
#
#     res = re.fullmatch(pattern, str)
#
#     print(res)
#
#     # coding=utf8
#     # the above tag defines encoding for this document and is for Python 2.x compatibility
#
#     # regex = r"[a-zA-Z]+[\s]*=[\s]*((([a-zA-Z]+|[0-9]+)[\s]*(\%|\\|\+|\-|\*)[\s]*([a-zA-Z]+|[0-9]+))|[0-9]+|[a-zA-Z]+);"
#     #
#     # test_str = ("n = n + 20;\n")
#     #
#     # matches = re.finditer(regex, test_str, re.MULTILINE)
#     #
#     # for matchNum, match in enumerate(matches, start=1):
#     #
#     #     print("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum=matchNum, start=match.start(),
#     #                                                                         end=match.end(), match=match.group()))
#     #
#     #     for groupNum in range(0, len(match.groups())):
#     #         groupNum = groupNum + 1
#     #
#     #         print("Group {groupNum} found at {start}-{end}: {group}".format(groupNum=groupNum,
#     #                                                                         start=match.start(groupNum),
#     #                                                                         end=match.end(groupNum),
#     #                                                                         group=match.group(groupNum)))
#
#     # Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.
#
#
# if __name__ == '__main__':
#     main()
