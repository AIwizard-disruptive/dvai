-- ============================================================================
-- CREATE TASKS FOR SERGE@ AND WIZARD@
-- Creates comprehensive task list for testing Google Tasks sync
-- ============================================================================

DO $$
DECLARE
    v_org_id UUID;
    v_serge_id UUID;
    v_wizard_id UUID;
    v_task_count INTEGER := 0;
BEGIN

-- Get org_id
SELECT id INTO v_org_id FROM orgs LIMIT 1;

IF v_org_id IS NULL THEN
    RAISE EXCEPTION 'No org found!';
END IF;

-- Get Serge's person_id
SELECT id INTO v_serge_id 
FROM people 
WHERE email IN ('serge@disruptiveventures.se', 'serge.lachapelle@disruptiveventures.se')
LIMIT 1;

-- Get Wizard's person_id
SELECT id INTO v_wizard_id 
FROM people 
WHERE email = 'wizard@disruptiveventures.se'
LIMIT 1;

IF v_serge_id IS NULL THEN
    RAISE EXCEPTION 'Serge not found! Run SETUP_WIZARD_SERGE_SYNC.sql first';
END IF;

IF v_wizard_id IS NULL THEN
    RAISE EXCEPTION 'Wizard not found! Run SETUP_WIZARD_SERGE_SYNC.sql first';
END IF;

RAISE NOTICE 'Creating tasks for:';
RAISE NOTICE '  Serge: %', v_serge_id;
RAISE NOTICE '  Wizard: %', v_wizard_id;
RAISE NOTICE '';

-- ============================================================================
-- SERGE'S TASKS
-- ============================================================================

-- Investment & Dealflow Tasks
INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id, 
 'Review Q4 portfolio company metrics',
 'Analyze Q4 performance across all portfolio companies. Focus on revenue growth, burn rate, and runway.',
 'todo', 'high', CURRENT_DATE + 3, 'manual',
 ARRAY['portfolio', 'metrics', 'q4']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id,
 'Due diligence: TechStartup AB',
 'Complete technical and financial due diligence for Series A investment. Review cap table, financials, and technical architecture.',
 'in_progress', 'urgent', CURRENT_DATE + 5, 'manual',
 ARRAY['dealflow', 'due-diligence', 'series-a']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id,
 'Prepare board meeting agenda - PortfolioCo',
 'Create agenda for upcoming board meeting. Include: Q4 results, 2025 strategy, funding needs.',
 'todo', 'high', CURRENT_DATE + 7, 'manual',
 ARRAY['board-meeting', 'portfolio']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id,
 'Follow up: AI startup pitch from last week',
 'Schedule follow-up call with AI startup team. Review financials and customer traction.',
 'todo', 'medium', CURRENT_DATE + 2, 'manual',
 ARRAY['dealflow', 'follow-up']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id,
 'Update LP quarterly report',
 'Compile Q4 portfolio performance and market insights for Limited Partners. Include valuations and exits.',
 'todo', 'high', CURRENT_DATE + 10, 'manual',
 ARRAY['reporting', 'lp', 'quarterly']);

v_task_count := v_task_count + 1;

-- Network & Relationships
INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id,
 'Coffee meeting with enterprise SaaS founder',
 'Discuss market trends and potential investment opportunities in enterprise SaaS.',
 'todo', 'medium', CURRENT_DATE + 4, 'manual',
 ARRAY['networking', 'saas']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id,
 'Introduce PortfolioCo to potential customer',
 'Connect PortfolioCo CEO with enterprise contact at TechCorp. Could be major customer.',
 'todo', 'medium', CURRENT_DATE + 3, 'manual',
 ARRAY['portfolio-support', 'networking']);

v_task_count := v_task_count + 1;

-- Strategy & Planning
INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id,
 'Define 2025 investment thesis',
 'Workshop with team to refine investment focus areas: AI/ML, Climate Tech, Enterprise SaaS.',
 'in_progress', 'high', CURRENT_DATE + 14, 'manual',
 ARRAY['strategy', '2025']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id,
 'Review and approve portfolio company hiring plan',
 'Review hiring plans for key portfolio companies. Approve budget allocations.',
 'todo', 'medium', CURRENT_DATE + 5, 'manual',
 ARRAY['portfolio-support', 'hiring']);

