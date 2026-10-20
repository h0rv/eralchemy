from eralchemy.main import intermediary_to_d2
from eralchemy.models import Column, Relation, Table, quote_d2
from tests.common import relationships, tables


def test_quote_d2():
    assert quote_d2("label") == '"label"'
    assert quote_d2("public.users") == '"public.users"'
    assert quote_d2('a"b\\c') == '"a\\"b\\\\c"'


def test_d2_column_marks_pk_and_fk():
    column = Column(name="association_id", type="UUID", is_key=True, is_foreign_key=True)
    assert column.to_d2() == '  "association_id": "UUID" {constraint: [primary_key; foreign_key]}'


def test_d2_column_without_constraint():
    column = Column(name="name", type="VARCHAR(255)")
    assert column.to_d2() == '  "name": "VARCHAR(255)"'


def test_d2_table():
    table = Table(name="parent", columns=[Column(name="id", type="INTEGER", is_key=True)])
    assert table.to_d2() == (
        '"parent": {\n  shape: sql_table\n  "id": "INTEGER" {constraint: [primary_key]}\n}'
    )


def test_d2_relation_uses_crowfoot_arrowheads():
    relation = Relation(
        left_table="s.child",
        left_column="parent_id",
        right_table="s.parent",
        right_column="id",
        left_cardinality="*",
        right_cardinality="1",
    )
    assert relation.to_d2() == (
        '"s.child"."parent_id" <-> "s.parent"."id": {\n'
        "  source-arrowhead.shape: cf-many\n"
        "  target-arrowhead.shape: cf-one-required\n"
        "}"
    )


def test_d2_relation_without_cardinality():
    relation = Relation(
        left_table="child",
        right_table="parent",
        left_cardinality="",
        right_cardinality="",
    )
    assert relation.to_d2() == '"child" -- "parent"'


def test_intermediary_to_d2():
    d2 = intermediary_to_d2(tables, relationships, title="Forum").decode()
    assert d2.startswith('diagram_title: "Forum" {\n  shape: text\n  near: top-center\n}\n')
    for table in tables:
        assert table.to_d2() in d2
    for relation in relationships:
        assert relation.to_d2() in d2
