import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = {
  title: "About",
  description: "About WIYATA — Database Learning Center and SQL practice environment.",
};

const features = [
  {
    title: "SQL Query Studio & Lab",
    desc: "Interactive query workbench with sandboxed database environments for practicing SQL safely.",
  },
  {
    title: "SQL Challenges",
    desc: "Hands-on exercises with guided tasks to build query and database problem-solving skills.",
  },
  {
    title: "Career Roles",
    desc: "Role-based learning paths and skill context for DBA, DBRE, and data engineering tracks.",
  },
  {
    title: "Knowledge Center",
    desc: "Articles and references covering database concepts, operations, and practical workflows.",
  },
  {
    title: "Professional Tools",
    desc: "Catalog of database and observability tools with practical context for real-world use.",
  },
];

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-[#071A3A] text-slate-100">
      <header className="sticky top-0 z-40 border-b border-slate-800 bg-[#071A3A]/95 backdrop-blur-md">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 sm:px-6">
          <Link href="/" className="flex items-center gap-2.5 rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#F2B84B] focus-visible:ring-offset-2 focus-visible:ring-offset-[#071A3A]">
            <div className="relative h-8 w-8 overflow-hidden rounded-lg border border-[#F2B84B]/40 bg-[#10264A]">
              <Image src="/wiyata-app-icon.png" alt="" width={32} height={32} className="h-full w-full object-cover" />
            </div>
            <span className="text-sm font-extrabold tracking-wider text-white sm:text-base">WIYATA</span>
          </Link>
          <nav className="flex items-center gap-2 text-sm">
            <Link href="/" className="inline-flex min-h-10 items-center rounded-md px-3 py-2 font-medium text-slate-300 hover:bg-slate-800/60 hover:text-white focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#F2B84B]">
              Home
            </Link>
            <span className="inline-flex min-h-10 items-center rounded-md border border-[#F2B84B]/30 bg-[#10264A] px-3 py-2 font-medium text-[#F2B84B]">
              About
            </span>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-10 px-4 py-10 sm:px-6 sm:py-14">
        <section className="max-w-3xl">
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[#F2B84B]">About</p>
          <h1 className="mt-3 text-3xl font-extrabold tracking-tight text-white sm:text-4xl">About WIYATA</h1>
          <p className="mt-4 text-base leading-relaxed text-slate-300 sm:text-lg">
            WIYATA is a database learning center and professional reference for practicing SQL, exploring database concepts, and building operational skills across roles like DBA and DBRE.
          </p>
        </section>

        <section className="grid gap-6 lg:grid-cols-[minmax(0,1.4fr)_minmax(0,1fr)]">
          <div className="rounded-xl border border-slate-800 bg-[#0b2242] p-5 sm:p-6">
            <h2 className="text-xl font-bold text-white">What you can do</h2>
            <ul className="mt-4 space-y-3 text-sm leading-relaxed text-slate-300 sm:text-base">
              <li><span className="font-semibold text-white">Practice SQL:</span> run queries in sandboxed environments through the Query Studio & Lab.</li>
              <li><span className="font-semibold text-white">Learn by doing:</span> work through SQL challenges and role-oriented learning content.</li>
              <li><span className="font-semibold text-white">Explore references:</span> use the Knowledge Center, glossary, and tools catalog for practical database guidance.</li>
              <li><span className="font-semibold text-white">Connect topics:</span> selected knowledge articles link to related server-platform topics on <a href="https://ladang.sadeyan.my.id" className="text-[#F2B84B] underline decoration-[#F2B84B]/40 underline-offset-2 hover:text-[#ffd27a]">LADANG</a>.</li>
            </ul>
          </div>
          <div className="space-y-4">
            <div className="rounded-xl border border-slate-800 bg-[#10264A]/60 p-5">
              <h2 className="text-lg font-bold text-white">Access</h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">
                WIYATA is designed for interactive learning. Sandbox sessions are used for practice workflows so you can experiment without affecting production systems.
              </p>
            </div>
            <div className="rounded-xl border border-slate-800 bg-[#0b2242] p-5">
              <h2 className="text-lg font-bold text-white">Ecosystem</h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-300">
                WIYATA is part of the Sadeyan ecosystem alongside <a href="https://ladang.sadeyan.my.id" className="text-[#F2B84B] underline decoration-[#F2B84B]/40 underline-offset-2 hover:text-[#ffd27a]">LADANG</a> (server platform learning). Browse services on the <a href="https://dash.sadeyan.my.id/learning.html" className="text-[#F2B84B] underline decoration-[#F2B84B]/40 underline-offset-2 hover:text-[#ffd27a]">Learning dashboard</a>.
              </p>
            </div>
          </div>
        </section>

        <section aria-labelledby="features-heading" className="space-y-4">
          <h2 id="features-heading" className="text-2xl font-bold tracking-tight text-white">Platform areas</h2>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <div key={f.title} className="rounded-xl border border-slate-800 bg-[#0b2242] p-4 sm:p-5">
                <h3 className="text-base font-bold text-white sm:text-lg">{f.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-slate-400">{f.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