v_task_count := v_task_count + 1;

-- Completed Tasks (for testing sync)
INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags, completed_at)
VALUES 
(v_org_id, v_serge_id,
 'Send term sheet to Nordic SaaS startup',
 'Term sheet sent and accepted. Moving to due diligence phase.',
 'done', 'high', CURRENT_DATE - 2, 'manual',
 ARRAY['dealflow', 'term-sheet'], NOW() - INTERVAL '2 days');

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags, completed_at)
VALUES 
(v_org_id, v_serge_id,
 'Attend Nordic Startup Conference',
 'Networked with 15+ founders, identified 3 promising startups for pipeline.',
 'done', 'medium', CURRENT_DATE - 5, 'manual',
 ARRAY['networking', 'conference'], NOW() - INTERVAL '5 days');

v_task_count := v_task_count + 1;

-- ============================================================================
-- WIZARD'S TASKS
-- ============================================================================

-- Meeting & Admin Tasks
INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Process meeting notes from investor call',
 'Extract action items and key decisions from Monday investor call. Create follow-up tasks.',
 'todo', 'high', CURRENT_DATE + 1, 'manual',
 ARRAY['meeting-notes', 'admin']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Schedule Q1 board meetings for all portfolio companies',
 'Coordinate with 8 portfolio companies to schedule Q1 board meetings. Send calendar invites.',
 'in_progress', 'high', CURRENT_DATE + 7, 'manual',
 ARRAY['scheduling', 'board-meetings']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Update CRM with new dealflow contacts',
 'Add 12 new startup contacts from last week meetings to CRM with notes.',
 'todo', 'medium', CURRENT_DATE + 2, 'manual',
 ARRAY['crm', 'dealflow']);

v_task_count := v_task_count + 1;

-- Document Management
INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Organize Q4 portfolio documents in Drive',
 'Create folder structure and organize Q4 board decks, financial reports, and contracts.',
 'todo', 'low', CURRENT_DATE + 5, 'manual',
 ARRAY['admin', 'google-drive']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Generate LP report distribution list',
 'Compile email list for Q4 LP report distribution. Verify all contacts are current.',
 'todo', 'medium', CURRENT_DATE + 8, 'manual',
 ARRAY['reporting', 'lp']);

v_task_count := v_task_count + 1;

-- Automation & Tools
INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Set up automated weekly portfolio metrics report',
 'Configure automation to pull key metrics from portfolio companies weekly.',
 'in_progress', 'medium', CURRENT_DATE + 10, 'manual',
 ARRAY['automation', 'reporting']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Test Google Tasks sync integration',
 'Verify bidirectional sync between database and Google Tasks is working correctly.',
 'todo', 'high', CURRENT_DATE + 1, 'manual',
 ARRAY['testing', 'integration']);

v_task_count := v_task_count + 1;

-- Research & Analysis
INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Research AI trends for investment thesis',
 'Compile report on emerging AI trends: LLMs, AI agents, enterprise AI adoption.',
 'todo', 'medium', CURRENT_DATE + 14, 'manual',
 ARRAY['research', 'ai', 'market-analysis']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Analyze competitor fund strategies',
 'Review investment focus and portfolio of 5 competing VC funds in Nordics.',
 'todo', 'low', CURRENT_DATE + 20, 'manual',
 ARRAY['research', 'competitive-analysis']);

v_task_count := v_task_count + 1;

-- Completed Tasks
INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags, completed_at)
VALUES 
(v_org_id, v_wizard_id,
 'Send meeting invites for team sync',
 'All invites sent. Meeting confirmed for Friday 10am.',
 'done', 'medium', CURRENT_DATE - 1, 'manual',
 ARRAY['scheduling', 'team'], NOW() - INTERVAL '1 day');

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags, completed_at)
VALUES 
(v_org_id, v_wizard_id,
 'Update portfolio company contact list',
 'Contact list updated with new CEOs and CFOs across portfolio.',
 'done', 'low', CURRENT_DATE - 3, 'manual',
 ARRAY['crm', 'portfolio'], NOW() - INTERVAL '3 days');

v_task_count := v_task_count + 1;

