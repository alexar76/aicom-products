from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # users
    op.create_table('users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum('admin','editor','viewer', name='user_role'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # advisories
    op.create_table('advisories',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rounded_lat', sa.Float(), nullable=False),
        sa.Column('rounded_lon', sa.Float(), nullable=False),
        sa.Column('hazard', sa.Enum('WEATHER','WILDFIRE','FLOOD', name='hazard_type'), nullable=False),
        sa.Column('level', sa.Enum('CALM','WATCH','WARNING','EMERGENCY','UNKNOWN', name='hazard_level'), nullable=False),
        sa.Column('measurement', sa.String(), nullable=True),
        sa.Column('distance_km', sa.Float(), nullable=True),
        sa.Column('receipt_digest', sa.String(255), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_cached', sa.Boolean(), nullable=False),
        sa.Column('sim_flag', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # cached_mesh_readings
    op.create_table('cached_mesh_readings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('rounded_lat', sa.Float(), nullable=False),
        sa.Column('rounded_lon', sa.Float(), nullable=False),
        sa.Column('capability_name', sa.String(255), nullable=False),
        sa.Column('response_json', sa.Text(), nullable=False),
        sa.Column('receipt_digest', sa.String(255), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # watch_locations
    op.create_table('watch_locations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('label', sa.String(255), nullable=False),
        sa.Column('lat', sa.Float(), nullable=False),
        sa.Column('lon', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # allowance_state
    op.create_table('allowance_state',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('used_invocations', sa.Integer(), nullable=False),
        sa.Column('max_invocations', sa.Integer(), nullable=False),
        sa.Column('window_seconds', sa.Integer(), nullable=False),
        sa.Column('renews_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    # invoke_audit_log
    op.create_table('invoke_audit_log',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('advisory_id', sa.String(36), sa.ForeignKey('advisories.id'), nullable=True),
        sa.Column('capability_name', sa.String(255), nullable=False),
        sa.Column('request_payload', sa.Text(), nullable=True),
        sa.Column('response_receipt_digest', sa.String(255), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=False),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('success','error','402','refusal', name='invoke_status'), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('cost_bucket', sa.String(255), nullable=True)
    )
    # heartbeat_log
    op.create_table('heartbeat_log',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('success', sa.Integer(), nullable=False),
        sa.Column('response_code', sa.Integer(), nullable=True),
        sa.Column('payload', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # dashboards
    op.create_table('dashboards',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('state', sa.Enum('draft','published','archived', name='dashboard_state'), nullable=False),
        sa.Column('owner_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('share_token', sa.String(255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False)
    )
    # metrics
    op.create_table('metrics',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('query_definition', sa.JSON(), nullable=True),
        sa.Column('data_source', sa.Enum('advisory','audit','allowance', name='data_source'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # charts
    op.create_table('charts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('dashboard_id', sa.String(36), sa.ForeignKey('dashboards.id'), nullable=False),
        sa.Column('metric_id', sa.String(36), sa.ForeignKey('metrics.id'), nullable=False),
        sa.Column('chart_type', sa.Enum('line','bar','area','table', name='chart_type'), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('position', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # filters
    op.create_table('filters',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('dashboard_id', sa.String(36), sa.ForeignKey('dashboards.id'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('config', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # datasets
    op.create_table('datasets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('source', sa.Enum('advisory','audit','allowance', name='dataset_source'), nullable=False),
        sa.Column('schema', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # share_links
    op.create_table('share_links',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('dashboard_id', sa.String(36), sa.ForeignKey('dashboards.id'), nullable=False),
        sa.Column('token', sa.String(255), nullable=False, unique=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )
    # data_exports
    op.create_table('data_exports',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('dashboard_id', sa.String(36), sa.ForeignKey('dashboards.id'), nullable=False),
        sa.Column('format', sa.Enum('csv','xlsx', name='export_format'), nullable=False),
        sa.Column('file_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False)
    )

def downgrade():
    op.drop_table('data_exports')
    op.drop_table('share_links')
    op.drop_table('datasets')
    op.drop_table('filters')
    op.drop_table('charts')
    op.drop_table('metrics')
    op.drop_table('dashboards')
    op.drop_table('heartbeat_log')
    op.drop_table('invoke_audit_log')
    op.drop_table('allowance_state')
    op.drop_table('watch_locations')
    op.drop_table('cached_mesh_readings')
    op.drop_table('advisories')
    op.drop_table('users')
