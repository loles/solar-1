#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import networkx as nx
from pytest import fixture

from solar.orchestration import graph
from solar.orchestration.traversal import states


def test_simple_plan_plan_created_and_loaded(simple_plan):
    plan = graph.get_plan(simple_plan.graph['uid'])
    assert set(plan.nodes()) == {'just_fail', 'echo_stuff'}


def test_reset_all_states(simple_plan):
    for n in simple_plan:
        simple_plan.node[n]['status'] == states.ERROR.name
    graph.reset(simple_plan)

    for n in simple_plan:
        assert simple_plan.node[n]['status'] == states.PENDING.name


def test_reset_only_provided(simple_plan):
    simple_plan.node['just_fail']['status'] = states.ERROR.name
    simple_plan.node['echo_stuff']['status'] = states.SUCCESS.name

    graph.reset(simple_plan, [states.ERROR.name])

    assert simple_plan.node['just_fail']['status'] == states.PENDING.name
    assert simple_plan.node['echo_stuff']['status'] == states.SUCCESS.name


def test_wait_finish(simple_plan):
    for n in simple_plan:
        simple_plan.node[n]['status'] = states.SUCCESS.name
    graph.update_graph(simple_plan)
    assert next(graph.wait_finish(simple_plan.graph['uid'], 10)) == {
        'SKIPPED': 0,
        'SUCCESS': 2,
        'NOOP': 0,
        'ERROR': 0,
        'INPROGRESS': 0,
        'PENDING': 0,
        'ERROR_RETRY': 0,
    }


def test_several_updates(simple_plan):
    simple_plan.node['just_fail']['status'] = states.ERROR.name
    graph.update_graph(simple_plan)

    assert next(graph.wait_finish(simple_plan.graph['uid'], 10)) == {
        'SKIPPED': 0,
        'SUCCESS': 0,
        'NOOP': 0,
        'ERROR': 1,
        'INPROGRESS': 0,
        'PENDING': 1,
        'ERROR_RETRY': 0,
    }

    simple_plan.node['echo_stuff']['status'] = states.ERROR.name
    graph.update_graph(simple_plan)

    assert next(graph.wait_finish(simple_plan.graph['uid'], 10)) == {
        'SKIPPED': 0,
        'SUCCESS': 0,
        'NOOP': 0,
        'ERROR': 2,
        'INPROGRESS': 0,
        'PENDING': 0,
        'ERROR_RETRY': 0,
    }


@fixture
def times():
    rst = nx.DiGraph()
    rst.add_node('t1', start_time=1.0, end_time=12.0,
                 status='', errmsg='')
    rst.add_node('t2', start_time=1.0, end_time=3.0,
                 status='', errmsg='')
    rst.add_node('t3', start_time=3.0, end_time=7.0,
                 status='', errmsg='')
    rst.add_node('t4', start_time=7.0, end_time=13.0,
                 status='', errmsg='')
    rst.add_node('t5', start_time=12.0, end_time=14.0,
                 status='', errmsg='')
    rst.add_path(['t1', 't5'])
    rst.add_path(['t2', 't3', 't4'])
    return rst


def test_report_progress(times):
    report = graph.report_progress_graph(times)
    assert report['total_time'] == 13.0
    assert report['total_delta'] == 25.0
    assert len(report['tasks']) == 5
