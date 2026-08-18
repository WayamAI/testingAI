import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  FolderKanban,
  Activity,
  ClipboardList,
  ListChecks,
  Layers,
  PlayCircle,
  CalendarClock,
  Globe,
  Sparkles,
  Stethoscope,
  Lightbulb,
  Gauge,
  Globe2,
  ScanEye,
  Monitor,
  Accessibility,
  Plug,
  ListTree,
  FileCode2,
  Server,
  Smartphone,
  Tablet,
  PieChart,
  Zap,
  TrendingUp,
  BarChart3,
  Shield,
  ShieldAlert,
  ShieldCheck,
  Database,
  EyeOff,
  Sprout,
  Workflow,
  Clock,
  Wand2,
  Award,
  Rocket,
  DoorOpen,
  Bug,
  Link2,
  GitBranch,
  MessageSquare,
  Webhook,
  Building2,
  Users,
  CreditCard,
  History,
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

export const SIDEBAR_GROUPS: SidebarGroup[] = [
  {
    group: "Overview",
    items: [
      { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
      { label: "Projects", path: "/projects", icon: FolderKanban },
      { label: "Activity Feed", path: "/activity", icon: Activity },
    ],
  },
  {
    group: "Test Management",
    items: [
      { label: "Requirements", path: "/requirements", icon: ClipboardList },
      { label: "Test Suites", path: "/test-suites", icon: Layers },
      { label: "Test Cases", path: "/test-cases", icon: ListChecks },
      { label: "Test Runs", path: "/test-runs", icon: PlayCircle },
      { label: "Test Plans", path: "/test-plans", icon: CalendarClock },
      { label: "Environments", path: "/environments", icon: Globe },
    ],
  },
  {
    group: "AI Testing",
    items: [
      { label: "AI Test Generator", path: "/ai/generator", icon: Sparkles },
      { label: "AI Failure Analysis", path: "/ai/failure-analysis", icon: Stethoscope },
      { label: "AI Insights", path: "/ai/insights", icon: Lightbulb },
      { label: "Test Optimization", path: "/ai/optimization", icon: Gauge },
    ],
  },
  {
    group: "Web Testing",
    items: [
      { label: "Web Test Suites", path: "/web-testing/suites", icon: Globe2 },
      { label: "Visual Regression", path: "/web-testing/visual-regression", icon: ScanEye },
      { label: "Cross-Browser Testing", path: "/web-testing/cross-browser", icon: Monitor },
      { label: "Accessibility Testing", path: "/web-testing/accessibility", icon: Accessibility },
    ],
  },
  {
    group: "API Testing",
    items: [
      { label: "API Collections", path: "/api-testing/collections", icon: Plug },
      { label: "API Test Runs", path: "/api-testing/runs", icon: ListTree },
      { label: "Contract Testing", path: "/api-testing/contracts", icon: FileCode2 },
      { label: "Mock Servers", path: "/api-testing/mocks", icon: Server },
    ],
  },
  {
    group: "Mobile Testing",
    items: [
      { label: "Mobile Test Suites", path: "/mobile-testing/suites", icon: Smartphone },
      { label: "Device Farm", path: "/mobile-testing/devices", icon: Tablet },
      { label: "App Coverage", path: "/mobile-testing/coverage", icon: PieChart },
    ],
  },
  {
    group: "Performance",
    items: [
      { label: "Load Testing", path: "/performance/load", icon: Zap },
      { label: "Stress Testing", path: "/performance/stress", icon: TrendingUp },
      { label: "Performance Trends", path: "/performance/trends", icon: BarChart3 },
    ],
  },
  {
    group: "Security",
    items: [
      { label: "Security Scans", path: "/security/scans", icon: Shield },
      { label: "Vulnerability Reports", path: "/security/vulnerabilities", icon: ShieldAlert },
      { label: "Compliance", path: "/security/compliance", icon: ShieldCheck },
    ],
  },
  {
    group: "Data",
    items: [
      { label: "Test Data Management", path: "/data/test-data", icon: Database },
      { label: "Data Masking", path: "/data/masking", icon: EyeOff },
      { label: "Fixtures & Seeds", path: "/data/fixtures", icon: Sprout },
    ],
  },
  {
    group: "Automation",
    items: [
      { label: "CI/CD Pipelines", path: "/automation/pipelines", icon: Workflow },
      { label: "Scheduled Runs", path: "/automation/schedules", icon: Clock },
      { label: "Self-Healing Tests", path: "/automation/self-healing", icon: Wand2 },
    ],
  },
  {
    group: "Quality",
    items: [
      { label: "Quality Score", path: "/quality/score", icon: Award },
      { label: "Release Readiness", path: "/quality/releases", icon: Rocket },
      { label: "Quality Gates", path: "/quality/gates", icon: DoorOpen },
      { label: "Defects", path: "/defects", icon: Bug },
    ],
  },
  {
    group: "Integrations",
    items: [
      { label: "Jira", path: "/integrations/jira", icon: Link2 },
      { label: "GitHub", path: "/integrations/github", icon: GitBranch },
      { label: "Slack", path: "/integrations/slack", icon: MessageSquare },
      { label: "Webhooks", path: "/integrations/webhooks", icon: Webhook },
    ],
  },
  {
    group: "Administration",
    items: [
      { label: "Organization Settings", path: "/admin/organization", icon: Building2 },
      { label: "Users & Roles", path: "/admin/users", icon: Users },
      { label: "Billing", path: "/admin/billing", icon: CreditCard },
      { label: "Audit Log", path: "/admin/audit-log", icon: History },
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
