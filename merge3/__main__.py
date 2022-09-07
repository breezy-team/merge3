# Copyright (C) 2021 Jelmer Vernooij
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

from . import Merge3


def main(argv):
    import argparse

    parser = argparse.ArgumentParser()
    # as for diff3 and meld the syntax is "MINE BASE OTHER"
    parser.add_argument(
        'mine', type=argparse.FileType('rt'),
        help='My text')
    parser.add_argument(
        'base', type=argparse.FileType('rt'),
        help='Base text')
    parser.add_argument(
        'other', type=argparse.FileType('rt'),
        help='Other text')
    parser.add_argument(
        '--annotated', action='store_true',
        help='Show annotated view.')

    args = parser.parse_args()

    m3 = Merge3(
        args.base.readlines(),
        args.mine.readlines(),
        args.other.readlines())

    if args.annotated:
        sys.stdout.writelines(m3.merge_annotated())
    else:
        sys.stdout.writelines(
            m3.merge_lines(
                name_a=args.mine.name, name_b=args.other.name,
                name_base=args.base.name))


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
