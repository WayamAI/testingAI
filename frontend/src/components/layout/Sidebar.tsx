import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  ListChecks,
  Layers,
  Sparkles,
  Link2,
  Bug,
  Award,
  Rocket,
  type LucideIcon,
} from "lucide-react";

export interface SidebarItem {
  label: string;
  path: string;
  icon: LucideIcon;
}

export interface SidebarGroup {
  group: string;
  items: SidebarItem[];
}

// Authoritative nav tree for WayamAI Testing Cloud — pruned to Testing and
// Quality only (sub-project 2 spec §2026-08-22 "real-testing-execution").
// Every remaining item routes to a real, functional page — no stubs.
export const SIDEBAR_GROUPS: SidebarGroup[] = [
  {
    group: "Overview",
    items: [
      { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
    ],
  },
  {
    group: "Test Management",
    items: [
      { label: "Test Cases", path: "/test-cases", icon: ListChecks },
      { label: "Test Suites", path: "/test-suites", icon: Layers },
      { label: "AI Test Generator", path: "/ai/test-generator", icon: Sparkles },
      { label: "Connect Project", path: "/connect-project", icon: Link2 },
    ],
  },
  {
    group: "Quality",
    items: [
      { label: "Defects", path: "/quality/defects", icon: Bug },
      { label: "Quality Score", path: "/quality/score", icon: Award },
      { label: "Release Readiness", path: "/quality/release-readiness", icon: Rocket },
    ],
  },
];

export function Sidebar() {
  return (
    <aside className="flex h-screen w-64 shrink-0 flex-col border-r border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-900">
      <div className="flex items-center gap-2 border-b border-neutral-200 px-4 py-4 dark:border-neutral-800">
        <picture>
          <source
            srcSet="/assets/wayam-logo-dark.svg"
            media="(prefers-color-scheme: dark)"
          />
          <img
            src="/assets/wayam-logo-light.svg"
            alt="WayamAI Testing Cloud"
            className="h-9 w-auto max-w-[160px] object-contain"
          />
        </picture>
      </div>
      <nav className="flex-1 overflow-y-auto px-2 py-4">
        {SIDEBAR_GROUPS.map((group) => (
          <div key={group.group} className="mb-4">
            <h4 className="px-2 pb-1 text-xs font-semibold uppercase tracking-wide text-neutral-400 dark:text-neutral-500">
              {group.group}
            </h4>
            <ul className="space-y-0.5">
              {group.items.map((item) => (
                <li key={item.path}>
                  <NavLink
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center gap-2 rounded-md px-2 py-1.5 text-sm font-medium transition-colors ${
                        isActive
                          ? "bg-brand-50 text-brand-600 dark:bg-brand-950 dark:text-brand-400"
                          : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 dark:text-neutral-300 dark:hover:bg-neutral-800 dark:hover:text-neutral-100"
                      }`
                    }
                  >
                    <item.icon className="h-4 w-4 shrink-0" />
                    <span className="truncate">{item.label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </nav>
    </aside>
  );
}
