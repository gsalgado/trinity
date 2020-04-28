from abc import abstractmethod
import os
from typing import Optional

from asyncio_run_in_process import open_in_process
from asyncio_run_in_process.typing import SubprocessKwargs
from async_service import background_asyncio_service
from lahja import EndpointAPI


from trinity._utils.logging import child_process_logging, get_logger
from trinity._utils.profiling import profiler
from trinity.boot_info import BootInfo

from .component import BaseIsolatedComponent
from .event_bus import AsyncioEventBusService


logger = get_logger('trinity.extensibility.asyncio.AsyncioIsolatedComponent')


class AsyncioIsolatedComponent(BaseIsolatedComponent):

    def get_subprocess_kwargs(self) -> Optional[SubprocessKwargs]:
        # By default we want every child process its own process group leader as we don't want a
        # Ctrl-C in the terminal to send a SIGINT to each one of our process, as that is already
        # handled by open_in_process().
        start_new_session = True
        if os.getenv('TRINITY_SINGLE_PROCESS_GROUP') == "1":
            # This is needed because some of our integration tests rely on all processes being in
            # a single process group.
            start_new_session = False
        return {'start_new_session': start_new_session}

    async def run(self) -> None:
        proc_ctx = open_in_process(
            self._do_run,
            self._boot_info,
            subprocess_kwargs=self.get_subprocess_kwargs(),
        )
        try:
            async with proc_ctx as proc:
                await proc.wait_result_or_raise()
        finally:
            # Right now, when we shutdown trinity, all our components terminate with a 15
            # returncode (SIGTERM), but ideally they should terminate with a 2 (SIGINT). See the
            # comment below for why that is.
            logger.debug("%s terminated: returncode=%s", self, proc.returncode)

    async def _do_run(self, boot_info: BootInfo) -> None:
        with child_process_logging(boot_info):
            endpoint_name = self.get_endpoint_name()
            event_bus_service = AsyncioEventBusService(
                boot_info.trinity_config,
                endpoint_name,
            )
            async with background_asyncio_service(event_bus_service):
                event_bus = await event_bus_service.get_event_bus()

                try:
                    if boot_info.profile:
                        with profiler(f'profile_{self.get_endpoint_name()}'):
                            await self.do_run(boot_info, event_bus)
                    else:
                        # XXX: When open_in_process() injects a KeyboardInterrupt into us (via
                        # coro.throw()), we hang forever here, until open_in_process() times out
                        # and sends us a SIGTERM, at which point we exit without executing either
                        # the except or the finally blocks below.
                        # See https://github.com/ethereum/trinity/issues/1711 for more.
                        await self.do_run(boot_info, event_bus)
                except KeyboardInterrupt:
                    # Currently we never reach this code path, but when we fix the issue above it
                    # will be needed.
                    return
                finally:
                    # Once we start seeing this in the logs, we'll likely have figured the issue
                    # above.
                    logger.debug("%s: do_run() finished", self)

    @abstractmethod
    async def do_run(self, boot_info: BootInfo, event_bus: EndpointAPI) -> None:
        """
        Define the entry point of the component. Should be overwritten in subclasses.
        """
        ...
