#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PyGoo - An Object-Graph mapper
# Copyright (c) 2010 Nicolas Wack <wackou@gmail.com>
#
# PyGoo is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# PyGoo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import unicode_literals
from pygootest import *

class TestBaseObject(TestCase):

    def setUp(self):
        ontology.clear()

    def testBaseObject(self, GraphClass = MemoryObjectGraph):
        class NiceGuy(BaseObject):
            schema = { 'friend': [BaseObject] }
            valid = [ 'friend' ]
            reverse_lookup = { 'friend': ['friendOf'] }
        g1 = GraphClass()
        o1 = g1.BaseObject(n='o1')
        o2 = g1.BaseObject(n='o2')

        #import pygoo.debugprint

        # make sure we accept generator as properties
        def friends():
            yield o1
            yield o2

        n1 = g1.NiceGuy(name='node1', friend=friends())
        #g1.display_graph('-- g1-40 --')

        n3 = g1.NiceGuy(name = 'other node', friend=[o1, o2])
        n4 = g1.NiceGuy(n='n4', friend=n3.friend)

        self.assertEqual(g1, next(n4.friend).graph())
        self.assertEqual(g1, next(n4.node.friend).graph())
        self.assert_(o1 in n4.friend)
        self.assert_(o2 in n4.friend)
        self.assert_(n3 in o1.friendOf)
        self.assert_(n3 in o2.friendOf)
        self.assert_(n4 in o1.friendOf)
        self.assert_(n4 in o2.friendOf)


    def testBaseObject2(self, GraphClass = MemoryObjectGraph):
        class NiceGuy(BaseObject):
            schema = { 'friend': [BaseObject] }
            valid = [ 'friend' ]
            reverse_lookup = { 'friend': ['friendOf'] }

        # There is a problem when the reverse-lookup has the same name as the property because of the types:
        # NiceGuy.friend = BaseObject, BaseObject.friend = NiceGuy
        #
        # it should also be possible to have A.friend = B and C.friend = B, and not be a problem for B, ie: type(B.friend) in [ A, C ]
        #
        # or we should restrict the ontology only to accept:
        #  - no reverseLookup where key == value
        #  - no 2 classes with the same link types to a third class
        # actually, no reverseLookup where the implicit property could override an already existing one

        g1 = GraphClass()
        g2 = GraphClass()

        n1 = g1.BaseObject(n='n1', a=23)
        n2 = g1.NiceGuy(n='n2', friend=n1)
        self.assertEqual(next(n1.friendOf), n2)
        #g1.display_graph('-- g1 --')
        r2 = g2.add_object(n2)
        r2.n = 'r2'
        self.assertEqual(next(n1.friendOf), n2)

        n3 = g1.NiceGuy(name = 'other node', friend = n1)
        r3 = g2.add_object(n3)

        #g2.display_graph('-- g2 --')

        # TODO: also try adding n2 after n3 is created

        #g1.display_graph('-- g1-2 --')
        o1 = g1.BaseObject(n = 'o1')
        o2 = g1.BaseObject(n = 'o2')
        #g1.display_graph('-- g1-3 --')

        old = next(n3.friend)
        n3.friend = [ o1, o2 ]
        self.assertEqual(next(o1.friendOf), n3)
        self.assertEqual(next(o2.friendOf), n3)
        self.assertEqual(next(old.friendOf), n2)

        #g1.display_graph('-- g1-41 --')

        n4 = g1.NiceGuy(n='n4', friend=n3.friend)
        self.assertEqual(g1, next(n4.friend).graph())
        self.assertEqual(g1, next(n4.node.friend).graph())
        self.assert_(o1 in n4.friend)
        self.assert_(o2 in n4.friend)
        self.assert_(n3 in o1.friendOf)
        self.assert_(n3 in o2.friendOf)
        self.assert_(n4 in o1.friendOf)
        self.assert_(n4 in o2.friendOf)
        #g1.display_graph('-- g1-42 --')

        n3.friend = []
        self.assertEqual(next(o1.friendOf), n4)
        self.assertEqual(next(o2.friendOf), n4)

        #g1.display_graph()
        g1.save('/tmp/pygoo_unittest.db')

        g3 = GraphClass()
        g3.load('/tmp/pygoo_unittest.db')

        self.assertEqual(next(g3.find_one(NiceGuy, n = 'n2').friend).a, 23)
        self.assertEqual(next(g3.find_one(NiceGuy, n = 'n2').friend).node,
                         g3.find_one(BaseObject, n = 'n1').node)

        os.remove('/tmp/pygoo_unittest.db')


    def testAddObject(self):
        ontology.import_ontology('media')

        g = MemoryObjectGraph()

        g1 = MemoryObjectGraph()
        m1 = g1.Video(filename = 'a.avi',
                      episode = g1.Episode(series = g1.Series(title = 'A'),
                                           season = 1,
                                           episodeNumber = 1))
        g.add_object(m1, recurse = Equal.OnUnique)

        g2 = MemoryObjectGraph()
        m2 = g2.File(filename = 'a.srt',
                     subtitle = g2.Subtitle(language = 'en',
                                            video = g2.Episode(series = g2.Series(title = 'A'),
                                                               season = 1,
                                                               episodeNumber = 1)))

        g.add_object(m2, recurse = Equal.OnUnique)

        self.assertEqual(len(g.find_all(Episode)), 1)


suite = allTests(TestBaseObject)

if __name__ == '__main__':
    TextTestRunner(verbosity=2).run(suite)
