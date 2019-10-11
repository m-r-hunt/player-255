import unittest
import edn_format
import string
import re


def unednize(l):
    out = []
    for item in l:
        d = {}
        for key, value in item.items():
            d[key.name.replace("-", "_")] = value
        out.append(d)
    return out


class TestUnednize(unittest.TestCase):
    def test_unednize(self):
        self.assertEqual(unednize(edn_format.ImmutableList([])), [])
        self.assertEqual(
            unednize(edn_format.ImmutableList([edn_format.ImmutableDict({})])), [{}]
        )
        self.assertEqual(
            unednize(
                edn_format.ImmutableList(
                    [edn_format.ImmutableDict({}), edn_format.ImmutableDict({})]
                )
            ),
            [{}, {}],
        )
        self.assertEqual(
            unednize(
                edn_format.ImmutableList(
                    [
                        edn_format.ImmutableDict({}),
                        edn_format.ImmutableDict({}),
                        edn_format.ImmutableDict({}),
                        edn_format.ImmutableDict({}),
                        edn_format.ImmutableDict({}),
                    ]
                )
            ),
            [{}, {}, {}, {}, {}],
        )
        self.assertEqual(
            unednize(
                edn_format.ImmutableList(
                    [edn_format.ImmutableDict({edn_format.Keyword("foo"): 123})]
                )
            ),
            [{"foo": 123}],
        )
        self.assertEqual(
            unednize(
                edn_format.ImmutableList(
                    [
                        edn_format.ImmutableDict(
                            {edn_format.Keyword("not-complete"): 123}
                        )
                    ]
                )
            ),
            [{"not_complete": 123}],
        )


# Not at all general purpose, only formats [{}, {}, ...] correctly.
# Mostly matches clojure edn pretty printing in this one case, for good compatibility/diffs.
def dump_edn(l):
    out = "["
    for item in l:
        out += "{"
        for k, v in item.items():
            out += "" + edn_format.dumps(k) + " " + edn_format.dumps(v) + ",\n  "
        if out[-4:] == ",\n  ":
            out = out[:-4]
        out += "}\n "
    if out[-2:] == "\n ":
        out = out[:-2]
    out += "]\n"
    return out


class TestDumpEdn(unittest.TestCase):
    def test_trivial_cases(self):
        self.assertEqual(dump_edn([]), "[]\n")
        self.assertEqual(dump_edn([{}]), "[{}]\n")
        self.assertEqual(dump_edn([{}, {}]), "[{}\n {}]\n")
        self.assertEqual(dump_edn([{}, {}, {}, {}, {}]), "[{}\n {}\n {}\n {}\n {}]\n")

    def test_single_map(self):
        self.assertEqual(dump_edn([{"a": "b"}]), '[{"a" "b"}]\n')
        self.assertEqual(dump_edn([{"a": "b", "c": "d"}]), '[{"a" "b",\n  "c" "d"}]\n')

    def test_multiple_maps(self):
        self.assertEqual(
            dump_edn([{"a": "b"}, {"c": "d"}]), '[{"a" "b"}\n {"c" "d"}]\n'
        )

    def test_edn_keywords(self):
        self.assertEqual(
            dump_edn([{edn_format.Keyword("foo"): edn_format.Keyword("bar")}]),
            "[{:foo :bar}]\n",
        )


def mapScreenshotNames(shortname, screenshots):
    out = []
    for (path, title) in screenshots:
        out.append(
            [
                path,
                "static-assets/images/screenshots/"
                + shortname
                + "-"
                + title
                + "."
                + path.split(".")[-1].lower(),
            ]
        )
    return out


class TestMapScreenshotNames(unittest.TestCase):
    def test_mapScreenshotNames(self):
        self.assertEqual(
            mapScreenshotNames("foo", [["path/to/shot.png", "title"]]),
            [["path/to/shot.png", "static-assets/images/screenshots/foo-title.png"]],
        )
        self.assertEqual(
            mapScreenshotNames("foo", [["path/to/shot.PnG", "title"]]),
            [["path/to/shot.PnG", "static-assets/images/screenshots/foo-title.png"]],
        )
        self.assertEqual(
            mapScreenshotNames(
                "foo", [["path/to/shot.PnG", "title"], ["another/as.gif", "gameplsefd"]]
            ),
            [
                ["path/to/shot.PnG", "static-assets/images/screenshots/foo-title.png"],
                [
                    "another/as.gif",
                    "static-assets/images/screenshots/foo-gameplsefd.gif",
                ],
            ],
        )


