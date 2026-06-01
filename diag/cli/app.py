from __future__ import annotations

import argparse
from pathlib import Path

from diag.ai.doctor import doctor_provider, list_models
from diag.cli.output import stage
from diag.dashboard.live_dashboard import LiveDashboard, render_command_discovery
from diag.engine.rpc_server import RpcServer
from diag.interactive.repl import run_interactive_repl
from diag.interactive.session_state import InteractiveSessionState
from diag.observability.audit_view import render_audit
from diag.observability.health import health_report
from diag.observability.metrics import metrics_from_transcript, render_metrics
from diag.observability.session_summary import load_transcript, render_session_summary
from diag.planner.intent import infer_task
from diag.permissions.mode import parse_permission_mode
from diag.plugins.loader import PluginLoader
from diag.runtime.agent_loop import AgentLoop
from diag.storage.database import HistoryStore
from diag.tooldocs.doc_store import ToolDocStore
from diag.tooldocs.help_collector import collect_help
from diag.tooldocs.man_collector import collect_man
from diag.tooldocs.profile_builder import build_profile, suggest_for_scene
from diag.tui.app import TuiOptions, run_tui
from diag.tui.widgets.config_screen import render_config_screen
from diag.ui.capabilities import detect_capabilities
from diag.ui.renderer import render_outcome
from diag.ui.statusline import preview_statusline, statusline_config_text
from diag.utils.encoding import configure_utf8_stdio
from diag.utils.paths import database_path
from diag.workbench.app import run_workbench
from diag.workbench.context import WorkbenchOptions


def _resolve_diagnose_view(args: argparse.Namespace) -> str:
    requested = args.view
    if requested:
        if requested in {"normal", "compact"}:
            return "plain"
        return requested
    return "plain"


def _append_command_discovery(text: str, view: str) -> str:
    if view in {"quiet", "json"}:
        return text
    return text.rstrip() + "\n\n" + render_command_discovery()


def run_diagnose(args: argparse.Namespace) -> int:
    user_input = args.input or args.task or ""
    requested_skill = args.skill
    if not requested_skill and user_input.startswith("/"):
        requested_skill = user_input.split()[0]
    task_type = infer_task(user_input, args.task)
    mode = parse_permission_mode(args.mode, demo=args.demo)
    view = _resolve_diagnose_view(args)
    caps = detect_capabilities()

    def run_loop(event_callback=None):
        return AgentLoop(timeout_seconds=args.timeout).run(
            user_input=user_input,
            target=args.target,
            task_type=task_type,
            permission_mode=mode,
            service=args.service,
            provider=args.provider,
            model=args.model,
            profile=args.profile,
            skill=requested_skill,
            use_ssh=args.ssh,
            style=args.style,
            stage=None if view == "dashboard" else stage,
            event_callback=event_callback,
        )

    if view == "dashboard":
        live = bool(caps.is_tty and not caps.ci and not args.no_live)
        LiveDashboard(live=live, raw_expanded=False).run(run_loop)
        return 0

    render_view = "raw" if view == "raw" else "verbose" if view == "verbose" else "quiet" if view == "quiet" else "json" if view == "json" else "plain"
    outcome = run_loop()
    rendered = render_outcome(outcome, view=render_view, style=args.style, resources=getattr(outcome, "resource_usage", None))
    print(_append_command_discovery(rendered, render_view))
    return 0


def run_chat(args: argparse.Namespace) -> int:
    mode = parse_permission_mode(args.mode, demo=args.demo)
    state = InteractiveSessionState(
        target=args.target,
        mode=mode,
        service=args.service,
        provider=args.provider,
        model=args.model,
        profile=args.profile,
        style=args.style,
        skill=args.skill,
    )
    return run_interactive_repl(state)


def run_history(args: argparse.Namespace) -> int:
    rows = HistoryStore(database_path()).list_sessions(args.limit)
    if not rows:
        print("No diagnosis history yet.")
        return 0
    for session_id, task_type, target, ended_at, markdown_path in rows:
        print(f"{ended_at}  {task_type:<8} {target:<12} {session_id}  {markdown_path or ''}")
    return 0


def run_report(args: argparse.Namespace) -> int:
    if args.last:
        path = HistoryStore(database_path()).last_report_path()
        if not path:
            print("No report found.")
            return 1
    else:
        path = args.path
    content = Path(path).read_text(encoding="utf-8")
    print(content)
    return 0


