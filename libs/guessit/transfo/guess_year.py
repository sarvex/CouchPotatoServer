#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# GuessIt - A library for guessing information from filenames
# Copyright (c) 2012 Nicolas Wack <wackou@gmail.com>
#
# GuessIt is free software; you can redistribute it and/or modify it under
# the terms of the Lesser GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# GuessIt is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# Lesser GNU General Public License for more details.
#
# You should have received a copy of the Lesser GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


import logging

from guessit.date import search_year
from guessit.transfo import SingleNodeGuesser

log = logging.getLogger(__name__)


def guess_year(string):
    year, span = search_year(string)
    if year:
        return { 'year': year }, span
    else:
        return None, None

def guess_year_skip_first(string):
    year, span = search_year(string)
    if year:
        year2, span2 = guess_year(string[span[1]:])
        if year2:
            return year2, (span2[0]+span[1], span2[1]+span[1])

    return None, None


def process(mtree, skip_first_year=False):
    if skip_first_year:
        SingleNodeGuesser(guess_year_skip_first, 1.0, log).process(mtree)
    else:
        SingleNodeGuesser(guess_year, 1.0, log).process(mtree)
