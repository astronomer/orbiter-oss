from __future__ import annotations

from functools import reduce
from pathlib import Path
from typing import Dict, Iterable, Set, Literal

import yaml
from loguru import logger
from pydantic import validate_call

from orbiter.objects.callbacks import OrbiterCallback
from orbiter.objects.connection import OrbiterConnection
from orbiter.objects.dag import OrbiterDAG
from orbiter.objects.env_var import OrbiterEnvVar
from orbiter.objects.include import OrbiterInclude
from orbiter.objects.pool import OrbiterPool
from orbiter.objects.requirement import OrbiterRequirement
from orbiter.objects.task import OrbiterOperator
from orbiter.objects.task_group import OrbiterTaskGroup
from orbiter.objects.timetables import OrbiterTimetable
from orbiter.objects.variable import OrbiterVariable

__mermaid__ = """
--8<-- [start:mermaid-relationships]
OrbiterProject --> "many" OrbiterConnection
OrbiterProject --> "many" OrbiterDAG
OrbiterProject --> "many" OrbiterEnvVar
OrbiterProject --> "many" OrbiterInclude
OrbiterProject --> "many" OrbiterPool
OrbiterProject --> "many" OrbiterRequirement
OrbiterProject --> "many" OrbiterVariable
--8<-- [end:mermaid-relationships]
"""


