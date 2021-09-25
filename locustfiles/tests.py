import os
from unittest import TestCase, main
from unittest.mock import patch
from xml.etree import ElementTree as ET

from locust.exception import LocustError

from form_submission import (
    dump_xform_tree,
    set_instance_id,
    set_new_case_ids,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UUID = 'aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee'


class TestDumpXFormTree(TestCase):

    def test_dump_xform_tree(self):
        """
        Verifies the return value of dump_xform_tree().

        Not identical, but correct.
        """
        filename = os.sep.join((BASE_DIR, 'xforms', 'simple_xform.xml'))
        xform_tree = ET.parse(filename)

        dumped = dump_xform_tree(xform_tree, 'utf-8')
        self.assertEqual(dumped, expected_xform.encode('utf-8'))


expected_xform = """<?xml version='1.0' encoding='utf-8'?>
<ns0:data xmlns:ns0="https://www.commcarehq.org/test/LocustPerfTesting/" xmlns:ns1="http://openrosa.org/jr/xforms">
    <ns0:foo />
    <ns0:bar />
    <ns1:meta>
        <ns1:deviceID>LocustPerfTesting</ns1:deviceID>
        <ns1:timeStart>2011-10-01T15:25:18.404-04</ns1:timeStart>
        <ns1:timeEnd>2011-10-01T15:26:29.551-04</ns1:timeEnd>
        <ns1:username>admin</ns1:username>
        <ns1:userID>testy.mctestface</ns1:userID>
        <ns1:instanceID>dd2f7684-548a-4165-91de-0533bdcec32c</ns1:instanceID>
    </ns1:meta>
</ns0:data>"""


class TestSetInstanceId(TestCase):

    def test_with_meta_namespace(self):
        filename = os.sep.join((BASE_DIR, 'xforms', 'simple_xform.xml'))
        xform_tree = ET.parse(filename)
        with patch('form_submission.uuid4') as uuid4:
            uuid4.return_value = UUID

            set_instance_id(xform_tree)
        xform = dump_xform_tree(xform_tree, 'unicode')
        self.assertIn(UUID, xform)

    def test_without_meta_namespace(self):
        xform_root = ET.fromstring(bad_xform)
        with patch('form_submission.uuid4') as uuid4:
            uuid4.return_value = UUID

            with self.assertRaises(LocustError):
                set_instance_id(xform_root)


bad_xform = """<?xml version='1.0' encoding='utf-8'?>
<data xmlns="https://www.commcarehq.org/test/LocustPerfTesting/">
    <foo />
    <bar />
    <meta>
        <deviceID>LocustPerfTesting</deviceID>
        <timeStart>2011-10-01T15:25:18.404-04</timeStart>
        <timeEnd>2011-10-01T15:26:29.551-04</timeEnd>
        <username>admin</username>
        <userID>testy.mctestface</userID>
        <instanceID>dd2f7684-548a-4165-91de-0533bdcec32c</instanceID>
    </meta>
</data>"""


class TestSetNewCaseIds(TestCase):

    def test_with_create(self):
        filename = os.sep.join((BASE_DIR, 'xforms', 'creates_case.xml'))
        xform_tree = ET.parse(filename)
        with patch('form_submission.uuid4') as uuid4:
            uuid4.return_value = UUID

            set_new_case_ids(xform_tree)
        xform = dump_xform_tree(xform_tree, 'unicode')
        self.assertIn(UUID, xform)

    def test_without_create(self):
        filename = os.sep.join((BASE_DIR, 'xforms', 'updates_case.xml'))
        xform_tree = ET.parse(filename)
        with patch('form_submission.uuid4') as uuid4:
            uuid4.return_value = UUID

            set_new_case_ids(xform_tree)
        xform = dump_xform_tree(xform_tree, 'unicode')
        self.assertNotIn(UUID, xform)


if __name__ == '__main__':
    main()
