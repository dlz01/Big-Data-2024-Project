def LCS(s1: str, s2: str) -> int:
    """
    Finding the length of longest common substring
    return: int
    """
    # abc d
    # ac d
    # initialization: lcs[0][0] = 0
    # lcs[i][j] = lcs[i-1][j-1] + 1 if s1[i]==s2[j] else max(lcs[i][j-1], lcs[i-1][j])
    lcs = [[0 for j in range(len(s2) + 1)] for i in range(len(s1) + 1)]
    for i in range(1, len(s1) + 1):
        for j in range(1, len(s2) + 1):
            if s1[i - 1] == s2[j - 1]:
                lcs[i][j] = lcs[i - 1][j - 1] + 1
            else:
                lcs[i][j] = max(lcs[i - 1][j], lcs[i][j - 1])
    return lcs[-1][-1]

def edit_distance(s1:str, s2:str) -> int:
    return len(s1) + len(s2) - 2 * LCS(s1, s2)
