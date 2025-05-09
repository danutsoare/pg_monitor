import asyncpg
import logging
from typing import List, Dict, Any, Optional

from app import schemas # Import your Pydantic schemas

logger = logging.getLogger(__name__)

async def get_column_details(conn: asyncpg.Connection, schema_name: str, object_name: str) -> List[schemas.monitoring.ColumnDetail]:
    """Fetches detailed column information for a table or view."""
    cols = []
    # Query based on information_schema.columns and pg_description for comments
    # Similar to `psql \d+ table_name` column section
    query = """
        SELECT
            c.column_name,
            c.data_type,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            c.is_nullable,
            c.column_default,
            c.collation_name AS collation,
            pgd.description
            -- col_description(pc.oid, c.ordinal_position) as description, -- Alternative for description
            -- pa.attstorage AS storage, -- Requires joining pg_attribute
            -- pa.attcompression AS compression -- Requires joining pg_attribute
        FROM information_schema.columns c
        LEFT JOIN pg_catalog.pg_stat_all_tables psat ON c.table_schema = psat.schemaname AND c.table_name = psat.relname
        LEFT JOIN pg_catalog.pg_description pgd ON pgd.objoid = psat.relid AND pgd.objsubid = c.ordinal_position
        -- LEFT JOIN pg_catalog.pg_class pc ON pc.relname = c.table_name AND pc.relnamespace = (SELECT oid FROM pg_catalog.pg_namespace WHERE nspname = c.table_schema)
        -- LEFT JOIN pg_catalog.pg_attribute pa ON pa.attrelid = pc.oid AND pa.attname = c.column_name
        WHERE c.table_schema = $1 AND c.table_name = $2
        ORDER BY c.ordinal_position;
    """
    try:
        records = await conn.fetch(query, schema_name, object_name)
        for r in records:
            # Map record to schemas.ColumnDetail
            # Need to format data_type properly (e.g., with length/precision/scale)
            # is_nullable is 'YES' or 'NO'
            dt = r['data_type']
            if r['character_maximum_length']:
                dt = f"{dt}({r['character_maximum_length']})"
            elif r['numeric_precision'] is not None:
                dt = f"{dt}({r['numeric_precision']},{r['numeric_scale']})" if r['numeric_scale'] is not None else f"{dt}({r['numeric_precision']})"

            cols.append(schemas.monitoring.ColumnDetail(
                column_name=r['column_name'],
                data_type=dt,
                collation=r['collation'],
                is_nullable=r['is_nullable'] == 'YES',
                column_default=r['column_default'],
                description=r['description'],
                # storage= ... need to map char to text for attstorage
                # compression= ... need to map char to text for attcompression
            ))
    except Exception as e:
        logger.error(f"Error fetching column details for {schema_name}.{object_name}: {e}")
    return cols

async def get_index_details(conn: asyncpg.Connection, schema_name: str, table_name: str) -> List[schemas.monitoring.IndexDetail]:
    """Fetches index information for a table."""
    indexes = []
    # Query based on pg_indexes or pg_class/pg_index for more detail
    # `psql \d+ table_name` indexes section
    query = """
        SELECT
            i.indexname,
            i.indexdef,
            idx.indisprimary AS is_primary_key,
            idx.indisunique AS is_unique,
            am.amname AS index_type
        FROM pg_catalog.pg_indexes i
        JOIN pg_catalog.pg_class c ON c.relname = i.tablename AND c.relnamespace = (SELECT oid FROM pg_catalog.pg_namespace WHERE nspname = i.schemaname)
        JOIN pg_catalog.pg_index idx ON idx.indexrelid = (SELECT oid FROM pg_catalog.pg_class WHERE relname = i.indexname AND relnamespace = (SELECT oid FROM pg_catalog.pg_namespace WHERE nspname = i.schemaname))
        JOIN pg_catalog.pg_class ic ON ic.oid = idx.indexrelid
        JOIN pg_catalog.pg_am am ON am.oid = ic.relam
        WHERE i.schemaname = $1 AND i.tablename = $2;
    """
    try:
        records = await conn.fetch(query, schema_name, table_name)
        for r in records:
            indexes.append(schemas.monitoring.IndexDetail(
                index_name=r['indexname'],
                index_definition=r['indexdef'],
                is_primary_key=r['is_primary_key'],
                is_unique=r['is_unique'],
                index_type=r['index_type'],
            ))
    except Exception as e:
        logger.error(f"Error fetching index details for {schema_name}.{table_name}: {e}")
    return indexes

async def get_constraint_details(conn: asyncpg.Connection, schema_name: str, table_name: str) -> List[schemas.monitoring.ConstraintDetail]:
    """Fetches constraint information for a table."""
    constraints = []
    # Query based on pg_constraint, information_schema.table_constraints etc.
    # `psql \d+ table_name` constraints section
    query = """
        SELECT
            conname AS constraint_name,
            contype AS constraint_type_code,
            pg_get_constraintdef(oid) AS definition
        FROM pg_catalog.pg_constraint
        WHERE conrelid = (
            SELECT c.oid
            FROM pg_catalog.pg_class c
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relname = $2 AND n.nspname = $1
        );
    """
    # Constraint type codes: c = CHECK, f = FOREIGN KEY, p = PRIMARY KEY, u = UNIQUE, t = TRIGGER, x = EXCLUSION
    type_map = {
        'c': 'CHECK',
        'f': 'FOREIGN KEY',
        'p': 'PRIMARY KEY',
        'u': 'UNIQUE',
        'x': 'EXCLUSION'
    }
    try:
        records = await conn.fetch(query, schema_name, table_name)
        for r in records:
            constraint_type = type_map.get(r['constraint_type_code'], r['constraint_type_code'])
            constraints.append(schemas.monitoring.ConstraintDetail(
                constraint_name=r['constraint_name'],
                constraint_type=constraint_type,
                definition=r['definition'],
            ))
    except Exception as e:
        logger.error(f"Error fetching constraint details for {schema_name}.{table_name}: {e}")
    return constraints

