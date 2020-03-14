from bottle import (
    route, run, template, request, redirect
)
import ipaddress

from scraputils import get_news
from db import News, session
from bayes import NaiveBayesClassifier


@route("/news")
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template('news_template', rows=rows)


@route("/add_label/")
def add_label():

    s = session()
    lebel = request.query['label']
    id = request.query['id']
    mark = s.query(News).filter(News.id == id).first()
    mark.label = lebel
    s.commit()
    redirect("/news")


@route("/update")
def update_news():
    s = session()
    base = s.query(News).all()
    new_news = get_news('https://news.ycombinator.com/newest', 1)
    for i in new_news:
        for j in base:
            if (i['title'] == j.title) and (i['author'] == j.author):
                break
            else:
                news = News(title=i['title'],
                            author=i['author'],
                            url=i["url"],
                            comments=i['comments'],
                            points=i['points'])
                s.add(news)
                s.commit()

    redirect("/news")


@route("/classify")
def classify_news():
    s = session()

    classif = NaiveBayesClassifier()
    train_news = s.query(News).filter(News.label is not None).options(load_only("title", "label")).all()

    x_train = [row.title for row in train_news]
    y_train = [row.label for row in train_news]

    classif.fit(x_train, y_train)
    test_news = s.query(News).filter(News.label is None).all()

    x = [row.title for row in test_news]
    labels = classif.predict(x)

    good = [test_news[i] for i in range(len(test_news)) if labels[i] == 'good']

    maybe = [test_news[i] for i in range(len(test_news)) if labels[i] == 'maybe']

    never = [test_news[i] for i in range(len(test_news)) if labels[i] == 'never']

    return template('recommendations_template',
                    {'good': good, 'never': never, 'maybe': maybe})


if __name__ == "__main__":
    run(host="localhost", port=8080)