def roman_to_int(input):
    """ Convert a Roman numeral to an integer. """
    """ Swiped from Python Cookbook, license:
    Copyright (c) 2001, Paul M. Winkler
All rights reserved.
Redistribution and use in source and binary forms, with or without 
modification, are permitted provided that the following conditions 
are met:
   * Redistributions of source code must retain the above copyright 
     notice, this list of conditions and the following disclaimer. 
   * Redistributions in binary form must reproduce the above
     copyright notice, this list of conditions and the following
     disclaimer in the documentation and/or other materials provided
     with the distribution. 
   * Neither the name of the <ORGANIZATION> nor the names of its 
     contributors may be used to endorse or promote products derived 
     from this software without specific prior written permission. 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS
OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
    if not isinstance(input, type("")):
        raise TypeError
    input = input.upper()
    nums = {"M": 1000, "D": 500, "C": 100, "L": 50, "X": 10, "V": 5, "I": 1}
    sum = 0
    for i in range(len(input)):
        try:
            value = nums[input[i]]
            # If the next place holds a larger number, this value is negative
            if i + 1 < len(input) and nums[input[i + 1]] > value:
                sum -= value
            else:
                sum += value
        except KeyError:
            raise ValueError
    return sum


def filterWord(word):
    if word == "":
        return ""
    if word.isnumeric():
        return word
    if re.fullmatch("[IVX]*", word):
        return str(roman_to_int(word))

    return word[0]


def makeShortname(game, all_shortnames):
    delete_table = str.maketrans("", "", string.punctuation)
    shortname = "".join(
        [
            filterWord(word.translate(delete_table))
            for word in game[edn_format.Keyword("game")].split()
        ]
    ).lower()
    if shortname in all_shortnames:
        n = 2
        while (shortname + str(n)) in all_shortnames:
            n += 1
        return shortname + str(n)
    return shortname


class TestMakeShortname(unittest.TestCase):
    def test_makeShortname(self):
        self.assertEqual(makeShortname({edn_format.Keyword("game"): "word"}, []), "w")
        self.assertEqual(
            makeShortname({edn_format.Keyword("game"): "multiple words"}, []), "mw"
        )
        self.assertEqual(
            makeShortname({edn_format.Keyword("game"): "this ones a repeat"}, ["toar"]),
            "toar2",
        )
        self.assertEqual(
            makeShortname(
                {edn_format.Keyword("game"): "this ones a repeat"}, ["toar", "toar2"]
            ),
            "toar3",
        )
        self.assertEqual(
            makeShortname(
                {edn_format.Keyword("game"): "this ones a repeat"},
                ["toar", "toar2", "toar3", "toar4"],
            ),
            "toar5",
        )
        self.assertEqual(
            makeShortname({edn_format.Keyword("game"): "Maybe Some Caps?"}, []), "msc"
        )
        self.assertEqual(
            makeShortname({edn_format.Keyword("game"): "* - . hello"}, []), "h"
        )
        self.assertEqual(
            makeShortname({edn_format.Keyword("game"): "  hello\t\nasdf"}, []), "ha"
        )
        self.assertEqual(
            makeShortname({edn_format.Keyword("game"): "longnum 12"}, []), "l12"
        )
        self.assertEqual(
            makeShortname({edn_format.Keyword("game"): "roman IV"}, []), "r4"
        )
        self.assertEqual(
            makeShortname({edn_format.Keyword("game"): "a : colon colon: IV:"}, []),
            "acc4",
        )


def updateLastPlayed(played_games, guidata, date):
    game = played_games[-1]
    all_shortnames = [
        game[edn_format.Keyword("shortname")] for game in played_games[:-1]
    ]
    shortname = makeShortname(game, all_shortnames)
    game[edn_format.Keyword("shortname")] = shortname
    game[edn_format.Keyword("rating")] = guidata["rating"]
    game[edn_format.Keyword("status")] = edn_format.Keyword(
        guidata["status"].lower().replace(" ", "-")
    )
    if guidata["status"] == "Other" and guidata["status_note"] != "":
        game[edn_format.Keyword("status-note")] = guidata["status_note"]
    game[edn_format.Keyword("notes")] = guidata["notes"]
    game[edn_format.Keyword("completion-date")] = date
    game[edn_format.Keyword("markdown")] = True
    return shortname
