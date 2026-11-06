export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8 bg-[var(--background)] text-[var(--foreground)]">
      <div className="max-w-2xl text-center space-y-6">
        <div className="inline-block px-3 py-1 text-xs font-semibold uppercase tracking-wider rounded-full bg-[var(--surface)] text-[var(--wiyata-gold)] border border-[var(--wiyata-gold)]/20">
          Database Workbench & Learning Ecosystem
        </div>
        <h1 className="text-5xl font-extrabold tracking-tight text-[var(--foreground)] sm:text-6xl">
          WIYATA
        </h1>
        <p className="text-xl text-[var(--muted)]">
          Your Database Learning Center
        </p>
        <p className="text-sm text-[var(--muted)] max-w-md mx-auto leading-relaxed">
          Learn, build, explore, and master database technologies — from your first SQL query to professional DBA workflows.
        </p>
        <div className="pt-4 flex flex-wrap justify-center gap-3 text-xs text-[var(--muted)]">
          <span className="px-3 py-1.5 rounded-md bg-[var(--surface)] border border-slate-700/50">
            ✔ SQLite Sandbox
          </span>
          <span className="px-3 py-1.5 rounded-md bg-[var(--surface)] border border-slate-700/50">
            ✔ Query Studio
          </span>
          <span className="px-3 py-1.5 rounded-md bg-[var(--surface)] border border-slate-700/50">
            ✔ Knowledge Center
          </span>
          <span className="px-3 py-1.5 rounded-md bg-[var(--surface)] border border-slate-700/50">
            ✔ Professional Tools
          </span>
        </div>
      </div>
    </main>
  );
}
