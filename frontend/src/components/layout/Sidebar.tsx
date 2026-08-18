import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  BrainCircuit,
  Activity,
  ListChecks,
  Layers,
  CalendarClock,
  Repeat,
  Compass,
  Sparkles,
  Route,
  Gauge,
  History,
  Stethoscope,
  Bot,
  Globe,
  Monitor,
  Columns2,
  ScanEye,
  Accessibility,
  Plug,
  ListTree,
  Search,
  FileCode2,
  Radar,
  Smartphone,
  LayoutGrid,
  Cpu,
  Apple,
  Zap,
  TrendingUp,
  ActivitySquare,
  Timer,
  Hourglass,
  Maximize,
  Shield,
  ShieldAlert,
  KeyRound,
  Lock,
  FileText,
  Database,
  ClipboardCheck,
  GitMerge,
  Network,
  Workflow,
  PlayCircle,
  Clock,
  GitBranch,
  Infinity as InfinityIcon,
  PieChart,
  AlertTriangle,
  Bug,
  Shuffle,
  Award,
  Rocket,
  DoorOpen,
  Link2,
  MessageSquare,
  UsersRound,
  Triangle,
  Cloud,
  CloudCog,
  CloudLightning,
  Container,
  Hexagon,
  BarChart3,
  Siren,
  GitCommitHorizontal,
  Building2,
  Users,
  ShieldCheck,
  Key,
  CreditCard,
  Settings,
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