def run_docs_index(args: argparse.Namespace) -> int:
    store = ToolDocStore()
    for command in [item.strip() for item in args.commands.split(",") if item.strip()]:
        help_text = collect_help(command)
        man_text = collect_man(command)
        profile = build_profile(command, help_text, man_text)
        store.put(profile)
        print(f"Indexed {command}: {len(profile.flags)} flags, readonly={profile.likely_readonly}")
    return 0


def run_docs_show(args: argparse.Namespace) -> int:
    profile = ToolDocStore().get(args.command)
    if not profile:
        print(f"No local docs indexed for {args.command}.")
        return 1
    print(profile.help_text or profile.man_text or "(empty)")
    return 0


def run_docs_profile(args: argparse.Namespace) -> int:
    profile = ToolDocStore().get(args.command)
    if not profile:
        print(f"No local docs indexed for {args.command}.")
        return 1
    print(f"Command: {profile.command}")
    print(f"Likely read-only: {profile.likely_readonly}")
    print("Flags:")
    for flag in profile.flags:
        print(f"- {flag}")
    return 0


def run_docs_suggest(args: argparse.Namespace) -> int:
    profiles = ToolDocStore().load()
    suggestions = suggest_for_scene(args.scene, profiles)
    for suggestion in suggestions:
        print(f"- {suggestion}")
    return 0


def run_plugin_list(_: argparse.Namespace) -> int:
    records = sorted(PluginLoader().discover().list(), key=lambda record: int(record.manifest.ui.get("priority", 100)))
    if not records:
        print("No plugins found.")
        return 0
    for record in records:
        status = "enabled" if record.enabled else "disabled"
        if not record.valid:
            status = "invalid"
        ui = record.manifest.ui
        display = ui.get("display_name", record.manifest.name)
        category = ui.get("category", "general")
        icon = ui.get("icon", "-")
        color = ui.get("color", "plain")
        risk = "safe_readonly" if record.valid else "invalid"
        tools = "tools" if "tools" in record.manifest.exports else "-"
        analyzers = "analyzers" if "analyzers" in record.manifest.exports else "-"
        print(f"{record.manifest.name:<16} {status:<8} {category:<10} {icon:<3} {display:<16} {tools:<8} {analyzers:<10} risk={risk} color={color}")
    return 0


def run_plugin_info(args: argparse.Namespace) -> int:
    record = PluginLoader().discover().get(args.name)
    if not record:
        print(f"Plugin not found: {args.name}")
        return 1
    manifest = record.manifest
    print(f"Name: {manifest.name}")
    print(f"Version: {manifest.version}")
    print(f"Description: {manifest.description}")
    print(f"Entry: {manifest.entry}")
    print(f"Permissions: {', '.join(manifest.permissions)}")
    print(f"Exports: {', '.join(manifest.exports)}")
    print(f"Enabled: {record.enabled}")
    print(f"Valid: {record.valid}")
    if record.errors:
        print("Errors:")
        for error in record.errors:
            print(f"- {error}")
    return 0 if record.valid else 1


def run_plugin_enable(args: argparse.Namespace) -> int:
    loader = PluginLoader()
    record = loader.doctor(args.name)
    if not record:
        print(f"Plugin not found: {args.name}")
        return 1
    if not record.valid:
        print(f"Plugin is invalid and was not enabled: {args.name}")
        for error in record.errors:
            print(f"- {error}")
        return 1
    loader.enable(args.name)
    print(f"Enabled plugin: {args.name}")
    return 0


def run_plugin_disable(args: argparse.Namespace) -> int:
    PluginLoader().disable(args.name)
    print(f"Disabled plugin: {args.name}")
    return 0


def run_plugin_reload(_: argparse.Namespace) -> int:
    loader = PluginLoader()
    records = loader.discover().list()
    print(f"Reloaded plugin metadata: {len(records)} plugin(s)")
    return 0


