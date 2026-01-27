export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Vezbot Dashboard</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <div className="bg-secondary p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Setup</h2>
            <p className="text-muted-foreground">Configure your server</p>
          </div>
          <div className="bg-secondary p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Tickets</h2>
            <p className="text-muted-foreground">Manage ticket system</p>
          </div>
          <div className="bg-secondary p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-2">Branding</h2>
            <p className="text-muted-foreground">Customize appearance</p>
          </div>
        </div>
      </div>
    </div>
  )
}