// Authoritative nav tree — spec §20 (WayamAI Testing Cloud sidebar), 13
// groups / 80 items, verbatim group and item labels. Paths are a reasonable
// kebab-case convention under each group's logical route prefix; Task 15's
// router is expected to match these exactly.
export const SIDEBAR_GROUPS: SidebarGroup[] = [
  {
    group: "Overview",
    items: [
      { label: "Dashboard", path: "/dashboard", icon: LayoutDashboard },
      { label: "Quality Intelligence", path: "/quality-intelligence", icon: BrainCircuit },
      { label: "Activity", path: "/activity", icon: Activity },
    ],
  },
  {
    group: "Test Management",
    items: [
      { label: "Test Cases", path: "/test-cases", icon: ListChecks },
      { label: "Test Suites", path: "/test-suites", icon: Layers },
      { label: "Test Plans", path: "/test-plans", icon: CalendarClock },
      { label: "Test Cycles", path: "/test-cycles", icon: Repeat },
      { label: "Test Explorer", path: "/test-explorer", icon: Compass },
    ],
  },
  {
    group: "AI Testing",
    items: [
      { label: "AI Test Generator", path: "/ai/test-generator", icon: Sparkles },
      { label: "AI Test Planner", path: "/ai/test-planner", icon: Route },
      { label: "AI Test Optimizer", path: "/ai/test-optimizer", icon: Gauge },
      { label: "AI Regression Intelligence", path: "/ai/regression-intelligence", icon: History },
      { label: "AI Failure Analysis", path: "/ai/failure-analysis", icon: Stethoscope },
      { label: "AI Quality Copilot", path: "/ai/quality-copilot", icon: Bot },
    ],
  },
  {
    group: "Web Testing",
    items: [
      { label: "Web Testing", path: "/web-testing", icon: Globe },
      { label: "Browser Testing", path: "/web-testing/browser-testing", icon: Monitor },
      { label: "Cross Browser", path: "/web-testing/cross-browser", icon: Columns2 },
      { label: "Visual Testing", path: "/web-testing/visual-testing", icon: ScanEye },
      { label: "Accessibility", path: "/web-testing/accessibility", icon: Accessibility },
    ],
  },
  {
    group: "API Testing",
    items: [
      { label: "API Testing", path: "/api-testing", icon: Plug },
      { label: "API Collections", path: "/api-testing/collections", icon: ListTree },
      { label: "API Explorer", path: "/api-testing/explorer", icon: Search },
      { label: "Contract Testing", path: "/api-testing/contract-testing", icon: FileCode2 },
      { label: "API Monitoring", path: "/api-testing/monitoring", icon: Radar },
    ],
  },
  {
    group: "Mobile Testing",
    items: [
      { label: "Mobile Testing", path: "/mobile-testing", icon: Smartphone },
      { label: "Device Matrix", path: "/mobile-testing/device-matrix", icon: LayoutGrid },
      { label: "Android", path: "/mobile-testing/android", icon: Cpu },
      { label: "iOS", path: "/mobile-testing/ios", icon: Apple },
    ],
  },
  {
    group: "Performance",
    items: [
      { label: "Performance", path: "/performance", icon: Zap },
      { label: "Load Testing", path: "/performance/load-testing", icon: TrendingUp },
      { label: "Stress Testing", path: "/performance/stress-testing", icon: ActivitySquare },
      { label: "Spike Testing", path: "/performance/spike-testing", icon: Timer },
      { label: "Endurance Testing", path: "/performance/endurance-testing", icon: Hourglass },
      { label: "Scalability", path: "/performance/scalability", icon: Maximize },
    ],
  },
  {
    group: "Security",
    items: [
      { label: "Security Testing", path: "/security", icon: Shield },
      { label: "API Security", path: "/security/api-security", icon: ShieldAlert },
      { label: "Authentication", path: "/security/authentication", icon: KeyRound },
      { label: "Authorization", path: "/security/authorization", icon: Lock },
      { label: "Security Reports", path: "/security/reports", icon: FileText },
    ],
  },
  {
    group: "Data",
    items: [
      { label: "Database Testing", path: "/data/database-testing", icon: Database },
      { label: "Data Validation", path: "/data/validation", icon: ClipboardCheck },
      { label: "Integration Testing", path: "/data/integration-testing", icon: GitMerge },
      { label: "Microservices", path: "/data/microservices", icon: Network },
    ],
  },
  {
    group: "Automation",
    items: [
      { label: "Automation Studio", path: "/automation/studio", icon: Workflow },
      { label: "Automation Tests", path: "/automation/tests", icon: PlayCircle },
      { label: "Schedules", path: "/automation/schedules", icon: Clock },
      { label: "Test Pipelines", path: "/automation/pipelines", icon: GitBranch },
      { label: "CI/CD", path: "/automation/ci-cd", icon: InfinityIcon },
    ],
  },
  {
    group: "Quality",
    items: [
      { label: "Coverage", path: "/quality/coverage", icon: PieChart },
      { label: "Risk Analysis", path: "/quality/risk-analysis", icon: AlertTriangle },
      { label: "Defects", path: "/quality/defects", icon: Bug },
      { label: "Flaky Tests", path: "/quality/flaky-tests", icon: Shuffle },
      { label: "Quality Score", path: "/quality/score", icon: Award },
      { label: "Release Readiness", path: "/quality/release-readiness", icon: Rocket },
      { label: "Quality Gates", path: "/quality/gates", icon: DoorOpen },
    ],
  },
  {
    group: "Integrations",
    items: [
      { label: "GitHub", path: "/integrations/github", icon: GitBranch },
      { label: "GitLab", path: "/integrations/gitlab", icon: GitMerge },
      { label: "Bitbucket", path: "/integrations/bitbucket", icon: GitCommitHorizontal },
      { label: "Jira", path: "/integrations/jira", icon: Link2 },
      { label: "Slack", path: "/integrations/slack", icon: MessageSquare },
      { label: "Teams", path: "/integrations/teams", icon: UsersRound },
      { label: "Vercel", path: "/integrations/vercel", icon: Triangle },
      { label: "AWS", path: "/integrations/aws", icon: Cloud },
      { label: "Azure", path: "/integrations/azure", icon: CloudCog },
      { label: "GCP", path: "/integrations/gcp", icon: CloudLightning },
      { label: "Docker", path: "/integrations/docker", icon: Container },
      { label: "Kubernetes", path: "/integrations/kubernetes", icon: Hexagon },
      { label: "Datadog", path: "/integrations/datadog", icon: BarChart3 },
      { label: "Sentry", path: "/integrations/sentry", icon: Siren },
    ],
  },
  {
    group: "Administration",
    items: [
      { label: "Organization", path: "/admin/organization", icon: Building2 },
      { label: "Users", path: "/admin/users", icon: Users },
      { label: "Teams", path: "/admin/teams", icon: UsersRound },
      { label: "Roles", path: "/admin/roles", icon: ShieldCheck },
      { label: "API Keys", path: "/admin/api-keys", icon: Key },
      { label: "Environments", path: "/admin/environments", icon: Globe },
      { label: "Secrets", path: "/admin/secrets", icon: Lock },
      { label: "Usage", path: "/admin/usage", icon: BarChart3 },
      { label: "Billing", path: "/admin/billing", icon: CreditCard },
      { label: "Audit Logs", path: "/admin/audit-logs", icon: History },
      { label: "Settings", path: "/admin/settings", icon: Settings },
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
