"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Guilds
    op.create_table(
        'guilds',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Guild brands
    op.create_table(
        'guild_brands',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('short_name', sa.String(length=100), nullable=False),
        sa.Column('icon_url', sa.String(length=512), nullable=True),
        sa.Column('primary_color', sa.Integer(), nullable=False),
        sa.Column('accent_color', sa.Integer(), nullable=False),
        sa.Column('neutral_color', sa.Integer(), nullable=False),
        sa.Column('footer_text', sa.String(length=255), nullable=True),
        sa.Column('tagline', sa.String(length=255), nullable=True),
        sa.Column('microcopy_voice', sa.String(length=50), nullable=False),
        sa.Column('embed_tone_preset', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('guild_id')
    )

    # User profiles
    op.create_table(
        'user_profiles',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('timezone', sa.String(length=100), nullable=True),
        sa.Column('currency_balance', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'guild_id', name='uq_user_guild')
    )

    # Tickets
    op.create_table(
        'tickets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), nullable=False),
        sa.Column('thread_id', sa.BigInteger(), nullable=True),
        sa.Column('creator_id', sa.BigInteger(), nullable=False),
        sa.Column('form_template_id', sa.Integer(), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('claimed_by_id', sa.BigInteger(), nullable=True),
        sa.Column('tags', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Ticket transcripts
    op.create_table(
        'ticket_transcripts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=False),
        sa.Column('content_markdown', sa.Text(), nullable=False),
        sa.Column('content_html', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Form templates
    op.create_table(
        'form_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.String(length=512), nullable=True),
        sa.Column('fields_json', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Form submissions
    op.create_table(
        'form_submissions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('form_template_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('ticket_id', sa.Integer(), nullable=True),
        sa.Column('data_json', sa.JSON(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('reviewer_id', sa.BigInteger(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['form_template_id'], ['form_templates.id'], ),
        sa.ForeignKeyConstraint(['ticket_id'], ['tickets.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Embed templates
    op.create_table(
        'embed_templates',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('embed_json', sa.JSON(), nullable=False),
        sa.Column('components_json', sa.JSON(), nullable=True),
        sa.Column('webhook_url', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Polls
    op.create_table(
        'polls',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), nullable=False),
        sa.Column('message_id', sa.BigInteger(), nullable=False),
        sa.Column('creator_id', sa.BigInteger(), nullable=False),
        sa.Column('question', sa.String(length=500), nullable=False),
        sa.Column('options_json', sa.JSON(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('closes_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('closed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Poll votes
    op.create_table(
        'poll_votes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('poll_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('option_indices', sa.ARRAY(sa.Integer()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['poll_id'], ['polls.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('poll_id', 'user_id', name='uq_poll_user')
    )

    # Reminders
    op.create_table(
        'reminders',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('channel_id', sa.BigInteger(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('remind_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('recurring_pattern', sa.String(length=50), nullable=True),
        sa.Column('completed', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Integration configs
    op.create_table(
        'integration_configs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('config_json', sa.JSON(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False),
        sa.Column('webhook_secret', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Audit logs
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=False),
        sa.Column('resource_id', sa.String(length=255), nullable=True),
        sa.Column('details_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Error logs
    op.create_table(
        'error_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('guild_id', sa.BigInteger(), nullable=True),
        sa.Column('correlation_id', sa.String(length=36), nullable=False),
        sa.Column('error_type', sa.String(length=100), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('stack_trace', sa.Text(), nullable=True),
        sa.Column('context_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('error_logs')
    op.drop_table('audit_logs')
    op.drop_table('integration_configs')
    op.drop_table('reminders')
    op.drop_table('poll_votes')
    op.drop_table('polls')
    op.drop_table('embed_templates')
    op.drop_table('form_submissions')
    op.drop_table('form_templates')
    op.drop_table('ticket_transcripts')
    op.drop_table('tickets')
    op.drop_table('user_profiles')
    op.drop_table('guild_brands')
    op.drop_table('guilds')
