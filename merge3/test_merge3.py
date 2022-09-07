# Copyright (C) 2005-2011, 2016 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import merge3
import unittest
import sys

if sys.version_info[0] == 3:
    import struct
    int2byte = struct.Struct(">B").pack
    from io import StringIO
else:
    int2byte = chr
    from StringIO import StringIO


def split_lines(t):
    return StringIO(t).readlines()


############################################################
# test case data from the gnu diffutils manual
# common base
TZU = split_lines("""     The Nameless is the origin of Heaven and Earth;
     The named is the mother of all things.

     Therefore let there always be non-being,
       so we may see their subtlety,
     And let there always be being,
       so we may see their outcome.
     The two are the same,
     But after they are produced,
       they have different names.
     They both may be called deep and profound.
     Deeper and more profound,
     The door of all subtleties!
""")

LAO = split_lines("""     The Way that can be told of is not the eternal Way;
     The name that can be named is not the eternal name.
     The Nameless is the origin of Heaven and Earth;
     The Named is the mother of all things.
     Therefore let there always be non-being,
       so we may see their subtlety,
     And let there always be being,
       so we may see their outcome.
     The two are the same,
     But after they are produced,
       they have different names.
""")


TAO = split_lines("""     The Way that can be told of is not the eternal Way;
     The name that can be named is not the eternal name.
     The Nameless is the origin of Heaven and Earth;
     The named is the mother of all things.

     Therefore let there always be non-being,
       so we may see their subtlety,
     And let there always be being,
       so we may see their result.
     The two are the same,
     But after they are produced,
       they have different names.

       -- The Way of Lao-Tzu, tr. Wing-tsit Chan

""")

MERGED_RESULT = split_lines(
    """     The Way that can be told of is not the eternal Way;
     The name that can be named is not the eternal name.
     The Nameless is the origin of Heaven and Earth;
     The Named is the mother of all things.
     Therefore let there always be non-being,
       so we may see their subtlety,
     And let there always be being,
       so we may see their result.
     The two are the same,
     But after they are produced,
       they have different names.
<<<<<<< LAO
=======

       -- The Way of Lao-Tzu, tr. Wing-tsit Chan

>>>>>>> TAO
""")


