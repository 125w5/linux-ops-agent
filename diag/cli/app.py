from __future__ import annotations

import argparse
from pathlib import Path

from diag.cli.output import print_summary, stage
from diag.planner.intent import infer_task
from diag.permissions.mode import parse_permission_mode
from diag.runtime.agent_loop import AgentLoop
from diag.storage.database import HistoryStore
from diag.tooldocs.doc_store import ToolDocStore
from diag.tooldocs.help_collector import collect_help
from diag.tooldocs.man_collector import collect_man
from diag.tooldocs.profile_builder import build_profile, suggest_for_scene
from diag.utils.paths import database_path


def run_diagnose(args: argparse.Namespace) -> int:
    user_input = args.input or args.task or ""
    task_type = infer_task(user_input, args.task)
    mode = parse_permission_mode(args.mode, demo=args.demo)
    outcome = AgentLoop(timeout_seconds=args.timeout).run(
        user_input=user_input,
        target=args.target,
        task_type=task_type,
        permission_mode=mode,
        service=args.service,
        stage=stage,
    )
    print_summary(outcome)
    return 0


def run_chat(_: argparse.Namespace) -> int:
    print("OpsPilot-Linux chat. Type 'exit' to quit.")
    while True:
        try:
            text = input("diag> ").strip()
        except EOFError:
            break
        if text.lower() in {"exit", "quit"}:
            break
        task = infer_task(text, None)
        print(f"Intent: {task}. Run: python -m diag diagnose --task {task} --input \"{text}\"")
    return 0


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="diag", description="Linux operations diagnosis assistant")
    subparsers = parser.add_subparsers(dest="command", required=True)

    diagnose = subparsers.add_parser("diagnose", help="Run a diagnosis workflow")
    diagnose.add_argument("--target", default="localhost")
    diagnose.add_argument("--task", choices=["disk", "cpu", "service", "ssh-failure", "ssh"], default=None)
    diagnose.add_argument("--input", default="")
    diagnose.add_argument("--service", default="nginx")
    diagnose.add_argument("--mode", choices=["demo", "readonly", "confirm", "fault-lab", "blocked"], default=None)
    diagnose.add_argument("--timeout", type=int, default=20)
    diagnose.add_argument("--demo", action="store_true", help="Use built-in demo command output")
    diagnose.set_defaults(func=run_diagnose)

    chat = subparsers.add_parser("chat", help="Start a tiny intent-detection REPL")
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
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)