async def get_row_count(conn: asyncpg.Connection, schema_name: str, table_name: str) -> Optional[int]:
    """Fetches the row count for a table."""
    try:
        # Ensure schema and table names are properly quoted to prevent SQL injection
        # if passed directly into an f-string. Using parameters is safer.
        # However, COUNT(*) on a fully qualified name constructed with $1.$2 doesn't work directly in asyncpg like that.
        # We need to quote identifiers properly if constructing the query string.
        # For now, this simple version assumes table_name doesn't need complex quoting.
        # A more robust solution would use format() with an SQL identifier quoter.
        quoted_schema_name = asyncpg.utils.quote_ident(schema_name)
        quoted_table_name = asyncpg.utils.quote_ident(table_name)
        count = await conn.fetchval(f'SELECT COUNT(*) FROM {quoted_schema_name}.{quoted_table_name}')
        return int(count) if count is not None else None
    except Exception as e:
        logger.error(f"Error fetching row count for {schema_name}.{table_name}: {e}")
        return None

async def get_view_definition(conn: asyncpg.Connection, schema_name: str, view_name: str) -> Optional[str]:
    """Fetches the definition for a view."""
    try:
        definition = await conn.fetchval(
            "SELECT definition FROM pg_catalog.pg_views WHERE schemaname = $1 AND viewname = $2",
            schema_name, view_name
        )
        return definition
    except Exception as e:
        logger.error(f"Error fetching view definition for {schema_name}.{view_name}: {e}")
        return None

async def get_table_options(conn: asyncpg.Connection, schema_name: str, table_name: str) -> Optional[List[str]]:
    """Fetches table options (like fillfactor) for a table."""
    try:
        options_array = await conn.fetchval("""
            SELECT c.reloptions
            FROM pg_catalog.pg_class c
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = $1 AND c.relname = $2 AND c.relkind IN ('r', 'p', 'm');
            """, schema_name, table_name)
        return options_array if options_array else []
    except Exception as e:
        logger.error(f"Error fetching table options for {schema_name}.{table_name}: {e}")
        return None

async def get_access_method(conn: asyncpg.Connection, schema_name: str, table_name: str) -> Optional[str]:
    """Fetches the access method for a table."""
    try:
        access_method_name = await conn.fetchval("""
            SELECT am.amname
            FROM pg_catalog.pg_class c
            JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            JOIN pg_catalog.pg_am am ON am.oid = c.relam
            WHERE n.nspname = $1 AND c.relname = $2 AND c.relkind IN ('r', 'p', 'm');
            """, schema_name, table_name)
        return access_method_name
    except Exception as e:
        logger.error(f"Error fetching access method for {schema_name}.{table_name}: {e}")
        return None


async def get_object_full_details(
    conn: asyncpg.Connection, 
    schema_name: str, 
    object_name: str, 
    object_type: str,
    owner: Optional[str] = None # Owner can be passed if already known
) -> Optional[schemas.monitoring.ObjectFullDetails]:
    """
    Fetches comprehensive details for a database object (table, view, index etc.).
    The `conn` should be an active asyncpg connection to the *monitored* database.
    """
    logger.info(f"Fetching full details for {object_type} {schema_name}.{object_name}")

    details = schemas.monitoring.ObjectFullDetails(
        schema_name=schema_name,
        object_name=object_name,
        object_type=object_type,
        owner=owner # Assign if passed
    )

    # Common details to fetch if owner is not provided
    if not owner:
        try:
            # This query gets owner for various relkinds
            owner_query = """
                SELECT pg_catalog.pg_get_userbyid(c.relowner) AS owner
                FROM pg_catalog.pg_class c
                JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = $1 AND c.relname = $2;
            """
            # For sequences, pg_class might not have owner directly, or might need different handling
            # For now, this covers tables, views, indexes.
            # If object_type is 'sequence', a different query for owner might be needed if this fails.
            fetched_owner = await conn.fetchval(owner_query, schema_name, object_name)
            details.owner = fetched_owner
        except Exception as e:
            logger.warning(f"Could not fetch owner for {schema_name}.{object_name}: {e}")

    if object_type in ['table', 'view', 'materialized view', 'foreign table', 'partitioned table']:
        details.columns = await get_column_details(conn, schema_name, object_name)

    if object_type in ['table', 'materialized view', 'partitioned table']:
        details.row_count = await get_row_count(conn, schema_name, object_name)

    if object_type in ['table', 'partitioned table']:
        details.indexes = await get_index_details(conn, schema_name, object_name)
        details.constraints = await get_constraint_details(conn, schema_name, object_name)
        details.access_method = await get_access_method(conn, schema_name, object_name)
        details.options = await get_table_options(conn, schema_name, object_name)
    
    if object_type == 'view':
        details.view_definition = await get_view_definition(conn, schema_name, object_name)
    
    # if object_type == 'index':
    #     # Fetch specific index details if not already covered by general object info
    #     # This might involve a query similar to get_index_details but focused on ONE index
    #     pass

    # if object_type == 'sequence':
    #     # Fetch sequence parameters (start_value, increment_by, max_value, min_value, cache_value, is_cycled)
    #     pass

    # TODO: Add description fetching for the object itself (not just columns)
    # e.g., obj_description(relid, 'pg_class')

    return details 