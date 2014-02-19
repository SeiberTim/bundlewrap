from datetime import datetime

from ..concurrency import WorkerPool
from ..utils import LOG
from ..utils.cmdline import get_target_nodes
from ..utils.text import bold, green, red, yellow
from ..utils.text import mark_for_translation as _


def format_node_action_result(result):
    output = []
    output.append(_("{} ok").format(result.actions_ok))

    if result.actions_aborted:
        output.append(yellow(_("{} aborted").format(result.actions_aborted)))
    else:
        output.append(_("{} aborted").format(result.actions_aborted))

    if result.actions_failed:
        output.append(red(_("{} failed").format(result.actions_failed)))
    else:
        output.append(_("{} failed").format(result.actions_failed))

    return ", ".join(output)


def format_node_item_result(result):
    output = []
    output.append(("{} correct").format(result.correct))

    if result.fixed:
        output.append(green(_("{} fixed").format(result.fixed)))
    else:
        output.append(_("{} fixed").format(result.fixed))

    if result.aborted:
        output.append(yellow(_("{} aborted").format(result.aborted)))
    else:
        output.append(_("{} aborted").format(result.aborted))

    if result.unfixable:
        output.append(red(_("{} unfixable").format(result.unfixable)))
    else:
        output.append(_("{} unfixable").format(result.unfixable))

    if result.failed:
        output.append(red(_("{} failed").format(result.failed)))
    else:
        output.append(_("{} failed").format(result.failed))

    return ", ".join(output)


def bw_apply(repo, args):
    target_nodes = get_target_nodes(repo, args.target)

    repo.hooks.apply_start(
        repo,
        args.target,
        target_nodes,
        interactive=args.interactive,
    )

    start_time = datetime.now()

    worker_count = 1 if args.interactive else args.node_workers
    with WorkerPool(workers=worker_count) as worker_pool:
        results = {}
        while worker_pool.keep_running():
            msg = worker_pool.get_event()
            if msg['msg'] == 'REQUEST_WORK':
                if target_nodes:
                    node = target_nodes.pop()
                    node_start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    if args.interactive:
                        yield _("\n{}: run started at {}").format(
                            bold(node.name),
                            node_start_time,
                        )
                    else:
                        LOG.info(_("{}: run started at {}").format(
                            node.name,
                            node_start_time,
                        ))

                    worker_pool.start_task(
                        msg['wid'],
                        node.apply,
                        task_id=node.name,
                        kwargs={
                            'force': args.force,
                            'interactive': args.interactive,
                            'workers': args.item_workers,
                        },
                    )
                else:
                    worker_pool.quit(msg['wid'])
            elif msg['msg'] == 'FINISHED_WORK':
                node_name = msg['task_id']
                results[node_name] = msg['return_value']

                if args.interactive:
                    yield _("\n  {}: run completed after {}s\n").format(
                        bold(node_name),
                        results[node_name].duration.total_seconds(),
                    )
                    yield _("  items: ") + \
                        format_node_item_result(results[node_name])
                    yield _("  actions: ") + \
                        format_node_action_result(results[node_name]) + "\n"
                else:
                    LOG.info(_("{}: run completed after {}s").format(
                        node_name,
                        results[node_name].duration.total_seconds(),
                    ))
                    LOG.info(_("{}: item stats: {}").format(
                        node_name,
                        format_node_item_result(results[node_name]),
                    ))
                    LOG.info(_("{}: action stats: {}").format(
                        node_name,
                        format_node_action_result(results[node_name]),
                    ))

    repo.hooks.apply_end(
        repo,
        args.target,
        target_nodes,
        duration=datetime.now() - start_time,
    )
