import json


class SearchEngine:
    # use LR(1) analyzer
    # E -> T OR E | T
    # T -> F AND T | F
    # F -> (E) | NOT F | word
    def __init__(self):
        self.bookWordMapPath = "../dataset/book_word.json"
        self.bookPostPath = "../dataset/book_post.json"
        self.movieWordMapPath = "../dataset/movie_word.json"
        self.moviePostPath = "../dataset/movie_post.json"
        self.movieMapPath = "../dataset/movie_map.json"
        self.bookMapPath = "../dataset/book_map.json"

        with open(self.movieWordMapPath, 'r', encoding="utf-8") as mw:
            self.movieWordMap = json.load(mw)

        with open(self.moviePostPath, 'r', encoding="utf-8") as mp:
            self.moviePostList = json.load(mp)
            self.moviePostList = list(self.moviePostList.values())
         #   print(1)

        with open(self.bookWordMapPath, 'r', encoding="utf-8") as bw:
            self.bookWordMap = json.load(bw)

        with open(self.bookPostPath, 'r', encoding="utf-8") as bp:
            self.bookPostList = json.load(bp)
            self.bookPostList = list(self.bookPostList.values())

        with open(self.movieMapPath, 'r', encoding="utf-8") as mm:
            self.movieMap = json.load(mm)

        with open(self.bookMapPath, 'r', encoding="utf-8") as bm:
            self.bookMap = json.load(bm)

        self.booknum = len(self.bookMap)
        self.bookwordnum = len(self.bookPostList)
        self.movienum = len(self.movieMap)
        self.moviewordnum = len(self.moviePostList)

        print("init success")

    def search(self, intends: str, pattern: str):
        self.token = intends.replace("（", "(").replace("）", ")").replace("(", " ( ").replace(")", " ) ").split()
        self.ptr = 0
        self.token.append("$")
        self.searchmode = pattern
        self.doc_num = self.E()[0]
        doc_name = []
        if pattern == "book":
            for each in self.doc_num:
                doc_name.append(self.bookMap[str(each)])
            for doc in doc_name:
                print(doc)
        else:
            for each in self.doc_num:
                doc_name.append(self.movieMap[str(each)])
            for doc in doc_name:
                print(doc)
        #return doc_name

    def E(self) -> tuple:
        # E -> T OR E | T
        # 返回一个元组,index=0，合并完的倒排表.index=1，是否是合法的
        T = self.T()
        if not T[1]:
            return ([], False)
        elif self.token[self.ptr].lower() == "or" or self.token[self.ptr] == "或":
            self.ptr += 1
            E = self.E()
            return (SearchEngine.OR(T[0], E[0]), True)
        else:
            return (T[0], True)

    def T(self) -> tuple:
        # T -> F AND T | F
        F = self.F()
        if not F[1]:
            return ([], False)
        elif self.token[self.ptr].lower() == "and" or self.token[self.ptr] == "和":
            self.ptr += 1
            T = self.T()
            return (SearchEngine.AND(F[0], T[0]), True)
        else:
            return (F[0], True)

    def F(self) -> tuple:
        # F -> (E) | NOT F | word
        if self.token[self.ptr].lower() == "not":
            self.ptr+=1
            F = self.F()
            return self.NOT(F[0]),True
        if self.token[self.ptr]=="(":
            self.ptr+=1
            E = self.E()
            if self.token[self.ptr] != ')':
                return ([],False)
            self.ptr+=1
            return (E[0],True)
        else:
            L1=self.getList(self.token[self.ptr])
            self.ptr+=1
            return (L1,True)

    def getList(self, word):
        # 需要做同义词
        if self.searchmode == "book":
            if word in self.bookWordMap:
                word_id = self.bookWordMap[word]
                postList = self.bookPostList[word_id]
                return postList
            else:
                print("word:" + word + "not in list")
                return []
        elif self.searchmode == "movie":
            if word in self.movieWordMap:
                word_id = self.movieWordMap[word]
                postList = self.moviePostList[word_id]
                return postList
            else:
                print("word:" + word + "not in list")
                return []

    @staticmethod
    def AND(L1: list, L2: list):
        # 加入相同项
        res = []
        idx1 = idx2 = 0
        len1 = len(L1)
        len2 = len(L2)
        while True:
            if idx1 == len1 or idx2 == len2:
                break
            elif L1[idx1] == L2[idx2]:
                res.append(L1[idx1])
                idx1 += 1
                idx2 += 1
            elif L1[idx1] < L2[idx2]:
                idx1 += 1
            else:
                idx2 += 1
        return res

    @staticmethod
    def OR(L1: list, L2: list):
        # 加入所有项，且相同项只要一个
        res = []
        idx1 = idx2 = 0
        len1 = len(L1)
        len2 = len(L2)
        while idx1 != len1 and idx2 != len2:
            if L1[idx1] == L2[idx2]:
                res.append(L1[idx1])
                idx1 += 1
                idx2 += 1
            elif L1[idx1] < L2[idx2]:
                res.append(L1[idx1])
                idx1 += 1
            else:
                res.append(L2[idx2])
                idx2 += 1
        if idx1 < len1:
            res += L1[idx1:]
        if idx2 < len2:
            res += L2[idx2:]
        return res

    def NOT(self, L: list):
        if self.searchmode == "book":
            total = list(range(self.booknum))
            return [x for x in total not in L]
        else:
            total = list(range(self.movienum))
            return [x for x in total not in L]


if __name__ == "__main__":
    se = SearchEngine()
    while True:
        mode = input("输入查找模式:book/movie:")
        searchItem = input("输入你想查找的序列:")
        se.search(searchItem,mode)
        c=input("你还要查找吗?是则输入1,否输入0:")
        if c =='0':
            break
