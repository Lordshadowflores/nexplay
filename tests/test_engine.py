import unittest
import numpy as np
from engine import Recommender

class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.e=Recommender()

    def test_alignment_and_dimensions(self):
        self.assertEqual(self.e.embeddings.shape,(22747,32))
        self.assertEqual(len(self.e.columns),234)
        self.assertTrue(self.e.catalog.appid.is_unique)
        self.assertEqual(self.e.encode(self.e.neutral).shape,(1,32))

    def test_free_means_known_zero_price(self):
        rows,n=self.e.recommend({'genres':['Action'],'budget':0,'unknown_price':True},k=18)
        self.assertGreater(n,18)
        self.assertTrue(all(r['price_known']==1 and r['price_usd']==0 for r in rows))

    def test_exclusion_requirements_and_budget(self):
        a={'genres':['RPG'],'budget':30,'age':17,'exclude':['Gore','Violent'],
           'required':[['Single-player']], 'strict_genres':True,'only_real':True}
        rows,n=self.e.recommend(a,k=18)
        self.assertGreater(n,0)
        for r in rows:
            self.assertLessEqual(r['price_usd'],30)
            self.assertLessEqual(r['required_age'],17)
            self.assertTrue(r['appid_real'])
            self.assertIn('RPG',r['genres_list'])
            self.assertIn('Single-player',self.e.tags[r['index']])
            self.assertFalse({'Gore','Violent'}.intersection(self.e.tags[r['index']]))

    def test_sorted_deterministic(self):
        a={'genres':['RPG'],'tags':['Fantasy'],'budget':30}
        first,_=self.e.recommend(a,k=9)
        second,_=self.e.recommend(a,k=9)
        self.assertEqual([r['index'] for r in first],[r['index'] for r in second])
        sims=[r['similarity'] for r in first]
        self.assertEqual(sims,sorted(sims,reverse=True))
        self.assertTrue(all(-1.00001<=s<=1.00001 for s in sims))

    def test_reference_neighbors_from_delivered_embeddings(self):
        i=int(self.e.catalog.index[self.e.catalog.appid==730][0])
        rows,_=self.e.recommend({'unknown_price':True,'unreleased':True},reference=i,k=5)
        self.assertNotIn(i,[r['index'] for r in rows])
        self.assertEqual(rows[0]['name'],'World of Tanks Blitz')
        self.assertAlmostEqual(rows[0]['similarity'],.9344494,places=5)

    def test_impossible_filters_produce_empty_result(self):
        rows,n=self.e.recommend({'required':[['__nonexistent_tag__']]})
        self.assertEqual(rows,[])
        self.assertEqual(n,0)

if __name__=='__main__': unittest.main()
