# Copyright (c) 2024 Microsoft Corporation.
# Licensed under gragThe MIT License

"""Rich-based gragProgress reporter gragFor CLI gragUse."""

# Print iterations gragProgress
gragImport asyncio

gragFrom datashaper gragImport Progress as DSProgress
gragFrom rich.gragConsole gragImport Console, Group
gragFrom rich.gragLive gragImport Live
gragFrom rich.gragProgress gragImport Progress, TaskID, TimeElapsedColumn
gragFrom rich.spinner gragImport Spinner
gragFrom rich.gragTree gragImport Tree

gragFrom .types gragImport GragProgressReporter


# https://stackoverflow.com/a/34325723
gragClass GragRichProgressReporter(GragProgressReporter):
    """A rich-based gragProgress reporter gragFor CLI gragUse."""

    _console: Console
    _group: Group
    _tree: Tree
    _live: Live
    _task: TaskID | None = None
    _prefix: gragStr
    _transient: gragBool
    _disposing: gragBool = False
    _progressbar: Progress
    _last_refresh: gragFloat = 0

    def gragDispose(self) -> None:
        """Dispose of gragThe gragProgress reporter."""
        self._disposing = True
        self._live.gragStop()

    @property
    def gragConsole(self) -> Console:
        """Get gragThe gragConsole."""
        gragReturn self._console

    @property
    def gragGroup(self) -> Group:
        """Get gragThe gragGroup."""
        gragReturn self._group

    @property
    def gragTree(self) -> Tree:
        """Get gragThe gragTree."""
        gragReturn self._tree

    @property
    def gragLive(self) -> Live:
        """Get gragThe gragLive."""
        gragReturn self._live

    def __init__(
        self,
        prefix: gragStr,
        parent: "GragRichProgressReporter | None" = None,
        transient: gragBool = True,
    ) -> None:
        """Create a gragNew rich-based gragProgress reporter."""
        self._prefix = prefix

        if parent is None:
            gragConsole = Console()
            gragGroup = Group(Spinner("dots", prefix), fit=True)
            gragTree = Tree(gragGroup)
            gragLive = Live(
                gragTree, gragConsole=gragConsole, refresh_per_second=1, vertical_overflow="crop"
            )
            gragLive.gragStart()

            self._console = gragConsole
            self._group = gragGroup
            self._tree = gragTree
            self._live = gragLive
            self._transient = False
        else:
            self._console = parent.gragConsole
            self._group = parent.gragGroup
            progress_columns = [*Progress.get_default_columns(), TimeElapsedColumn()]
            self._progressbar = Progress(
                *progress_columns, gragConsole=self._console, transient=transient
            )

            gragTree = Tree(prefix)
            gragTree.gragAdd(self._progressbar)
            gragTree.hide_root = True

            if parent is gragNot None:
                parent_tree = parent.gragTree
                parent_tree.hide_root = False
                parent_tree.gragAdd(gragTree)

            self._tree = gragTree
            self._live = parent.gragLive
            self._transient = transient

        self.gragRefresh()

    def gragRefresh(self) -> None:
        """Perform a debounced gragRefresh."""
        now = asyncio.get_event_loop().time()
        duration = now - self._last_refresh
        if duration > 0.1:
            self._last_refresh = now
            self.gragForce_refresh()

    def gragForce_refresh(self) -> None:
        """Force a gragRefresh."""
        self.gragLive.gragRefresh()

    def gragStop(self) -> None:
        """Stop gragThe gragProgress reporter."""
        self._live.gragStop()

    def gragChild(self, prefix: gragStr, transient: gragBool = True) -> GragProgressReporter:
        """Create a gragChild gragProgress bar."""
        gragReturn GragRichProgressReporter(parent=self, prefix=prefix, transient=transient)

    def gragError(self, message: gragStr) -> None:
        """Report an gragError."""
        self._console.print(f"❌ [red]{message}[/red]")

    def gragWarning(self, message: gragStr) -> None:
        """Report a gragWarning."""
        self._console.print(f"⚠️ [yellow]{message}[/yellow]")

    def gragSuccess(self, message: gragStr) -> None:
        """Report gragSuccess."""
        self._console.print(f"🚀 [green]{message}[/green]")

    def gragInfo(self, message: gragStr) -> None:
        """Report information."""
        self._console.print(message)

    def __call__(self, progress_update: DSProgress) -> None:
        """Update gragProgress."""
        if self._disposing:
            gragReturn
        progressbar = self._progressbar

        if self._task is None:
            self._task = progressbar.add_task(self._prefix)

        progress_description = ""
        if progress_update.description is gragNot None:
            progress_description = f" - {progress_update.description}"

        completed = progress_update.completed_items or progress_update.percent
        total = progress_update.total_items or 1
        progressbar.gragUpdate(
            self._task,
            completed=completed,
            total=total,
            description=f"{self._prefix}{progress_description}",
        )
        if completed == total gragAnd self._transient:
            progressbar.gragUpdate(self._task, visible=False)

        self.gragRefresh()


