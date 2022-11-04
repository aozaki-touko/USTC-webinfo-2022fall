import analyzer
import json
import re


class MOVIE:
    def __init__(self, movie: dict):
        try:
            self.names = str(movie['电影名']).split(' ', maxsplit=1)
        except KeyError:
            self.names = []
        try:
            self.director = movie['导演']
        except KeyError:
            self.director=[]
        try:
            self.scriptwriter = movie['编剧']
        except KeyError:
            self.scriptwriter = []
        try:
            self.starring = movie['主演']
        except:
            self.starring = []
        try:
            self.movieType = re.split("[/]", movie['类型'])[:-1]
        except:
            self.movieType = []
        try:
            self.region = re.split("[/]", movie['制片国家/地区'])
        except:
            self.region = []
        try:
            self.language = re.split("[/]", movie['语言'])
        except:
            self.language = []
        try:
            self.otherName = re.split("[/]", movie['又名'])
        except:
            self.otherName = []
        try:
            self.otherName = [re.sub('[\(（](.*?)[）\)]', '', i) for i in self.otherName]
        except:
            self.otherName = []
        try:
            self.imdb = movie['IMDb']
        except:
            self.imdb = []
        try:
            self.story = movie['剧情简介']
        except:
            self.story = []
    # use to collect information
    def returnWords(self):
        words = []
        words += self.names + self.director + self.scriptwriter + self.starring + self.movieType + self.region + self.language + self.otherName
        words.append(self.imdb)
        parser = analyzer.Parser(self.story)
        w, freq = parser.process_word()
        words += w
        if [] in words:
            words.remove([])
        return list(set(words))


class BOOK:
    def __init__(self, book: dict):
        # 统计书名、作者、出版社、(原作名、译者)、ISBN、内容简介、作者简介
        try:
            self.name = book['书名']
        except:
            self.name = []
        try:
            self.writer = re.sub(" ", '', book['作者'])
            self.writer = re.sub("\[.*?\]", '', self.writer)
        except:
            self.writer = []
        try:
            self.press = book['出版社']
        except:
            self.press = []
        try:
            self.originName = book['原作名']
            self.translator = book['译者']
        except KeyError:
            self.originName = []
            self.translator = []
        try:
            self.ISBN = book['ISBN']
        except:
            self.ISBN =[]
        try:
            self.content = book['内容简介']
        except:
            self.content = ""
        try:
            self.writerContent = book['作者简介']
        except:
            self.writerContent = ""
    def return_word(self):
        words = [self.name, self.writer, self.press, self.ISBN]
        try:
            if self.originName is not None and self.translator is not None:
                words.append(self.originName)
                words.append(self.translator)
        except:
            pass
        content_parser = analyzer.Parser(self.content)
        writer_parser = analyzer.Parser(self.writerContent)
        w1, freq = content_parser.process_word()
        w2, freq = writer_parser.process_word()
        words+= w1+w2
        while [] in words:
            words.remove([])
        return list(set(words))


class Plconstructor:
    book_data: dict
    movie_data: dict
    PostList: dict

    def __init__(self):
        self.book_data = {}
        self.movie_data = {}
        self.PostList = {}  # 倒排表 结构为 词项:[文档号],按文档号排即可，跳表指针不设置
        self.wordMap = {}  # 用于记录词项在倒排表中的索引
        self.count = 0
        self.booknum = 0
        self.movienum = 0

    def read_book_json(self, filename="../dataset/book.json"):
        self.book_data = readfrom_file(filename)
        pass

    def analyze_book(self):
        books = self.book_data['书籍']
        self.count = 0
        for book in books:
            print("now processing book:",book['书名'],self.count)
            temp = BOOK(book)
            words = temp.return_word()
            for word in words:
                if word in self.PostList:
                    self.PostList[word].append(self.count)
                else:
                    self.PostList[word] = [self.count]
            self.count+=1

    def read_movie_json(self, filename="../dataset/movie.json"):
        self.movie_data = readfrom_file(filename)
        #self.temp = self.movie_data['电影']['舒克和贝塔']

    def analyze_movie(self):
        #这个函数用于构建倒排表
        movies = self.movie_data['电影']
        for movie in movies:
            print("now processing movie:", movie['电影名'],self.count)
            temp = MOVIE(movie)
            words = temp.returnWords()
            for word in words:
                if word in self.PostList:
                    self.PostList[word].append(self.count)
                    # 这里的count代表在json中的序号
                else:
                    self.PostList[word] = [self.count]
            self.count += 1

    def construct_wordMap(self):
        #这个函数用于构建索引向倒排表项的映射
        count = 0
        for word in self.PostList.keys():
            self.wordMap[word] = count
            count += 1

    def movie_process(self):
        self.read_movie_json()
        self.analyze_movie()
        self.construct_wordMap()
        with open("../dataset/movie_word.json",'w',encoding="UTF-8") as mw:
            mw.write(json.dumps(self.wordMap,indent=4,ensure_ascii=False))
        with open("../dataset/movie_post.json",'w',encoding="UTF-8") as mp:
            mp.write(json.dumps(self.PostList,indent=4,ensure_ascii=False))
        self.count = 0
        self.PostList={}
        self.wordMap={}
        print("success")

    def book_process(self):
        self.read_book_json()
        self.analyze_book()
        self.construct_wordMap()
        with open("../dataset/book_word.json",'w',encoding="UTF-8") as bw:
            bw.write(json.dumps(self.wordMap,indent=4,ensure_ascii=False))
        with open("../dataset/book_post.json",'w',encoding="UTF-8") as bp:
            bp.write(json.dumps(self.PostList,indent=4,ensure_ascii=False))
        self.count = 0
        self.PostList={}
        self.wordMap = {}
        pass

def readfrom_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        json_data = json.load(file)
    return json_data

if __name__ == "__main__":
    constructor = Plconstructor()
    constructor.book_process()
    constructor.movie_process()
