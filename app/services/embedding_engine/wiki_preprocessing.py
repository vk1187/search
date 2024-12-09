from gensim.corpora import WikiCorpus

space = " "
i = 0
inp = "D:\\Wiki-news\\enwikinews-20210201-pages-articles.xml.bz2"
outp = "D:\\Wiki-news\\wiki_dum.en.text"
wiki = WikiCorpus(inp, lemmatize=False, dictionary={})
with open(outp, 'w') as output:
    for text in wiki.get_texts():
        # if six.PY3:
        output.write(space.join(text) + '\n')
        print(space.join(text))

        # #             output.write(' '.join(text).encode('utf-8') + '\n')
        # #   ###another method###
        # #    output.write(
        # #            space.join(map(lambda x:x.decode("utf-8"), text)) + '\n')
        # else:
        #     output.write(space.join(text) + "\n")
        i = i + 1
        if i % 10 == 0:
            # logger.info("Saved " + str(i) + " articles")
            break