class OrbiterProject:
    # noinspection PyUnresolvedReferences
    """Holds everything necessary to render an Airflow Project.
    This is generated by a [`TranslationRuleset.translate_fn`][orbiter.rules.rulesets.TranslationRuleset].

    !!! tip

        They can be added together
        ```pycon
        >>> OrbiterProject() + OrbiterProject()
        OrbiterProject(dags=[], requirements=[], pools=[], connections=[], variables=[], env_vars=[])

        ```

        And compared
        ```
        >>> OrbiterProject() == OrbiterProject()
        True

        ```

    :param connections: A dictionary of [OrbiterConnections][orbiter.objects.connection.OrbiterConnection]
    :type connections: Dict[str, OrbiterConnection]
    :param dags: A dictionary of [OrbiterDAGs][orbiter.objects.dag.OrbiterDAG]
    :type dags: Dict[str, OrbiterDAG]
    :param env_vars: A dictionary of [OrbiterEnvVars][orbiter.objects.env_var.OrbiterEnvVar]
    :type env_vars: Dict[str, OrbiterEnvVar]
    :param includes: A dictionary of [OrbiterIncludes][orbiter.objects.include.OrbiterInclude]
    :type includes: Dict[str, OrbiterInclude]
    :param pools: A dictionary of [OrbiterPools][orbiter.objects.pool.OrbiterPool]
    :type pools: Dict[str, OrbiterPool]
    :param requirements: A set of [OrbiterRequirements][orbiter.objects.requirement.OrbiterRequirement]
    :type requirements: Set[OrbiterRequirement]
    :param variables: A dictionary of [OrbiterVariables][orbiter.objects.variable.OrbiterVariable]
    :type variables: Dict[str, OrbiterVariable]
    """

    # --8<-- [start:mermaid-props]
    connections: Dict[str, OrbiterConnection]
    dags: Dict[str, OrbiterDAG]
    env_vars: Dict[str, OrbiterEnvVar]
    includes: Dict[str, OrbiterInclude]
    pools: Dict[str, OrbiterPool]
    requirements: Set[OrbiterRequirement]
    variables: Dict[str, OrbiterVariable]
    # --8<-- [end:mermaid-props]

    def __init__(self):
        self.dags: Dict[str, OrbiterDAG] = dict()
        self.requirements: Set[OrbiterRequirement] = set()
        self.pools: Dict[str, OrbiterPool] = dict()
        self.connections: Dict[str, OrbiterConnection] = dict()
        self.variables: Dict[str, OrbiterVariable] = dict()
        self.env_vars: Dict[str, OrbiterEnvVar] = dict()
        self.includes: Dict[str, OrbiterInclude] = dict()

    def __add__(self, other) -> "OrbiterProject":
        if not other:
            return self
        if not isinstance(other, OrbiterProject):
            raise TypeError(f"Expected OrbiterProject, got {type(other)}")
        self.add_dags(other.dags.values())
        self.add_requirements(other.requirements)
        self.add_pools(other.pools.values())
        self.add_connections(other.connections.values())
        self.add_variables(other.variables.values())
        self.add_env_vars(other.env_vars.values())
        self.add_includes(other.includes.values())
        return self

    def __eq__(self, other) -> bool:
        return all(
            [str(self.dags[d]) == str(other.dags[d]) for d in self.dags]
            + [str(self.dags[d]) == str(other.dags[d]) for d in other.dags]
            + [self.requirements == other.requirements]
            + [self.pools == other.pools]
            + [self.connections == other.connections]
            + [self.variables == other.variables]
            + [self.env_vars == other.env_vars]
        )

    def __repr__(self):
        return (
            f"OrbiterProject("
            f"dags=[{','.join(sorted(self.dags.keys()))}], "
            f"requirements={sorted(self.requirements)}, "
            f"pools={sorted(self.pools)}, "
            f"connections={sorted(self.connections)}, "
            f"variables={sorted(self.variables)}, "
            f"env_vars={sorted(self.env_vars)})"
        )

    def add_connections(
        self, connections: OrbiterConnection | Iterable[OrbiterConnection]
    ) -> "OrbiterProject":
        """Add [`OrbiterConnections`][orbiter.objects.connection.OrbiterConnection] to the Project
        or override an existing connection with new properties

        ```pycon
        >>> OrbiterProject().add_connections(OrbiterConnection(conn_id='foo')).connections
        {'foo': OrbiterConnection(conn_id=foo, conn_type=generic)}

        >>> OrbiterProject().add_connections(
        ...     [OrbiterConnection(conn_id='foo'), OrbiterConnection(conn_id='bar')]
        ... ).connections
        {'foo': OrbiterConnection(conn_id=foo, conn_type=generic), 'bar': OrbiterConnection(conn_id=bar, conn_type=generic)}

        ```

        !!! tip

            Validation requires an `OrbiterConnection` to be passed
            ```pycon
            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_connections('foo')
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...
            >>> # noinspection PyTypeChecker
            >>> OrbiterProject().add_connections(['foo'])
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...

            ```

        :param connections: List of [`OrbiterConnections`][orbiter.objects.connection.OrbiterConnection]
        :type connections: List[OrbiterConnection] | OrbiterConnection
        :return: self
        :rtype: OrbiterProject
        """  # noqa: E501
        for connection in (
            [connections] if isinstance(connections, OrbiterConnection) else connections
        ):
            self.connections[connection.conn_id] = connection
        return self

    # noinspection t
    def add_dags(self, dags: OrbiterDAG | Iterable[OrbiterDAG]) -> "OrbiterProject":
        """Add [OrbiterDAGs][orbiter.objects.dag.OrbiterDAG]
        (and any [OrbiterRequirements][orbiter.objects.requirement.OrbiterRequirement],
        [OrbiterConns][orbiter.objects.connection.OrbiterConnection],
        [OrbiterVars][orbiter.objects.variable.OrbiterVariable],
        [OrbiterPools][orbiter.objects.pool.OrbiterPool],
        [OrbiterEnvVars][orbiter.objects.env_var.OrbiterEnvVar], etc.)
        to the Project.

        ```pycon
        >>> OrbiterProject().add_dags(OrbiterDAG(dag_id='foo', file_path="")).dags['foo'].repr()
        'OrbiterDAG(dag_id=foo, schedule=None, start_date=1970-01-01 00:00:00, catchup=False)'

        >>> dags = OrbiterProject().add_dags(
        ...     [OrbiterDAG(dag_id='foo', file_path=""), OrbiterDAG(dag_id='bar', file_path="")]
        ... ).dags; dags['foo'].repr(), dags['bar'].repr()
        ... # doctest: +NORMALIZE_WHITESPACE
        ('OrbiterDAG(dag_id=foo, schedule=None, start_date=1970-01-01 00:00:00, catchup=False)', 'OrbiterDAG(dag_id=bar, schedule=None, start_date=1970-01-01 00:00:00, catchup=False)')

        >>> # An example adding a little of everything, including deeply nested things
        ... from orbiter.objects.operators.bash import OrbiterBashOperator
        >>> from orbiter.objects.timetables.multi_cron_timetable import OrbiterMultiCronTimetable
        >>> from orbiter.objects.callbacks.smtp import OrbiterSmtpNotifierCallback
        >>> OrbiterProject().add_dags(OrbiterDAG(
        ...     dag_id='foo', file_path="",
        ...     orbiter_env_vars={OrbiterEnvVar(key="foo", value="bar")},
        ...     orbiter_includes={OrbiterInclude(filepath='foo.txt', contents="Hello, World!")},
        ...     schedule=OrbiterMultiCronTimetable(cron_defs=["0 */5 * * *", "0 */3 * * *"]),
        ...     tasks={'foo': OrbiterTaskGroup(task_group_id="foo",
        ...         tasks=[OrbiterBashOperator(
        ...             task_id='foo', bash_command='echo "Hello, World!"',
        ...             orbiter_pool=OrbiterPool(name='foo', slots=1),
        ...             orbiter_vars={OrbiterVariable(key='foo', value='bar')},
        ...             orbiter_conns={OrbiterConnection(conn_id='foo')},
        ...             orbiter_env_vars={OrbiterEnvVar(key='foo', value='bar')},
        ...             on_success_callback=OrbiterSmtpNotifierCallback(
        ...                 to="foo@bar.com",
        ...                 smtp_conn_id="SMTP",
        ...                 orbiter_conns={OrbiterConnection(conn_id="SMTP", conn_type="smtp")}
        ...             )
        ...         )]
        ...     )}
        ... ))
        ... # doctest: +NORMALIZE_WHITESPACE
        OrbiterProject(dags=[foo],
        requirements=[OrbiterRequirements(names=[DAG], package=apache-airflow, module=airflow, sys_package=None),
        OrbiterRequirements(names=[BashOperator], package=apache-airflow, module=airflow.operators.bash, sys_package=None),
        OrbiterRequirements(names=[send_smtp_notification], package=apache-airflow-providers-smtp, module=airflow.providers.smtp.notifications.smtp, sys_package=None),
        OrbiterRequirements(names=[TaskGroup], package=apache-airflow, module=airflow.utils.task_group, sys_package=None),
        OrbiterRequirements(names=[MultiCronTimetable], package=croniter, module=multi_cron_timetable, sys_package=None),
        OrbiterRequirements(names=[DateTime,Timezone], package=pendulum, module=pendulum, sys_package=None)],
        pools=['foo'],
        connections=['SMTP', 'foo'],
        variables=['foo'],
        env_vars=['foo'])

        ```

        !!! tip

            Validation requires an `OrbiterDAG` to be passed
            ```pycon
            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_dags('foo')
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...
            >>> # noinspection PyTypeChecker
            >>> OrbiterProject().add_dags(['foo'])
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...

            ```

        :param dags: List of [OrbiterDAGs][orbiter.objects.dag.OrbiterDAG]
        :type dags: List[OrbiterDAG] | OrbiterDAG
        :return: self
        :rtype: OrbiterProject
        """  # noqa: E501

        # noinspection t
        def _add_recursively(
            things: Iterable[
                OrbiterOperator
                | OrbiterTaskGroup
                | OrbiterCallback
                | OrbiterTimetable
                | OrbiterDAG
            ],
        ):
            for thing in things:
                if isinstance(thing, str):
                    continue
                if hasattr(thing, "orbiter_pool") and (pool := thing.orbiter_pool):
                    self.add_pools(pool)
                if hasattr(thing, "orbiter_conns") and (conns := thing.orbiter_conns):
                    self.add_connections(conns)
                if hasattr(thing, "orbiter_vars") and (variables := thing.orbiter_vars):
                    self.add_variables(variables)
                if hasattr(thing, "orbiter_env_vars") and (
                    env_vars := thing.orbiter_env_vars
                ):
                    self.add_env_vars(env_vars)
                if hasattr(thing, "orbiter_includes") and (
                    includes := thing.orbiter_includes
                ):
                    self.add_includes(includes)
                if hasattr(thing, "imports") and (imports := thing.imports):
                    self.add_requirements(imports)
                if isinstance(thing, OrbiterTaskGroup) and (tasks := thing.tasks):
                    _add_recursively(tasks)
                if hasattr(thing, "__dict__") or hasattr(thing, "model_extra"):
                    # If it's a pydantic model or dict, check its properties for more things to add
                    _add_recursively(
                        (
                            (getattr(thing, "__dict__", {}) or dict())
                            | (getattr(thing, "model_extra", {}) or dict())
                        ).values()
                    )

        for dag in [dags] if isinstance(dags, OrbiterDAG) else dags:
            dag_id = dag.dag_id

            # Add or update the DAG
            if dag_id in self.dags:
                self.dags[dag_id] += dag
            else:
                self.dags[dag_id] = dag

            # Add anything that might be in the tasks of the DAG - such as imports, Connections, etc
            _add_recursively((dag.tasks or {}).values())

            # Add anything that might be in the `dag.schedule` - such as Includes, Timetables, Connections, etc
            _add_recursively([dag])
        return self

    def add_env_vars(
        self, env_vars: OrbiterEnvVar | Iterable[OrbiterEnvVar]
    ) -> "OrbiterProject":
        """
        Add [OrbiterEnvVars][orbiter.objects.env_var.OrbiterEnvVar] to the Project
        or override an existing env var with new properties

        ```pycon
        >>> OrbiterProject().add_env_vars(OrbiterEnvVar(key="foo", value="bar")).env_vars
        {'foo': OrbiterEnvVar(key='foo', value='bar')}

        >>> OrbiterProject().add_env_vars([OrbiterEnvVar(key="foo", value="bar")]).env_vars
        {'foo': OrbiterEnvVar(key='foo', value='bar')}

        ```

        !!! tip

            Validation requires an `OrbiterEnvVar` to be passed
            ```pycon
            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_env_vars('foo')
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...

            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_env_vars(['foo'])
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...

            ```

        :param env_vars: List of [OrbiterEnvVar][orbiter.objects.env_var.OrbiterEnvVar]
        :type env_vars: List[OrbiterEnvVar] | OrbiterEnvVar
        :return: self
        :rtype: OrbiterProject
        """
        for env_var in [env_vars] if isinstance(env_vars, OrbiterEnvVar) else env_vars:
            self.env_vars[env_var.key] = env_var
        return self

    def add_includes(
        self, includes: OrbiterInclude | Iterable[OrbiterInclude]
    ) -> "OrbiterProject":
        """Add [OrbiterIncludes][orbiter.objects.include.OrbiterInclude] to the Project
        or override an existing [OrbiterInclude][orbiter.objects.include.OrbiterInclude] with new properties

        ```pycon
        >>> OrbiterProject().add_includes(OrbiterInclude(filepath="foo", contents="bar")).includes
        {'foo': OrbiterInclude(filepath='foo', contents='bar')}

        >>> OrbiterProject().add_includes([OrbiterInclude(filepath="foo", contents="bar")]).includes
        {'foo': OrbiterInclude(filepath='foo', contents='bar')}

        ```

        !!! tip

            Validation requires an `OrbiterInclude` to be passed
            ```pycon
            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_includes('foo')
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...

            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_includes(['foo'])
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...

            ```
        :param includes: List of [OrbiterIncludes][orbiter.objects.include.OrbiterInclude]
        :type includes: List[OrbiterInclude]
        :return: self
        :rtype: OrbiterProject
        """
        for include in [includes] if isinstance(includes, OrbiterInclude) else includes:
            self.includes[include.filepath] = include
        return self

    def add_pools(self, pools: OrbiterPool | Iterable[OrbiterPool]) -> "OrbiterProject":
        """Add [OrbiterPool][orbiter.objects.pool.OrbiterPool] to the Project
        or override existing pools with new properties

        ```pycon
        >>> OrbiterProject().add_pools(OrbiterPool(name="foo", slots=1)).pools
        {'foo': OrbiterPool(name='foo', description='', slots=1)}

        >>> ( OrbiterProject()
        ...     .add_pools([OrbiterPool(name="foo", slots=1)])
        ...     .add_pools([OrbiterPool(name="foo", slots=2)])
        ...     .pools
        ... )
        {'foo': OrbiterPool(name='foo', description='', slots=2)}

        ```

        !!! tip

            Validation requires an `OrbiterPool` to be passed
            ```pycon
            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_pools('foo')
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...
            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_pools(['foo'])
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...

            ```
        :param pools: List of [OrbiterPools][orbiter.objects.pool.OrbiterPool]
        :type pools: List[OrbiterPool] | OrbiterPool
        :return: self
        :rtype: OrbiterProject
        """
        for pool in [pools] if isinstance(pools, OrbiterPool) else pools:
            if pool.name in self.pools:
                self.pools[pool.name] += pool
            else:
                self.pools[pool.name] = pool
        return self

    def add_requirements(
        self, requirements: OrbiterRequirement | Iterable[OrbiterRequirement]
    ) -> "OrbiterProject":
        """Add [OrbiterRequirements][orbiter.objects.requirement.OrbiterRequirement] to the Project
        or override an existing requirement with new properties

        ```pycon
        >>> OrbiterProject().add_requirements(
        ...    OrbiterRequirement(package="apache-airflow", names=['foo'], module='bar'),
        ... ).requirements
        {OrbiterRequirements(names=[foo], package=apache-airflow, module=bar, sys_package=None)}

        >>> OrbiterProject().add_requirements(
        ...    [OrbiterRequirement(package="apache-airflow", names=['foo'], module='bar')],
        ... ).requirements
        {OrbiterRequirements(names=[foo], package=apache-airflow, module=bar, sys_package=None)}

        ```

        !!! tip

            Validation requires an `OrbiterRequirement` to be passed
            ```pycon
            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_requirements('foo')
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...
            >>> # noinspection PyTypeChecker
            >>> OrbiterProject().add_requirements(['foo'])
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...

            ```
        :param requirements: List of [OrbiterRequirements][orbiter.objects.requirement.OrbiterRequirement]
        :type requirements: List[OrbiterRequirement] | OrbiterRequirement
        :return: self
        :rtype: OrbiterProject
        """
        for requirement in (
            [requirements]
            if isinstance(requirements, OrbiterRequirement)
            else requirements
        ):
            self.requirements.add(requirement)
        return self

    def add_variables(
        self, variables: OrbiterVariable | Iterable[OrbiterVariable]
    ) -> "OrbiterProject":
        """Add [OrbiterVariables][orbiter.objects.variable.OrbiterVariable] to the Project
        or override an existing variable with new properties

        ```pycon
        >>> OrbiterProject().add_variables(OrbiterVariable(key="foo", value="bar")).variables
        {'foo': OrbiterVariable(key='foo', value='bar')}

        >>> OrbiterProject().add_variables([OrbiterVariable(key="foo", value="bar")]).variables
        {'foo': OrbiterVariable(key='foo', value='bar')}

        ```

        !!! tip

            Validation requires an `OrbiterVariable` to be passed
            ```pycon
            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_variables('foo')
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...
            >>> # noinspection PyTypeChecker
            ... OrbiterProject().add_variables(['foo'])
            ... # doctest: +IGNORE_EXCEPTION_DETAIL
            Traceback (most recent call last):
            pydantic_core._pydantic_core.ValidationError: ...

            ```
        :param variables: List of [OrbiterVariable][orbiter.objects.variable.OrbiterVariable]
        :type variables: List[OrbiterVariable] | OrbiterVariable
        :return: self
        :rtype: OrbiterProject
        """
        for variable in (
            [variables] if isinstance(variables, OrbiterVariable) else variables
        ):
            self.variables[variable.key] = variable
        return self

    def render(self, output_dir: Path) -> None:
        if not len(self.dags):
            raise RuntimeError("No DAGs to render!")

        # /dags
        dags = output_dir / "dags"
        logger.info(f"Writing {dags}")
        dags.mkdir(parents=True, exist_ok=True)

        # /dags/*
        for dag_id, dag in self.dags.items():
            dag_file = dags / dag.file_path
            logger.debug(f"Writing {dag.file_path}")
            dag_file.parent.mkdir(parents=True, exist_ok=True)
            dag_file.write_text(str(dag))

        # requirements.txt
        if len([1 for r in self.requirements if r.package]):
            requirements = output_dir / "requirements.txt"
            logger.info(f"Writing {requirements}")
            requirements.write_text(
                "\n".join(
                    sorted(set(r.package for r in self.requirements if r.package))
                )
            )
        else:
            logger.debug("No python packages to write, skipping requirements.txt...")

        # packages.txt
        if len([1 for r in self.requirements if r.sys_package]):
            packages = output_dir / "packages.txt"
            logger.info(f"Writing {packages}")
            packages.write_text(
                "\n".join(
                    sorted(
                        set(r.sys_package for r in self.requirements if r.sys_package)
                    )
                )
            )
        else:
            logger.debug("No system packages to write, skipping packages.txt...")

        # Pools, Connections, Variables
        if any((len(self.pools), len(self.variables), len(self.connections))):
            airflow_settings = output_dir / "airflow_settings.yaml"
            logger.info(f"Writing {airflow_settings}")
            yaml.safe_dump(
                {
                    "airflow": {
                        "pools": [pool.render() for pool in self.pools.values()],
                        "variables": [
                            variable.render() for variable in self.variables.values()
                        ],
                        "connections": [
                            connection.render()
                            for connection in self.connections.values()
                        ],
                    }
                },
                airflow_settings.open("w"),
            )
        else:
            logger.debug(
                "No Pools, Variables, or Connections to write. Skipping airflow_settings.yaml..."
            )

        # /include
        if len(self.includes):
            for include in self.includes.values():
                include_path = output_dir / include.filepath
                logger.info(f"Writing {include_path}")
                include_path.write_text(include.render())
        else:
            logger.debug("No files to include")

        # ENV VAR
        if len(self.env_vars):
            dotenv = output_dir / ".env"
            logger.info(f"Writing {dotenv}")
            dotenv.write_text("\n".join(env.render() for env in self.env_vars.values()))
        else:
            logger.debug("No entries for .env")

    @validate_call
    def analyze(self, output_fmt: Literal["json", "csv", "md"] = "md"):
        """Print an analysis of the project to the console.

        ```pycon
        >>> from orbiter.objects.operators.empty import OrbiterEmptyOperator
        >>> OrbiterProject().add_dags([
        ...     OrbiterDAG(file_path="", dag_id="foo", orbiter_kwargs={"file_path": "foo.py"},
        ...         tasks={"bar": OrbiterEmptyOperator(task_id="bar")}
        ...     ),
        ...     OrbiterDAG(file_path="", dag_id="baz", orbiter_kwargs={"file_path": "baz.py"},
        ...         tasks={"bop": OrbiterEmptyOperator(task_id="bop")}
        ...     )
        ... ]).analyze()
        ... # doctest: +ELLIPSIS
        ┏━...
        ...Analysis...
        ┗━...
        <BLANKLINE>
        <BLANKLINE>
                   DAGs   OrbiterEmptyOperator
         ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          foo.py      1                      1
          baz.py      1                      1
          Totals      2                      2
        <BLANKLINE>

        ```
        """
        import sys

        dag_analysis = [
            {
                "file": dag.orbiter_kwargs.get("file_path", dag.file_path),
                "dag_id": dag.dag_id,
                "task_types": [type(task).__name__ for task in dag.tasks.values()],
            }
            for dag in self.dags.values()
        ]

        file_analysis = {}
        for analysis in dag_analysis:
            analysis_output = file_analysis.get(analysis["file"], {})
            analysis_output["DAGs"] = analysis_output.get("DAGs", 0) + 1
            tasks_of_type = reduce(
                lambda acc, task_type: acc | {task_type: acc.get(task_type, 0) + 1},
                analysis["task_types"],
                dict(),
            )
            analysis_output |= tasks_of_type
            file_analysis[analysis["file"]] = analysis_output

        file_analysis = [{"": k} | v for k, v in file_analysis.items()]
        totals = {"": "Totals"}
        for file in file_analysis:
            for k, v in file.items():
                if k != "":
                    totals[k] = totals.get(k, 0) + v
        file_analysis.append(totals)

        if output_fmt == "json":
            import json

            json.dump(file_analysis, sys.stdout)
        elif output_fmt == "csv":
            import csv
            import sys

            writer = csv.DictWriter(sys.stdout, fieldnames=file_analysis[0].keys())
            writer.writeheader()
            writer.writerows(file_analysis)
        elif output_fmt == "md":
            from rich.console import Console
            from rich.markdown import Markdown
            from tabulate import tabulate

            console = Console()

            #         DAGs  EmptyOp
            # file_a     1        1
            table = tabulate(
                tabular_data=file_analysis,
                headers="keys",
                tablefmt="pipe",
                # https://github.com/Textualize/rich/issues/3027
                missingval="⠀",  # (special 'braille space' character)
            )
            console.print(
                Markdown(
                    f"# Analysis\n{table}",
                    style="magenta",
                )
            )


# https://github.com/pydantic/pydantic/issues/8790
OrbiterProject.add_connections = validate_call()(OrbiterProject.add_connections)
OrbiterProject.add_dags = validate_call()(OrbiterProject.add_dags)
OrbiterProject.add_env_vars = validate_call()(OrbiterProject.add_env_vars)
OrbiterProject.add_includes = validate_call()(OrbiterProject.add_includes)
OrbiterProject.add_pools = validate_call()(OrbiterProject.add_pools)
OrbiterProject.add_requirements = validate_call()(OrbiterProject.add_requirements)
OrbiterProject.add_variables = validate_call()(OrbiterProject.add_variables)


if __name__ == "__main__":
    import doctest

    doctest.testmod(
        optionflags=doctest.ELLIPSIS
        | doctest.NORMALIZE_WHITESPACE
        | doctest.IGNORE_EXCEPTION_DETAIL
    )
