"""
create a top-level materialized view for forum events
"""
from alembic import op


revision = "0019"
down_revision = "0018"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS {{ ASPECTS_XAPI_DATABASE }}.{{ ASPECTS_FORUM_EVENTS_TABLE }} (
            `event_id` UUID NOT NULL,
            `emission_time` DateTime64 NOT NULL,
            `org` String NOT NULL,
            `course_key` String NOT NULL,
            `object_id` String NOT NULL,
            `actor_id` String NOT NULL,
            `verb_id` LowCardinality(String) NOT NULL
        ) ENGINE = ReplacingMergeTree
        PRIMARY KEY (org, course_key, verb_id)
        ORDER BY (org, course_key, verb_id, emission_time, actor_id, object_id, event_id);
        """
    )

    op.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS {{ ASPECTS_XAPI_DATABASE }}.{{ ASPECTS_FORUM_TRANSFORM_MV }}
        TO {{ ASPECTS_XAPI_DATABASE }}.{{ ASPECTS_FORUM_EVENTS_TABLE }} AS
        SELECT
            event_id,
            cast(emission_time as DateTime) as emission_time,
            org,
            splitByString('/', course_id)[-1] AS course_key,
            object_id,
            actor_id,
            verb_id
        FROM
            {{ ASPECTS_XAPI_DATABASE }}.{{ ASPECTS_XAPI_TABLE }}
        WHERE
            JSON_VALUE(event_str, '$.object.definition.type') = 'http://id.tincanapi.com/activitytype/discussion'
        """
    )


def downgrade():
    op.execute(
        "DROP TABLE IF EXISTS {{ ASPECTS_XAPI_DATABASE }}.{{ ASPECTS_FORUM_EVENTS_TABLE }}"
    )
    op.execute(
        "DROP VIEW IF EXISTS {{ ASPECTS_XAPI_DATABASE }}.{{ ASPECTS_FORUM_TRANSFORM_MV }}"
    )