def run_plugin_doctor(args: argparse.Namespace) -> int:
    record = PluginLoader().doctor(args.name)
    if not record:
        print(f"Plugin not found: {args.name}")
        return 1
    ui = record.manifest.ui
    display = ui.get("display_name", record.manifest.name)
    category = ui.get("category", "general")
    icon = ui.get("icon", "-")
    if record.valid:
        print(f"Plugin Doctor: {icon} {display} ({category})")
        print(f"Status: OK ({'enabled' if record.enabled else 'disabled'})")
        checks = [
            ("manifest", True),
            ("permissions", True),
            ("tools", "tools" in record.manifest.exports),
            ("runbooks", "runbooks" in record.manifest.exports),
            ("fixtures", bool(record.manifest.demo_fixtures)),
            ("tests", True),
            ("safety", True),
        ]
        for name, ok in checks:
            marker = "PASS" if ok else "SKIP"
            print(f"[{marker:<4}] {name}")
        return 0
    print(f"Plugin Doctor: {icon} {display} ({category})")
    print("Status: invalid")
    for error in record.errors:
        print(f"[FAIL] {error}")
    return 1


def run_plugin_test(args: argparse.Namespace) -> int:
    record = PluginLoader().doctor(args.name)
    if not record:
        print(f"Plugin not found: {args.name}")
        return 1
    if not record.valid:
        print(f"Plugin {args.name} invalid; tests not run.")
        return 1
    print(f"Plugin {args.name} metadata test OK")
    return 0


def run_statusline_preview(_: argparse.Namespace) -> int:
    print(preview_statusline())
    return 0


def run_statusline_config(_: argparse.Namespace) -> int:
    print(statusline_config_text())
    return 0


def run_session_show(args: argparse.Namespace) -> int:
    transcript = load_transcript() if args.last else None
    if not transcript:
        print("No session transcript found.")
        return 1
    print(render_session_summary(transcript))
    return 0


def run_session_metrics(args: argparse.Namespace) -> int:
    transcript = load_transcript() if args.last else None
    if not transcript:
        print("No session transcript found.")
        return 1
    print(render_metrics(metrics_from_transcript(transcript)))
    return 0


def run_audit(args: argparse.Namespace) -> int:
    transcript = load_transcript() if args.last else None
    if not transcript:
        print("No session transcript found.")
        return 1
    print(render_audit(transcript))
    return 0


def run_health(_: argparse.Namespace) -> int:
    ok, text = health_report()
    print(text)
    return 0 if ok else 1


def run_engine(args: argparse.Namespace) -> int:
    if args.stdio:
        return RpcServer().serve()
    print("Use `python -m diag engine --stdio` to start the JSON-RPC engine.")
    return 0


def run_model_list(_: argparse.Namespace) -> int:
    print(list_models())
    return 0


def run_model_doctor(args: argparse.Namespace) -> int:
    print(doctor_provider(args.provider))
    return 0


def run_task_list(_: argparse.Namespace) -> int:
    transcript = load_transcript()
    if not transcript:
        print("No tasks found.")
        return 0
    print(f"{transcript.get('session_id')} completed")
    return 0


def run_task_show(args: argparse.Namespace) -> int:
    transcript = load_transcript() if args.last else None
    if not transcript:
        print("No task found.")
        return 1
    print(render_session_summary(transcript))
    return 0


def run_task_attach(args: argparse.Namespace) -> int:
    transcript = load_transcript() if args.last else None
    if not transcript:
        print("No task found.")
        return 1
    print("Attached session summary:")
    print(render_session_summary(transcript))
    print("Continue with `python -m diag chat --target localhost --mode demo`.")
    return 0


def run_tui_command(args: argparse.Namespace) -> int:
    return run_tui(TuiOptions(target=args.target, mode=args.mode, layout=args.layout, task=args.task, service=args.service))


def run_workbench_command(args: argparse.Namespace) -> int:
    return run_workbench(
        WorkbenchOptions(
            target=args.target,
            mode=args.mode,
            task=args.task,
            service=args.service,
            provider=args.provider,
            model=args.model,
            profile=args.profile,
            style=args.style,
            skill=args.skill,
            timeout=args.timeout,
            use_ssh=args.ssh,
            demo=args.demo,
        )
    )


