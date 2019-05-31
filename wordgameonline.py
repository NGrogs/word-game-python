from flask import Flask, render_template, request, session, redirect, url_for
import datetime
import random
import pickle
from collections import Counter

app = Flask(__name__)


@app.route('/')
def index():

    session['start'] = datetime.datetime.now()

    with open("words.txt") as w:
        rawdata = w.read()
        rawdata = rawdata.split("\n")
        while True:
            bigWord = random.choice(rawdata).lower()
            if not(len(bigWord) <= 7):
                session['bigWord'] = bigWord
                break

    return render_template('wordgame.html',
                            big_Word = session['bigWord'],
                            the_title = 'Word Game')


@app.route('/result', methods=['POST'])
def results():

    if request.method == 'POST':

        # create list for each of the fail conditions
        session['duplicates'] = []
        session['wordNotInDictionary'] = []
        session['lettersNotInWord'] = []
        session['lettersOverUsed'] = []
        session['wordShort'] = []
        session['wordSame'] = []
        session['not7'] = ""

        # check word is at least 3 long
        def checkLength(w):
            if(len(w) < 3):
                session['wordShort'].append(w)
                return True
            # print nothing
            return False

        # check word != bigword
        def checkEqual(w, b):
            if(w == b):
                session['wordSame'].append(w)
                return True
            # print nothing
            return False

        # check if the letters in word are in bigword
        def checkLetter(w, b):

            cb = Counter(b)
            cw = Counter(w)

            for letter in cw:
                if(letter in cb):
                    # if letter is used more than it can be
                    if(cw[letter] > cb[letter]):
                        session['lettersOverUsed'].append(letter)
                        return True
                else:
                    # will retrun if a letter isnt in big word
                    session['lettersNotInWord'].append(letter)
                    return True

            # will return false if no problems
            return False
            print(b)

        # check the word is in dictionary
        def checkDictionary(w, r):
            if w not in r:
                session['wordNotInDictionary'].append(w)
                return True
            # print nothong
            return False

        # check if 2 words are the same def checkDuplicate(s):
        def checkDuplicate(userIn):
            newSet = []
            for word in userIn:
                newSet.append(word)

            newSet = set(newSet)

            cw = Counter(userIn)
            for word in userIn:
                if cw[word] > 1:
                    session['duplicates'].append(word)

            if(len(newSet) < 7):
                return True
            return False

        # main body
        session['end'] = datetime.datetime.now()
        timeScore = str(session['end'] - session['start'])[2:]
        timeScore = timeScore.replace(':', '')
        session['timeScore'] = timeScore[2:]

        with open("words.txt") as w:
            rawdata = w.read()
            rawdata = rawdata.split("\n")

        words = request.form['words']
        session['words'] = words

        session['words'] = list(str(session['words']).lower().split(" "))

        session['passed'] = True
        # check there's 7 words
        if len(session['words']) is not 7:
            session['not7'] = "Must have 7 words!"
            session['passed'] = False

        for session['word'] in session['words']:

            if (checkLength(session['word']) is True):
                session['passed'] = False

            if (checkEqual(session['word'], session['bigWord']) is True):
                session['passed'] = False

            if (checkLetter(session['word'], session['bigWord']) is True):
                session['passed'] = False

            if (checkDictionary(session['word'], rawdata) is True):
                session['passed'] = False

        if (checkDuplicate(session['words']) is True):
            session['passed'] = False

        # if fail
        if(session['passed'] is False):
            return redirect(url_for('loser'))

        # if Pass
        if(session['passed'] is True):

           return render_template('result.html',
                                    the_score = session['timeScore'])

    return 'Please use GET or POST.'


@app.route('/loser')
def loser():

    return render_template('loser.html',
                            dupes = session['duplicates'],
                            too_short = session['wordShort'],
                            l_not_in_word = session['lettersNotInWord'],
                            w_not_in_dic = session['wordNotInDictionary'],
                            l_overused = session['lettersOverUsed'],
                            same_as_big = session['wordSame'],
                            not_seven = session['not7']
                            )


@app.route('/winner', methods=['POST'])
def winner():

    if request.method == 'POST':
        session['listOfWinners'] = pickle.load(open("scores.txt", "rb"))
        session['listOfWinners'] = sorted(session['listOfWinners'].items())

        name = request.form['name']
        session['name'] = name

        session['saveThis'] = {float(session['timeScore']): session['name']}
        with open("scores.txt", "rb") as f:
            old = pickle.load(f)
            old.update(session['saveThis'])
        with open("scores.txt", "wb") as f:
            pickle.dump(old, f)

        session['listOfWinners'] = pickle.load(open("scores.txt", "rb"))
        session['listOfWinners'] = sorted(session['listOfWinners'].items())
        session['tempList'] = dict(session['listOfWinners'])
        session['userPos'] = list(session['tempList'].keys()).index(
                                float(session['timeScore'])) + 1

        return render_template('winner.html',
                                    the_name = session['name'],
                                    the_pos = session['userPos'],
                                    list_of_winners = session['listOfWinners'])

    return 'Please use GET or POST.'


@app.route('/scoreboard')
def scoreboard():

    # output the leaderboard
    session['listOfWinners'] = pickle.load(open("scores.txt", "rb"))
    session['listOfWinners'] = sorted(session['listOfWinners'].items())

    # if list too small
    if(len(session['listOfWinners']) < 10):
        for i in range(len(session['listOfWinners'])):
            print(i+1, session['listOfWinners'][i])
    # if list has at least 10
    else:
        for i in range(10):
            print(i+1, session['listOfWinners'][i])

    return render_template('scoreboard.html',
                        list_of_winners = session['listOfWinners'])


if __name__ == '__main__':
    app.secret_key = 'slicknilly'
    app.run(debug=True)