class TestMerge3(unittest.TestCase):

    def test_no_changes(self):
        """No conflicts because nothing changed"""
        m3 = merge3.Merge3(['aaa', 'bbb'],
                           ['aaa', 'bbb'],
                           ['aaa', 'bbb'])

        self.assertEqual(m3.find_unconflicted(), [(0, 2)])

        self.assertEqual(
                list(m3.find_sync_regions()),
                [(0, 2, 0, 2, 0, 2), (2, 2, 2, 2, 2, 2)])

        self.assertEqual(list(m3.merge_regions()),
                         [('unchanged', 0, 2)])

        self.assertEqual(list(m3.merge_groups()),
                         [('unchanged', ['aaa', 'bbb'])])

    def test_front_insert(self):
        m3 = merge3.Merge3([b'zz'],
                           [b'aaa', b'bbb', b'zz'],
                           [b'zz'])

        # todo: should use a sentinal at end as from get_matching_blocks
        # to match without zz
        self.assertEqual(list(m3.find_sync_regions()),
                         [(0, 1, 2, 3, 0, 1),
                          (1, 1, 3, 3, 1, 1), ])

        self.assertEqual(list(m3.merge_regions()),
                         [('a', 0, 2),
                          ('unchanged', 0, 1)])

        self.assertEqual(list(m3.merge_groups()),
                         [('a', [b'aaa', b'bbb']),
                          ('unchanged', [b'zz'])])

    def test_null_insert(self):
        m3 = merge3.Merge3([],
                           ['aaa', 'bbb'],
                           [])
        # todo: should use a sentinal at end as from get_matching_blocks
        # to match without zz
        self.assertEqual(list(m3.find_sync_regions()),
                         [(0, 0, 2, 2, 0, 0)])

        self.assertEqual(list(m3.merge_regions()),
                         [('a', 0, 2)])

        self.assertEqual(list(m3.merge_lines()),
                         ['aaa', 'bbb'])

    def test_no_conflicts(self):
        """No conflicts because only one side changed"""
        m3 = merge3.Merge3(['aaa', 'bbb'],
                           ['aaa', '111', 'bbb'],
                           ['aaa', 'bbb'])

        self.assertEqual(m3.find_unconflicted(),
                         [(0, 1), (1, 2)])

        self.assertEqual(list(m3.find_sync_regions()),
                         [(0, 1, 0, 1, 0, 1),
                          (1, 2, 2, 3, 1, 2),
                          (2, 2, 3, 3, 2, 2), ])

        self.assertEqual(list(m3.merge_regions()),
                         [('unchanged', 0, 1),
                          ('a', 1, 2),
                          ('unchanged', 1, 2), ])

    def test_append_a(self):
        m3 = merge3.Merge3(['aaa\n', 'bbb\n'],
                           ['aaa\n', 'bbb\n', '222\n'],
                           ['aaa\n', 'bbb\n'])

        self.assertEqual(''.join(m3.merge_lines()),
                         'aaa\nbbb\n222\n')

    def test_append_b(self):
        m3 = merge3.Merge3(['aaa\n', 'bbb\n'],
                           ['aaa\n', 'bbb\n'],
                           ['aaa\n', 'bbb\n', '222\n'])

        self.assertEqual(''.join(m3.merge_lines()),
                         'aaa\nbbb\n222\n')

    def test_append_agreement(self):
        m3 = merge3.Merge3(['aaa\n', 'bbb\n'],
                           ['aaa\n', 'bbb\n', '222\n'],
                           ['aaa\n', 'bbb\n', '222\n'])

        self.assertEqual(''.join(m3.merge_lines()),
                         'aaa\nbbb\n222\n')

    def test_append_clash(self):
        m3 = merge3.Merge3(['aaa\n', 'bbb\n'],
                           ['aaa\n', 'bbb\n', '222\n'],
                           ['aaa\n', 'bbb\n', '333\n'])

        ml = m3.merge_lines(name_a='a',
                            name_b='b',
                            start_marker='<<',
                            mid_marker='--',
                            end_marker='>>')
        self.assertEqual(''.join(ml), '''\
aaa
bbb
<< a
222
--
333
>> b
''')

    def test_insert_agreement(self):
        m3 = merge3.Merge3(['aaa\n', 'bbb\n'],
                           ['aaa\n', '222\n', 'bbb\n'],
                           ['aaa\n', '222\n', 'bbb\n'])

        ml = m3.merge_lines(name_a='a',
                            name_b='b',
                            start_marker='<<',
                            mid_marker='--',
                            end_marker='>>')
        self.assertEqual(''.join(ml), 'aaa\n222\nbbb\n')

    def test_insert_clash(self):
        """Both try to insert lines in the same place."""
        m3 = merge3.Merge3(['aaa\n', 'bbb\n'],
                           ['aaa\n', '111\n', 'bbb\n'],
                           ['aaa\n', '222\n', 'bbb\n'])

        self.assertEqual(m3.find_unconflicted(),
                         [(0, 1), (1, 2)])

        self.assertEqual(list(m3.find_sync_regions()),
                         [(0, 1, 0, 1, 0, 1),
                          (1, 2, 2, 3, 2, 3),
                          (2, 2, 3, 3, 3, 3), ])

        self.assertEqual(list(m3.merge_regions()),
                         [('unchanged', 0, 1),
                          ('conflict', 1, 1, 1, 2, 1, 2),
                          ('unchanged', 1, 2)])

        self.assertEqual(list(m3.merge_groups()),
                         [('unchanged', ['aaa\n']),
                          ('conflict', [], ['111\n'], ['222\n']),
                          ('unchanged', ['bbb\n']),
                          ])

        ml = m3.merge_lines(name_a='a',
                            name_b='b',
                            start_marker='<<',
                            mid_marker='--',
                            end_marker='>>')
        self.assertEqual(''.join(ml), '''\
aaa
<< a
111
--
222
>> b
bbb
''')

    def test_replace_clash(self):
        """Both try to insert lines in the same place."""
        m3 = merge3.Merge3(['aaa', '000', 'bbb'],
                           ['aaa', '111', 'bbb'],
                           ['aaa', '222', 'bbb'])

        self.assertEqual(m3.find_unconflicted(),
                         [(0, 1), (2, 3)])

        self.assertEqual(list(m3.find_sync_regions()),
                         [(0, 1, 0, 1, 0, 1),
                          (2, 3, 2, 3, 2, 3),
                          (3, 3, 3, 3, 3, 3), ])

    def test_replace_multi(self):
        """Replacement with regions of different size."""
        m3 = merge3.Merge3([b'aaa', b'000', b'000', b'bbb'],
                           [b'aaa', b'111', b'111', b'111', b'bbb'],
                           [b'aaa', b'222', b'222', b'222', b'222', b'bbb'])

        self.assertEqual(m3.find_unconflicted(),
                         [(0, 1), (3, 4)])

        self.assertEqual(list(m3.find_sync_regions()),
                         [(0, 1, 0, 1, 0, 1),
                          (3, 4, 4, 5, 5, 6),
                          (4, 4, 5, 5, 6, 6), ])

    def test_merge_poem(self):
        """Test case from diff3 manual"""
        m3 = merge3.Merge3(TZU, LAO, TAO)
        ml = list(m3.merge_lines('LAO', 'TAO'))
        self.assertEqual(ml, MERGED_RESULT)

    def test_merge_poem_bytes(self):
        """Test case from diff3 manual"""
        m3 = merge3.Merge3(
            [line.encode() for line in TZU],
            [line.encode() for line in LAO],
            [line.encode() for line in TAO])
        ml = list(m3.merge_lines('LAO'.encode(), 'TAO'.encode()))
        self.assertEqual(
            ml, [line.encode() for line in MERGED_RESULT])

    def test_minimal_conflicts_common(self):
        """Reprocessing"""
        base_text = ("a\n" * 20).splitlines(True)
        this_text = ("a\n"*10 + "b\n" * 10).splitlines(True)
        other_text = ("a\n"*10 + "c\n" + "b\n" * 8 + "c\n").splitlines(True)
        m3 = merge3.Merge3(base_text, other_text, this_text)
        m_lines = m3.merge_lines('OTHER', 'THIS', reprocess=True)
        merged_text = "".join(list(m_lines))
        optimal_text = (
            "a\n" * 10 + "<<<<<<< OTHER\nc\n"
            "=======\n" + ">>>>>>> THIS\n" + 8 * "b\n" +
            "<<<<<<< OTHER\nc\n" + "=======\n" + 2 * "b\n" +
            ">>>>>>> THIS\n")
        self.assertEqual(optimal_text, merged_text)

    def test_cherrypick(self):
        base_text = "ba\nb\n"
        this_text = "ba\n"
        other_text = "a\nb\nc\n"

        m3 = merge3.Merge3(
            base_text.splitlines(True),
            other_text.splitlines(True),
            this_text.splitlines(True))

        self.assertEqual(m3.find_unconflicted(), [])

        self.assertEqual(list(m3.find_sync_regions()), [(2, 2, 3, 3, 1, 1)])

    def test_minimal_conflicts_common_with_patiencediff(self):
        """Reprocessing"""
        try:
            import patiencediff
        except ImportError:
            self.skipTest('patiencediff not available')
        base_text = ("a\n" * 20).splitlines(True)
        this_text = ("a\n"*10 + "b\n" * 10).splitlines(True)
        other_text = ("a\n"*10 + "c\n" + "b\n" * 8 + "c\n").splitlines(True)
        m3 = merge3.Merge3(
            base_text, other_text, this_text,
            sequence_matcher=patiencediff.PatienceSequenceMatcher)
        m_lines = m3.merge_lines(
                'OTHER', 'THIS', reprocess=True)
        merged_text = "".join(list(m_lines))
        optimal_text = (
            "a\n" * 10 + "<<<<<<< OTHER\nc\n"
            + 8 * "b\n" + "c\n=======\n"
            + 10 * "b\n" + ">>>>>>> THIS\n")
        self.assertEqual(optimal_text, merged_text)

    def test_minimal_conflicts_unique(self):
        def add_newline(s):
            """Add a newline to each entry in the string"""
            return [(x+'\n') for x in s]

        base_text = add_newline("abcdefghijklm")
        this_text = add_newline("abcdefghijklmNOPQRSTUVWXYZ")
        other_text = add_newline("abcdefghijklm1OPQRSTUVWXY2")
        m3 = merge3.Merge3(base_text, other_text, this_text)
        m_lines = m3.merge_lines('OTHER', 'THIS', reprocess=True)
        merged_text = "".join(list(m_lines))
        optimal_text = ''.join(
            add_newline("abcdefghijklm")
            + ["<<<<<<< OTHER\n1\n=======\nN\n>>>>>>> THIS\n"]
            + add_newline('OPQRSTUVWXY')
            + ["<<<<<<< OTHER\n2\n=======\nZ\n>>>>>>> THIS\n"]
            )
        self.assertEqual(optimal_text, merged_text)

    def test_minimal_conflicts_nonunique(self):
        def add_newline(s):
            """Add a newline to each entry in the string"""
            return [(x+'\n') for x in s]

        base_text = add_newline("abacddefgghij")
        this_text = add_newline("abacddefgghijkalmontfprz")
        other_text = add_newline("abacddefgghijknlmontfprd")
        m3 = merge3.Merge3(base_text, other_text, this_text)
        m_lines = m3.merge_lines('OTHER', 'THIS', reprocess=True)
        merged_text = "".join(list(m_lines))
        optimal_text = ''.join(
            add_newline("abacddefgghijk")
            + ["<<<<<<< OTHER\nn\n=======\na\n>>>>>>> THIS\n"]
            + add_newline('lmontfpr')
            + ["<<<<<<< OTHER\nd\n=======\nz\n>>>>>>> THIS\n"]
            )
        self.assertEqual(optimal_text, merged_text)

    def test_reprocess_and_base(self):
        """Reprocessing and showing base breaks correctly"""
        base_text = ("a\n" * 20).splitlines(True)
        this_text = ("a\n"*10+"b\n" * 10).splitlines(True)
        other_text = ("a\n"*10+"c\n"+"b\n" * 8 + "c\n").splitlines(True)
        m3 = merge3.Merge3(base_text, other_text, this_text)
        m_lines = m3.merge_lines('OTHER', 'THIS', reprocess=True,
                                 base_marker='|||||||')
        self.assertRaises(merge3.CantReprocessAndShowBase, list, m_lines)

    def test_dos_text(self):
        base_text = 'a\r\n'
        this_text = 'b\r\n'
        other_text = 'c\r\n'
        m3 = merge3.Merge3(base_text.splitlines(True),
                           other_text.splitlines(True),
                           this_text.splitlines(True))
        m_lines = m3.merge_lines('OTHER', 'THIS')
        self.assertEqual(
            '<<<<<<< OTHER\r\nc\r\n=======\r\nb\r\n'
            '>>>>>>> THIS\r\n'.splitlines(True), list(m_lines))

    def test_mac_text(self):
        base_text = 'a\r'
        this_text = 'b\r'
        other_text = 'c\r'
        m3 = merge3.Merge3(base_text.splitlines(True),
                           other_text.splitlines(True),
                           this_text.splitlines(True))
        m_lines = m3.merge_lines('OTHER', 'THIS')
        self.assertEqual(
            '<<<<<<< OTHER\rc\r=======\rb\r'
            '>>>>>>> THIS\r'.splitlines(True), list(m_lines))

    def test_merge3_cherrypick(self):
        base_text = "a\nb\n"
        this_text = "a\n"
        other_text = "a\nb\nc\n"
        # When cherrypicking, lines in base are not part of the conflict
        m3 = merge3.Merge3(base_text.splitlines(True),
                           this_text.splitlines(True),
                           other_text.splitlines(True), is_cherrypick=True)
        m_lines = m3.merge_lines()
        self.assertEqual('a\n<<<<<<<\n=======\nc\n>>>>>>>\n',
                         ''.join(m_lines))

        # This is not symmetric
        m3 = merge3.Merge3(base_text.splitlines(True),
                           other_text.splitlines(True),
                           this_text.splitlines(True), is_cherrypick=True)
        m_lines = m3.merge_lines()
        self.assertEqual('a\n<<<<<<<\nb\nc\n=======\n>>>>>>>\n',
                         ''.join(m_lines))

    def test_merge3_cherrypick_w_mixed(self):
        base_text = 'a\nb\nc\nd\ne\n'
        this_text = 'a\nb\nq\n'
        other_text = 'a\nb\nc\nd\nf\ne\ng\n'
        # When cherrypicking, lines in base are not part of the conflict
        m3 = merge3.Merge3(base_text.splitlines(True),
                           this_text.splitlines(True),
                           other_text.splitlines(True), is_cherrypick=True)
        m_lines = m3.merge_lines()
        self.assertEqual('a\n'
                         'b\n'
                         '<<<<<<<\n'
                         'q\n'
                         '=======\n'
                         'f\n'
                         '>>>>>>>\n'
                         '<<<<<<<\n'
                         '=======\n'
                         'g\n'
                         '>>>>>>>\n',
                         ''.join(m_lines))

    def test_allow_objects(self):
        """Objects other than strs may be used with Merge3.

        merge_groups and merge_regions work with non-str input.  Methods that
        return lines like merge_lines fail.
        """
        base = [(int2byte(x), int2byte(x)) for x in bytearray(b'abcde')]
        a = [(int2byte(x), int2byte(x)) for x in bytearray(b'abcdef')]
        b = [(int2byte(x), int2byte(x)) for x in bytearray(b'Zabcde')]
        m3 = merge3.Merge3(base, a, b)
        self.assertEqual(
            [('b', 0, 1),
             ('unchanged', 0, 5),
             ('a', 5, 6)],
            list(m3.merge_regions()))
        self.assertEqual(
            [('b', [(b'Z', b'Z')]),
             ('unchanged', [
                 (int2byte(x), int2byte(x)) for x in bytearray(b'abcde')]),
             ('a', [(b'f', b'f')])],
            list(m3.merge_groups()))
