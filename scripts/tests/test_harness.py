import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import artifact_path
from fast_qa import find_docx
from analyse_survey import analyse, load_constructs, resolve_results
from run_project import configured_scripts, run_pipeline, run_script
from utils.evidence import check_evidence, sha256


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for folder in ['inputs', 'outputs', 'qa', 'feedback', 'knowledge-base']:
            (self.root / folder).mkdir()
        (self.root / 'project.yaml').write_text('{}')

    def test_no_latest_docx_selection(self):
        (self.root / 'outputs/survey-questionnaire.docx').touch()
        self.assertEqual(find_docx(self.root, None), self.root / 'outputs/dissertation.docx')

    def test_cross_project_path_rejected(self):
        with self.assertRaises(ValueError):
            artifact_path(self.root, '../other-project/data.csv')

    def test_no_dataset_guessing(self):
        (self.root / 'inputs/random.csv').touch()
        with self.assertRaises(ValueError):
            resolve_results(self.root, None, {})

    def test_no_construct_inference(self):
        self.assertEqual(load_constructs(self.root, 17), [])
        self.assertEqual(load_constructs(self.root, 20), [])

    def test_missing_builder_rejected(self):
        with self.assertRaises(ValueError):
            configured_scripts(self.root, {'generation': {'builder': 'missing.py'}})

    def test_builder_timeout(self):
        script = self.root / 'slow.py'
        script.write_text('import time\ntime.sleep(10)')
        self.assertEqual(run_script(script, self.root, timeout=0.01)['returncode'], 124)

    def test_valid_denominator_and_invalid_column_visible(self):
        (self.root / 'inputs/results.csv').write_text('q1,q2\n5,wrong\n,3\n4,4\n')
        result = analyse(self.root, results='inputs/results.csv', metadata_cols=0)
        self.assertEqual(result['item_summary'][0]['agree_pct'], 100)
        self.assertEqual(result['item_summary'][0]['valid_n'], 2)
        self.assertEqual(result['invalid_likert_cells'], 1)
        self.assertEqual(result['rejected_columns'], ['q2'])

    def test_reverse_coding_and_complete_cases(self):
        (self.root / 'inputs/results.csv').write_text('q1,q2\n5,1\n4,2\n3,\n')
        (self.root / 'knowledge-base/survey-codebook.json').write_text(json.dumps({'constructs': [{'code': 'A', 'items': [1, 2], 'reverse_items': [2]}]}))
        result = analyse(self.root, results='inputs/results.csv', metadata_cols=0)
        self.assertEqual(result['construct_summary'][0]['valid_n'], 2)
        self.assertEqual(result['construct_summary'][0]['mean'], 4.5)

    def test_invalid_codebook_not_silently_truncated(self):
        (self.root / 'knowledge-base/survey-codebook.json').write_text(json.dumps({'constructs': [{'code': 'A', 'items': [1, 99]}]}))
        with self.assertRaises(ValueError):
            load_constructs(self.root, 2)

    def ledger(self):
        source = self.root / 'inputs/source.txt'
        source.write_text('Observed sample comprised 20 participants.')
        output = self.root / 'outputs/dissertation.docx'
        output.write_bytes(b'output-v1')
        ledger = {'sources': [{'id': 'S1', 'path': 'inputs/source.txt', 'sha256': sha256(source)}],
                  'claims': [{'id': 'C1', 'text': '20 participants', 'section': 'Findings', 'source_id': 'S1', 'passage': source.read_text(), 'locator': 'section 1', 'support_review': 'verified'}],
                  'output_review': {'sha256': sha256(output), 'claims_complete': True, 'reviewer': 'reviewer'}}
        path = self.root / 'knowledge-base/evidence-ledger.json'
        path.write_text(json.dumps(ledger))
        return ledger, path, source, output

    def test_source_and_output_changes_invalidate_review(self):
        _, _, source, output = self.ledger()
        self.assertEqual(check_evidence(self.root, output)['status'], 'pass')
        source.write_text('Changed source')
        self.assertEqual(check_evidence(self.root, output)['status'], 'fail')
        _, _, _, output = self.ledger()
        output.write_bytes(b'output-v2')
        self.assertEqual(check_evidence(self.root, output)['status'], 'fail')

    def test_fabricated_passage_rejected(self):
        ledger, path, _, output = self.ledger()
        ledger['claims'][0]['passage'] = 'Invented quotation'
        path.write_text(json.dumps(ledger))
        self.assertEqual(check_evidence(self.root, output)['status'], 'fail')

    def test_failed_artifact_gate_blocks_builders(self):
        with patch('run_project.run_preflight', return_value={'status': 'pass', 'summary': {'fail': 0}, 'checks': []}), patch('run_project.scan', return_value={}), patch('run_project.discovery_markdown', return_value='discovery'), patch('run_project.run_artifact_gate', return_value={'status': 'fail', 'summary': {'artifacts': 0}}), patch('run_project.artifact_gate_markdown', return_value='failed'), patch('run_project.configured_scripts') as builders:
            log = run_pipeline(self.root, 'final', 'fast', True)
        builders.assert_not_called()
        self.assertEqual(log['status'], 'fail')

    def test_final_cannot_disable_qa(self):
        self.assertEqual(run_pipeline(self.root, 'final', 'none', True)['status'], 'fail')

    def test_manifest_requires_render(self):
        (self.root / 'project.yaml').write_text('qa:\n  render_required_for_final: true\n')
        with patch('run_project.run_preflight', return_value={'status': 'fail', 'summary': {'fail': 1}, 'checks': []}):
            log = run_pipeline(self.root, 'final', 'fast', False)
        self.assertEqual(log['qa_mode'], 'render')

    def test_final_pipeline_invokes_required_render_and_binds_output(self):
        self.ledger()
        (self.root / 'project.yaml').write_text('qa:\n  render_required_for_final: true\n')
        with patch('run_project.run_preflight', return_value={'status': 'pass', 'summary': {'fail': 0}, 'checks': []}), patch('run_project.scan', return_value={}), patch('run_project.discovery_markdown', return_value='discovery'), patch('run_project.run_artifact_gate', return_value={'status': 'pass', 'summary': {'artifacts': 1}}), patch('run_project.artifact_gate_markdown', return_value='passed'), patch('run_project.run_fast_qa', return_value={'summary': {'fail': 0}}), patch('run_project.fast_qa_markdown', return_value='passed'), patch('run_project.run_benchmark_qa', return_value={'status': 'pass', 'summary': {'fail': 0}}), patch('run_project.benchmark_qa_markdown', return_value='passed'), patch('run_project.render_qa', return_value={'status': 'pass', 'page_images': {'png_pages': 1}}) as renderer, patch('run_project.render_qa_markdown', return_value='passed'):
            log = run_pipeline(self.root, 'final', 'fast', False)
        renderer.assert_called_once_with(self.root)
        self.assertEqual(log['status'], 'pass')
        self.assertEqual(log['output_sha256'], sha256(self.root / 'outputs/dissertation.docx'))

    def test_missing_evidence_blocks_final_builder(self):
        with patch('run_project.run_preflight', return_value={'status': 'pass', 'summary': {'fail': 0}, 'checks': []}), patch('run_project.scan', return_value={}), patch('run_project.discovery_markdown', return_value='discovery'), patch('run_project.run_artifact_gate', return_value={'status': 'pass', 'summary': {'artifacts': 1}}), patch('run_project.artifact_gate_markdown', return_value='passed'), patch('run_project.configured_scripts') as builders:
            log = run_pipeline(self.root, 'final', 'fast', True)
        builders.assert_not_called()
        self.assertEqual(log['status'], 'fail')


if __name__ == '__main__':
    unittest.main()