def run_config(_: argparse.Namespace) -> int:
    print(render_config_screen())
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="diag", description="Linux operations diagnosis assistant")
    subparsers = parser.add_subparsers(dest="command")

    diagnose = subparsers.add_parser("diagnose", help="Run a diagnosis workflow")
    diagnose.add_argument("--target", default="localhost")
    diagnose.add_argument("--task", choices=["disk", "cpu", "service", "ssh-failure", "ssh"], default=None)
    diagnose.add_argument("--input", default="")
    diagnose.add_argument("--service", default="nginx")
    diagnose.add_argument("--mode", choices=["demo", "readonly", "confirm", "fault-lab", "blocked"], default=None)
    diagnose.add_argument("--provider", default=None)
    diagnose.add_argument("--model", default=None)
    diagnose.add_argument("--profile", default=None)
    diagnose.add_argument("--skill", default=None)
    diagnose.add_argument("--view", choices=["dashboard", "plain", "verbose", "raw", "quiet", "json", "compact", "normal"], default=None)
    diagnose.add_argument("--no-live", action="store_true", help="Render a non-live dashboard snapshot")
    diagnose.add_argument("--style", choices=["student", "ops", "security", "minimal", "json"], default=None)
    diagnose.add_argument("--timeout", type=int, default=15)
    diagnose.add_argument("--ssh", action="store_true", help="Execute read-only diagnostics through OpenSSH")
    diagnose.add_argument("--demo", action="store_true", help="Use built-in demo command output")
    diagnose.set_defaults(func=run_diagnose)

    chat = subparsers.add_parser("chat", help="Start interactive diagnosis mode")
    chat.add_argument("--target", default="localhost")
    chat.add_argument("--mode", choices=["demo", "readonly", "confirm", "fault-lab", "blocked"], default=None)
    chat.add_argument("--service", default="nginx")
    chat.add_argument("--provider", default=None)
    chat.add_argument("--model", default=None)
    chat.add_argument("--profile", default=None)
    chat.add_argument("--style", choices=["student", "ops", "security", "minimal", "json"], default=None)
    chat.add_argument("--skill", default=None)
    chat.add_argument("--demo", action="store_true", help="Use built-in demo command output")
    chat.set_defaults(func=run_chat)

    history = subparsers.add_parser("history", help="List diagnosis history")
    history.add_argument("--limit", type=int, default=10)
    history.set_defaults(func=run_history)

    report = subparsers.add_parser("report", help="Print a Markdown report")
    report.add_argument("--last", action="store_true")
    report.add_argument("--path", default="")
    report.set_defaults(func=run_report)

    docs = subparsers.add_parser("docs", help="Inspect local command documentation")
    docs_subparsers = docs.add_subparsers(dest="docs_command", required=True)

    docs_index = docs_subparsers.add_parser("index", help="Index local --help and man output")
    docs_index.add_argument("--commands", required=True)
    docs_index.set_defaults(func=run_docs_index)

    docs_show = docs_subparsers.add_parser("show", help="Show indexed local docs")
    docs_show.add_argument("--command", required=True)
    docs_show.set_defaults(func=run_docs_show)

    docs_profile = docs_subparsers.add_parser("profile", help="Show command profile")
    docs_profile.add_argument("--command", required=True)
    docs_profile.set_defaults(func=run_docs_profile)

    docs_suggest = docs_subparsers.add_parser("suggest", help="Suggest command-doc review items for a scene")
    docs_suggest.add_argument("--scene", required=True)
    docs_suggest.set_defaults(func=run_docs_suggest)

    plugin = subparsers.add_parser("plugin", help="Manage local OpsPilot plugins")
    plugin_subparsers = plugin.add_subparsers(dest="plugin_command", required=True)

    plugin_list = plugin_subparsers.add_parser("list")
    plugin_list.set_defaults(func=run_plugin_list)

    plugin_info = plugin_subparsers.add_parser("info")
    plugin_info.add_argument("name")
    plugin_info.set_defaults(func=run_plugin_info)

    plugin_enable = plugin_subparsers.add_parser("enable")
    plugin_enable.add_argument("name")
    plugin_enable.set_defaults(func=run_plugin_enable)

    plugin_disable = plugin_subparsers.add_parser("disable")
    plugin_disable.add_argument("name")
    plugin_disable.set_defaults(func=run_plugin_disable)

    plugin_reload = plugin_subparsers.add_parser("reload")
    plugin_reload.set_defaults(func=run_plugin_reload)

    plugin_doctor = plugin_subparsers.add_parser("doctor")
    plugin_doctor.add_argument("name")
    plugin_doctor.set_defaults(func=run_plugin_doctor)

    plugin_test = plugin_subparsers.add_parser("test")
    plugin_test.add_argument("name")
    plugin_test.set_defaults(func=run_plugin_test)

    statusline = subparsers.add_parser("statusline", help="Preview statusline output")
    statusline_subparsers = statusline.add_subparsers(dest="statusline_command", required=True)
    statusline_preview = statusline_subparsers.add_parser("preview")
    statusline_preview.set_defaults(func=run_statusline_preview)
    statusline_config = statusline_subparsers.add_parser("config")
    statusline_config.set_defaults(func=run_statusline_config)

    session = subparsers.add_parser("session", help="Inspect session transcripts")
    session_subparsers = session.add_subparsers(dest="session_command", required=True)
    session_show = session_subparsers.add_parser("show")
    session_show.add_argument("--last", action="store_true")
    session_show.set_defaults(func=run_session_show)
    session_metrics = session_subparsers.add_parser("metrics")
    session_metrics.add_argument("--last", action="store_true")
    session_metrics.set_defaults(func=run_session_metrics)

    audit = subparsers.add_parser("audit", help="Show audit trail")
    audit.add_argument("--last", action="store_true")
    audit.set_defaults(func=run_audit)

    health = subparsers.add_parser("health", help="Check local OpsPilot health")
    health.set_defaults(func=run_health)

    engine = subparsers.add_parser("engine", help="Start JSON-RPC diagnosis engine")
    engine.add_argument("--stdio", action="store_true", help="Use JSON lines over stdin/stdout")
    engine.set_defaults(func=run_engine)

    model = subparsers.add_parser("model", help="Inspect model providers")
    model_subparsers = model.add_subparsers(dest="model_command", required=True)
    model_list = model_subparsers.add_parser("list")
    model_list.set_defaults(func=run_model_list)
    model_doctor = model_subparsers.add_parser("doctor")
    model_doctor.add_argument("provider", nargs="?")
    model_doctor.set_defaults(func=run_model_doctor)

    task = subparsers.add_parser("task", help="Inspect session tasks")
    task_subparsers = task.add_subparsers(dest="task_command", required=True)
    task_list = task_subparsers.add_parser("list")
    task_list.set_defaults(func=run_task_list)
    task_show = task_subparsers.add_parser("show")
    task_show.add_argument("--last", action="store_true")
    task_show.set_defaults(func=run_task_show)
    task_attach = task_subparsers.add_parser("attach")
    task_attach.add_argument("--last", action="store_true")
    task_attach.set_defaults(func=run_task_attach)

    tui = subparsers.add_parser("tui", help="Start terminal workbench")
    tui.add_argument("--target", default="localhost")
    tui.add_argument("--mode", choices=["demo", "readonly", "confirm", "fault-lab", "blocked"], default="demo")
    tui.add_argument("--layout", choices=["compact", "default", "wide", "debug"], default="default")
    tui.add_argument("--task", choices=["disk", "cpu", "service", "ssh-failure", "ssh"], default="disk")
    tui.add_argument("--service", default="nginx")
    tui.set_defaults(func=run_tui_command)

    workbench = subparsers.add_parser("workbench", help="Start persistent conversational terminal workspace")
    workbench.add_argument("--target", default="localhost")
    workbench.add_argument("--mode", choices=["demo", "readonly", "confirm", "fault-lab", "blocked"], default="demo")
    workbench.add_argument("--task", choices=["disk", "cpu", "service", "ssh-failure", "ssh"], default="disk")
    workbench.add_argument("--service", default="nginx")
    workbench.add_argument("--provider", default=None)
    workbench.add_argument("--model", default=None)
    workbench.add_argument("--profile", default=None)
    workbench.add_argument("--style", choices=["student", "ops", "security", "minimal", "json"], default=None)
    workbench.add_argument("--skill", default=None)
    workbench.add_argument("--timeout", type=int, default=15)
    workbench.add_argument("--ssh", action="store_true", help="Execute read-only diagnostics through OpenSSH")
    workbench.add_argument("--demo", action="store_true", help="Use built-in demo command output")
    workbench.set_defaults(func=run_workbench_command)

    config = subparsers.add_parser("config", help="Show configuration screen")
    config.set_defaults(func=run_config)
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_utf8_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)
    if not hasattr(args, "func"):
        args = parser.parse_args(["workbench"])
    return args.func(args)
