import os, tempfile, unittest, importlib.util, pathlib
module_file=pathlib.Path(__file__).resolve().parents[1]/"backend"/"native_host.py"
with tempfile.TemporaryDirectory() as tmp:
    os.environ["AZZLAER_JOBHUNTER_HOME"]=tmp
    spec=importlib.util.spec_from_file_location("native_host",module_file)
    host=importlib.util.module_from_spec(spec);spec.loader.exec_module(host)
    class NativeHostTests(unittest.TestCase):
        def test_search_order(self):
            for n in range(3):
                host.handle({"action":"record_search","url":"https://www.linkedin.com/jobs/search/?keywords=Help+Desk","term":"Help Desk","location":"Chile"})
            s=host.handle({"action":"stats"})
            self.assertEqual(s["search_runs"],3)
            self.assertEqual(s["unique_searches"],1)
        def test_offer_and_stats(self):
            host.handle({"action":"upsert_offer","offer":{"id":"test123","url":"https://www.linkedin.com/jobs/view/12345678/","title":"Help Desk L1","company":"Empresa","status":"guardada"},"score":75})
            s=host.handle({"action":"stats"})
            self.assertEqual(s["offers"],1)
            self.assertEqual(s["matches"],1)
            self.assertEqual(s["recent_offers"][0]["result_position"],1)
        def test_url_validation(self):
            with self.assertRaises(ValueError):host.handle({"action":"record_search","url":"https://example.com/jobs/search/"})
if __name__ == '__main__':
    unittest.main()
