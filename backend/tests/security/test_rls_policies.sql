-- RLS Policy Tests
-- Run these tests against your Supabase database to verify RLS is working

-- Test 1: Users can only see their org's data
BEGIN;
  -- Create test data
  INSERT INTO orgs (id, name) VALUES 
    ('11111111-1111-1111-1111-111111111111', 'Test Org 1'),
    ('22222222-2222-2222-2222-222222222222', 'Test Org 2');
  
  INSERT INTO org_memberships (org_id, user_id, role) VALUES
    ('11111111-1111-1111-1111-111111111111', '99999999-9999-9999-9999-999999999999', 'owner'),
    ('22222222-2222-2222-2222-222222222222', '88888888-8888-8888-8888-888888888888', 'owner');
  
  INSERT INTO meetings (org_id, title) VALUES
    ('11111111-1111-1111-1111-111111111111', 'Org 1 Meeting'),
    ('22222222-2222-2222-2222-222222222222', 'Org 2 Meeting');
  
  -- Set user context to user from Org 1
  SET request.jwt.claims = '{"sub": "99999999-9999-9999-9999-999999999999"}';
  
  -- Should see only Org 1 meeting
  SELECT assert_equals(
    (SELECT COUNT(*) FROM meetings WHERE org_id = '11111111-1111-1111-1111-111111111111'),
    1,
    'User should see own org meetings'
  );
  
  -- Should NOT see Org 2 meeting
  SELECT assert_equals(
    (SELECT COUNT(*) FROM meetings WHERE org_id = '22222222-2222-2222-2222-222222222222'),
    0,
    'User should NOT see other org meetings'
  );

ROLLBACK;

-- Test 2: Viewers can read but not write
BEGIN;
  INSERT INTO orgs (id, name) VALUES ('33333333-3333-3333-3333-333333333333', 'Test Org 3');
  INSERT INTO org_memberships (org_id, user_id, role) VALUES
    ('33333333-3333-3333-3333-333333333333', '77777777-7777-7777-7777-777777777777', 'viewer');
  
  SET request.jwt.claims = '{"sub": "77777777-7777-7777-7777-777777777777"}';
  
  -- Should fail to insert (viewers cannot write)
  DO $$
  BEGIN
    INSERT INTO meetings (org_id, title) VALUES
      ('33333333-3333-3333-3333-333333333333', 'Test Meeting');
    RAISE EXCEPTION 'Viewer should not be able to insert';
  EXCEPTION WHEN insufficient_privilege THEN
    -- Expected
  END $$;

ROLLBACK;

-- Test 3: Only admins can manage integrations
BEGIN;
  INSERT INTO orgs (id, name) VALUES ('44444444-4444-4444-4444-444444444444', 'Test Org 4');
  INSERT INTO org_memberships (org_id, user_id, role) VALUES
    ('44444444-4444-4444-4444-444444444444', '66666666-6666-6666-6666-666666666666', 'member');
  
  SET request.jwt.claims = '{"sub": "66666666-6666-6666-6666-666666666666"}';
  
  -- Member should NOT be able to insert integration
  DO $$
  BEGIN
    INSERT INTO integrations (org_id, provider) VALUES
      ('44444444-4444-4444-4444-444444444444', 'linear');
    RAISE EXCEPTION 'Member should not be able to insert integration';
  EXCEPTION WHEN insufficient_privilege THEN
    -- Expected
  END $$;

ROLLBACK;

-- Test 4: Cross-org data isolation
BEGIN;
  INSERT INTO orgs (id, name) VALUES 
    ('55555555-5555-5555-5555-555555555555', 'Org A'),
    ('66666666-6666-6666-6666-666666666666', 'Org B');
  
  INSERT INTO org_memberships (org_id, user_id, role) VALUES
    ('55555555-5555-5555-5555-555555555555', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'owner');
  
  INSERT INTO meetings (id, org_id, title) VALUES
    ('11111111-1111-1111-1111-111111111111', '55555555-5555-5555-5555-555555555555', 'Org A Meeting'),
    ('22222222-2222-2222-2222-222222222222', '66666666-6666-6666-6666-666666666666', 'Org B Meeting');
  
  SET request.jwt.claims = '{"sub": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"}';
  
  -- User from Org A should NOT be able to access Org B's meeting
  SELECT assert_equals(
    (SELECT COUNT(*) FROM meetings WHERE id = '22222222-2222-2222-2222-222222222222'),
    0,
    'Cross-org data should be isolated'
  );

ROLLBACK;





