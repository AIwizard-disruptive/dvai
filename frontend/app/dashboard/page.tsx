import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, FileText, CheckSquare, LightbulbIcon } from 'lucide-react'

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <header className="border-b">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-bold text-xl">Meeting Intelligence</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/dashboard/meetings">
              <Button variant="ghost">Meetings</Button>
            </Link>
            <Link href="/dashboard/action-items">
              <Button variant="ghost">Action Items</Button>
            </Link>
            <Link href="/dashboard/settings">
              <Button variant="ghost">Settings</Button>
            </Link>
          </nav>
        </div>
      </header>

      <main className="flex-1 container py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">
              Welcome back! Here's what's happening with your meetings.
            </p>
          </div>
          <Link href="/dashboard/upload">
            <Button>
              <Plus className="mr-2 h-4 w-4" /> Upload Meeting
            </Button>
          </Link>
        </div>

        <div className="grid gap-6 md:grid-cols-3 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Total Meetings
              </CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">12</div>
              <p className="text-xs text-muted-foreground">
                +2 from last week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Action Items
              </CardTitle>
              <CheckSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">23</div>
              <p className="text-xs text-muted-foreground">
                8 completed this week
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Decisions Made
              </CardTitle>
              <LightbulbIcon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">17</div>
              <p className="text-xs text-muted-foreground">
                +5 from last week
              </p>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Recent Meetings</CardTitle>
              <CardDescription>
                Your most recent meeting transcripts
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  {
                    title: 'Product Roadmap Review',
                    date: '2025-12-10',
                    status: 'completed',
                  },
                  {
                    title: 'Team Standup',
                    date: '2025-12-09',
                    status: 'completed',
                  },
                  {
                    title: 'Client Kickoff Call',
                    date: '2025-12-08',
                    status: 'processing',
                  },
                ].map((meeting, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between border-b pb-3 last:border-0 last:pb-0"
                  >
                    <div>
                      <p className="font-medium">{meeting.title}</p>
                      <p className="text-sm text-muted-foreground">
                        {meeting.date}
                      </p>
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded-full ${
                        meeting.status === 'completed'
                          ? 'bg-green-100 text-green-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {meeting.status}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Open Action Items</CardTitle>
              <CardDescription>
                Items that need your attention
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  {
                    title: 'Complete design mockups',
                    owner: 'Alice',
                    due: '2025-12-15',
                  },
                  {
                    title: 'Review pricing proposal',
                    owner: 'Bob',
                    due: '2025-12-13',
                  },
                  {
                    title: 'Schedule follow-up meeting',
                    owner: 'Charlie',
                    due: '2025-12-12',
                  },
                ].map((item, i) => (
                  <div
                    key={i}
                    className="flex items-center justify-between border-b pb-3 last:border-0 last:pb-0"
                  >
                    <div>
                      <p className="font-medium">{item.title}</p>
                      <p className="text-sm text-muted-foreground">
                        Assigned to {item.owner}
                      </p>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      Due {item.due}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}




