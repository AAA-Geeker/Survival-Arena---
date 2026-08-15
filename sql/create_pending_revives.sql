-- ============================================================
-- Survival Arena - pending_revives Table Migration
-- Cross-device friend revival tokens
-- Run this in Supabase SQL Editor: https://app.supabase.com
-- ============================================================

CREATE TABLE IF NOT EXISTS pending_revives (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  created_at  TIMESTAMPTZ DEFAULT NOW(),
  from_player TEXT NOT NULL,
  to_player   TEXT NOT NULL,
  time        BIGINT NOT NULL
);

-- Index for fast lookup by recipient
CREATE INDEX IF NOT EXISTS idx_pending_revives_to_player
  ON pending_revives (to_player);

-- Index for fast lookup by sender (dedup checks)
CREATE INDEX IF NOT EXISTS idx_pending_revives_from_player
  ON pending_revives (from_player);

-- Composite index for dedup queries
CREATE INDEX IF NOT EXISTS idx_pending_revives_pair
  ON pending_revives (from_player, to_player);

-- Enable Row Level Security
ALTER TABLE pending_revives ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- IMPORTANT: idempotent policy setup
-- Re-running this file SAFELY recreates ALL anonymous policies.
-- If a policy was ever dropped/altered (e.g. the INSERT policy missing
-- due to a partial migration), re-running this restores it.
-- ============================================================

-- Allow anonymous inserts (game clients use publishable key, which maps to the "anon" role)
-- REQUIRED for the friend-revive feature to work across devices.
-- Explicit TO anon, authenticated: the publishable key authenticates as "anon"; if the
-- policy omits the role it defaults to PUBLIC (also fine) but explicit is safer against
-- Supabase's wizard generating authenticated-only policies that break anonymous inserts.
DROP POLICY IF EXISTS "Allow anonymous insert" ON pending_revives;
CREATE POLICY "Allow anonymous insert" ON pending_revives
  FOR INSERT TO anon, authenticated WITH CHECK (true);

-- Allow anonymous selects
DROP POLICY IF EXISTS "Allow anonymous select" ON pending_revives;
CREATE POLICY "Allow anonymous select" ON pending_revives
  FOR SELECT TO anon, authenticated USING (true);

-- Allow anonymous deletes (for consuming revives after verification)
DROP POLICY IF EXISTS "Allow anonymous delete" ON pending_revives;
CREATE POLICY "Allow anonymous delete" ON pending_revives
  FOR DELETE TO anon, authenticated USING (true);
