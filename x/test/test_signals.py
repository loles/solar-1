import unittest

import base

from x import signals as xs


class TestBaseInput(base.BaseResourceTest):
    def test_input_dict_type(self):
        sample_meta_dir = self.make_resource_meta("""
id: sample
handler: ansible
version: 1.0.0
input:
  values: {}
        """)

        sample1 = self.create_resource(
            'sample1', sample_meta_dir, {'values': {'a': 1, 'b': 2}}
        )
        sample2 = self.create_resource(
            'sample2', sample_meta_dir, {'values': None}
        )
        xs.connect(sample1, sample2)
        self.assertDictEqual(
            sample1.args['values'].value,
            sample2.args['values'].value,
        )

        # Check update
        sample1.update({'values': {'a': 2}})
        self.assertDictEqual(
            sample1.args['values'].value,
            {'a': 2}
        )
        self.assertDictEqual(
            sample1.args['values'].value,
            sample2.args['values'].value,
        )

        # Check disconnect
        xs.disconnect(sample1, sample2)
        sample1.update({'values': {'a': 3}})
        self.assertDictEqual(
            sample1.args['values'].value,
            {'a': 3}
        )
        self.assertDictEqual(
            sample2.args['values'].value,
            {'a': 2}
        )


class TestListInput(base.BaseResourceTest):
    def test_list_input_single(self):
        sample_meta_dir = self.make_resource_meta("""
id: sample
handler: ansible
version: 1.0.0
input:
  ip:
        """)
        list_input_single_meta_dir = self.make_resource_meta("""
id: list-input-single
handler: ansible
version: 1.0.0
input:
  ips:
input-types:
  ips: list
        """)

        sample1 = self.create_resource(
            'sample1', sample_meta_dir, {'ip': '10.0.0.1'}
        )
        sample2 = self.create_resource(
            'sample2', sample_meta_dir, {'ip': '10.0.0.2'}
        )
        list_input_single = self.create_resource(
            'list-input-single', list_input_single_meta_dir, {'ips': {}}
        )

        xs.connect(sample1, list_input_single, mapping={'ip': 'ips'})
        self.assertDictEqual(
            list_input_single.args['ips'].value,
            {
                'sample1': sample1.args['ip'].value,
            }
        )

        xs.connect(sample2, list_input_single, mapping={'ip': 'ips'})
        self.assertDictEqual(
            list_input_single.args['ips'].value,
            {
                'sample1': sample1.args['ip'].value,
                'sample2': sample2.args['ip'].value,
            }
        )

    def test_list_input_multi(self):
        sample_meta_dir = self.make_resource_meta("""
id: sample
handler: ansible
version: 1.0.0
input:
  ip:
  port:
        """)
        list_input_multi_meta_dir = self.make_resource_meta("""
id: list-input-multi
handler: ansible
version: 1.0.0
input:
  ips:
  ports:
input-types:
  ips: list
  ports: list
        """)

        sample1 = self.create_resource(
            'sample1', sample_meta_dir, {'ip': '10.0.0.1', 'port': '1000'}
        )
        sample2 = self.create_resource(
            'sample2', sample_meta_dir, {'ip': '10.0.0.2', 'port': '1001'}
        )
        list_input_multi = self.create_resource(
            'list-input-multi', list_input_multi_meta_dir, {'ips': {}, 'ports': {}}
        )

        xs.connect(sample1, list_input_multi, mapping={'ip': 'ips', 'port': 'ports'})
        self.assertDictEqual(
            list_input_multi.args['ips'].value,
            {
                'sample1': sample1.args['ip'].value,
            }
        )
        self.assertDictEqual(
            list_input_multi.args['ports'].value,
            {
                'sample1': sample1.args['port'].value,
            }
        )

        xs.connect(sample2, list_input_multi, mapping={'ip': 'ips', 'port': 'ports'})
        self.assertDictEqual(
            list_input_multi.args['ips'].value,
            {
                'sample1': sample1.args['ip'].value,
                'sample2': sample2.args['ip'].value,
            }
        )
        self.assertDictEqual(
            list_input_multi.args['ports'].value,
            {
                'sample1': sample1.args['port'].value,
                'sample2': sample2.args['port'].value,
            }
        )


if __name__ == '__main__':
    unittest.main()
