from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('subject', sa.String(), unique=True),
        sa.Column('email', sa.String()),
        sa.Column('role', sa.String()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('iban', sa.String()),
        sa.Column('bic', sa.String()),
        sa.Column('display_name', sa.String()),
        sa.Column('sensitive_metadata', sa.LargeBinary()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'transfers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('debtor_account_id', sa.Integer(), sa.ForeignKey('accounts.id'), nullable=False),
        sa.Column('creditor_iban', sa.String()),
        sa.Column('creditor_bic', sa.String()),
        sa.Column('amount', sa.Numeric(18,2), nullable=False),
        sa.Column('currency', sa.String(3), nullable=False),
        sa.Column('status', sa.Enum('INITIATED','PENDING','COMPLETED','FAILED', name='transferstatus'), index=True),
        sa.Column('reference', sa.String()),
        sa.Column('pacs008_xml', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'transfer_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('transfer_id', sa.Integer(), sa.ForeignKey('transfers.id'), nullable=False),
        sa.Column('type', sa.String(), nullable=False),
        sa.Column('payload', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'kyc_documents',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('document_type', sa.String(), nullable=False),
        sa.Column('encrypted_blob', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('correlation_id', sa.String()),
        sa.Column('actor_subject', sa.String()),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('target', sa.String(), nullable=False),
        sa.Column('details', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

def downgrade() -> None:
    op.drop_table('audit_log')
    op.drop_table('kyc_documents')
    op.drop_table('transfer_events')
    op.drop_table('transfers')
    op.drop_table('accounts')
    op.drop_table('users')