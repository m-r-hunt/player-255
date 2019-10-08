import unittest
import edn_format


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