-- ============================================================================
-- SHARED TASKS (assigned to both)
-- ============================================================================

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_serge_id,
 'Prepare annual investor meeting presentation',
 'Collaborate on annual meeting deck: portfolio highlights, performance, 2025 outlook.',
 'in_progress', 'urgent', CURRENT_DATE + 21, 'manual',
 ARRAY['presentation', 'investor-meeting', 'shared']);

v_task_count := v_task_count + 1;

INSERT INTO tasks (org_id, assigned_to_person_id, title, description, status, priority, due_date, source, tags)
VALUES 
(v_org_id, v_wizard_id,
 'Prepare annual investor meeting presentation',
 'Collaborate on annual meeting deck: portfolio highlights, performance, 2025 outlook.',
 'in_progress', 'urgent', CURRENT_DATE + 21, 'manual',
 ARRAY['presentation', 'investor-meeting', 'shared']);

v_task_count := v_task_count + 1;

-- ============================================================================
-- SUMMARY
-- ============================================================================

RAISE NOTICE '';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE 'TASKS CREATED SUCCESSFULLY';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE 'Total tasks created: %', v_task_count;
RAISE NOTICE '';
RAISE NOTICE 'Breakdown:';
RAISE NOTICE '  Serge tasks: 13';
RAISE NOTICE '  Wizard tasks: 12';
RAISE NOTICE '';
RAISE NOTICE 'Status distribution:';
RAISE NOTICE '  - To Do: %', (SELECT COUNT(*) FROM tasks WHERE status = 'todo');
RAISE NOTICE '  - In Progress: %', (SELECT COUNT(*) FROM tasks WHERE status = 'in_progress');
RAISE NOTICE '  - Done: %', (SELECT COUNT(*) FROM tasks WHERE status = 'done');
RAISE NOTICE '';
RAISE NOTICE 'Priority distribution:';
RAISE NOTICE '  - Urgent: %', (SELECT COUNT(*) FROM tasks WHERE priority = 'urgent');
RAISE NOTICE '  - High: %', (SELECT COUNT(*) FROM tasks WHERE priority = 'high');
RAISE NOTICE '  - Medium: %', (SELECT COUNT(*) FROM tasks WHERE priority = 'medium');
RAISE NOTICE '  - Low: %', (SELECT COUNT(*) FROM tasks WHERE priority = 'low');
RAISE NOTICE '';
RAISE NOTICE '════════════════════════════════════════════════════════════';
RAISE NOTICE 'NEXT STEPS:';
RAISE NOTICE '1. Run: python backend/sync_google_tasks.py';
RAISE NOTICE '2. Check Google Tasks - should see all tasks!';
RAISE NOTICE '3. Update a task in Google Tasks';
RAISE NOTICE '4. Run sync again - database should update!';
RAISE NOTICE '════════════════════════════════════════════════════════════';

END $$;

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- View Serge's tasks
SELECT 
    title,
    status,
    priority,
    due_date,
    tags
FROM tasks t
JOIN people p ON p.id = t.assigned_to_person_id
WHERE p.email IN ('serge@disruptiveventures.se', 'serge.lachapelle@disruptiveventures.se')
ORDER BY 
    CASE priority 
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    due_date ASC;

-- View Wizard's tasks
SELECT 
    title,
    status,
    priority,
    due_date,
    tags
FROM tasks t
JOIN people p ON p.id = t.assigned_to_person_id
WHERE p.email = 'wizard@disruptiveventures.se'
ORDER BY 
    CASE priority 
        WHEN 'urgent' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
    END,
    due_date ASC;

-- All tasks summary
SELECT 
    p.name,
    COUNT(*) as total_tasks,
    SUM(CASE WHEN t.status = 'todo' THEN 1 ELSE 0 END) as todo,
    SUM(CASE WHEN t.status = 'in_progress' THEN 1 ELSE 0 END) as in_progress,
    SUM(CASE WHEN t.status = 'done' THEN 1 ELSE 0 END) as done
FROM tasks t
JOIN people p ON p.id = t.assigned_to_person_id
WHERE p.email IN ('serge@disruptiveventures.se', 'serge.lachapelle@disruptiveventures.se', 'wizard@disruptiveventures.se')
GROUP BY p.name
ORDER BY p.name;
