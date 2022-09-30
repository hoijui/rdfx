import uuid
from pathlib import Path

from rdflib import Graph

from rdfx.persistence_systems import SOP

sample_graph = Graph().parse(
    data="""
    <a:> <b:> <c:> .
    <a:> <d:> <e:> .
    """,
    format="turtle",
)
existing_datagraph = "http://topbraid.org/examples/kennedys"

local_sop_ps = SOP()


def test_asset_exists_local_positive():
    # the kennedy's graph should be in any SOP system by default
    assert local_sop_ps.asset_exists(existing_datagraph)


def test_sop_query_local():
    query = "SELECT * { ?s ?p ?o } LIMIT 10"
    results = local_sop_ps.query(query, existing_datagraph)
    # simply validating we are getting results back at this point
    assert len(results) == 10


def test_create_datagraph_local():
    datagraph_to_create = f"datagraph-{uuid.uuid4()}".replace("-", "_")
    assert not local_sop_ps.asset_exists(datagraph_to_create)
    new_datagraph_local = local_sop_ps.create_datagraph(datagraph_to_create)
    assert local_sop_ps.asset_exists(new_datagraph_local)
    assert datagraph_to_create == new_datagraph_local.split(":")[2]
    # NB if you pass an invalid graph name to SOP for creation, it will try to make it valid, so the graph name
    # returned by SOP will not necessarily match the one asked for.


def test_create_workflow_local():
    workflow_to_create = f"workflow-{uuid.uuid4()}".replace("-", "_")
    assert not local_sop_ps.asset_exists(workflow_to_create)
    new_datagraph = local_sop_ps.create_datagraph()
    workflow_urn = local_sop_ps.create_workflow(
        graph_iri=new_datagraph, workflow_name=workflow_to_create
    )
    assert local_sop_ps.asset_exists(workflow_urn)


def test_create_manifest_local():
    manifest_to_create = f"manifest-{uuid.uuid4()}".replace("-", "_")
    assert not local_sop_ps.asset_exists(manifest_to_create)
    manifest_urn = local_sop_ps.create_manifest(manifest_name=manifest_to_create)
    assert local_sop_ps.asset_exists(manifest_urn)


def test_sop_duplicate_datagraph_creation():
    new_graph_name = f"datagraph-{uuid.uuid4()}".replace("-", "_")
    response_1 = local_sop_ps.create_datagraph(datagraph_name=new_graph_name)
    response_2 = local_sop_ps.create_datagraph(datagraph_name=new_graph_name)
    assert response_1 != response_2


def test_local_workflow_insert():
    new_datagraph_local = local_sop_ps.create_datagraph()
    workflow_graph_urn = local_sop_ps.create_workflow(new_datagraph_local)
    # try to insert something in to the graph
    insert_response = local_sop_ps.write(sample_graph, workflow_graph_urn)
    assert (
        insert_response == "File with 2 statements has been imported successfully. \n"
    )


def test_asset_size_local():
    new_datagraph_local = local_sop_ps.create_datagraph()
    assert local_sop_ps.asset_collection_size(new_datagraph_local) == 7


def test_read_workflow():
    new_datagraph_local = local_sop_ps.create_datagraph()
    workflow_graph_urn = local_sop_ps.create_workflow(new_datagraph_local)
    local_sop_ps.write(sample_graph, workflow_graph_urn)
    comments, g = local_sop_ps.read(workflow_graph_urn)
    assert len(g) == 6


def test_read_asset():
    new_datagraph_local = local_sop_ps.create_datagraph()
    local_sop_ps.write(sample_graph, new_datagraph_local)
    comments, g = local_sop_ps.read(new_datagraph_local)
    assert len(g) == 6


def test_create_file():
    file_uri = local_sop_ps.create_file(Path("data/file_01.ttl"))
    assert local_sop_ps.asset_exists(file_uri)
    # TODO remove file
