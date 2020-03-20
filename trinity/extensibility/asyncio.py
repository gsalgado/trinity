from abc import abstractmethod
import asyncio
import signal
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
        # Note that this method currently only exist to facilitate testing.
        return None

    async def run(self) -> None:
        proc_ctx = open_in_process(
            self._do_run,
            self._boot_info,
            subprocess_kwargs=self.get_subprocess_kwargs(),
        )
        async with proc_ctx as proc:
            try:
                await proc.wait_result()
            except asyncio.CancelledError:
                logger.exception('Component %s exiting. Sending SIGINT to pid=%d', self, proc.pid)
                proc.send_signal(signal.SIGINT)
                try:
                    await asyncio.wait_for(proc.wait(), timeout=2)
                except asyncio.TimeoutError as exc:
                    logger.info(
                        'Component %s running in process pid=%d timed out '
                        'during shutdown. Sending SIGTERM and exiting: %s',
                        self,
                        proc.pid,
                        exc,
                    )
                    proc.send_signal(signal.SIGTERM)

    # XXX
    # This method never seems to return.
    # Interesting things to notice.
    # 1. After the SIGINT, both UPnPService2 and AsyncioEventBusService finish cleanly
    # 2. asyncio_run_in_process: got_SIGINT is set twice:
    #   2020-04-03 13:14:00,772  asyncio_run_in_process  <coroutine object AsyncioIsolatedComponent._do_run at 0x7f5497513a70> got SIGINT
    #   2020-04-03 13:14:00,835  asyncio_run_in_process  <coroutine object AsyncioIsolatedComponent._do_run at 0x7f5497513a70> got SIGINT
    # 3. After both services started by the component finish, the component seems to hang here,
    #    until we reach the timeout and the component-manager sends a SIGTERM
    # INFO  2020-04-03 13:14:00,841  Manager  <Manager[AsyncioEventBusService] flags=SrCFe>: finished
    # INFO  2020-04-03 13:14:02,832  AsyncioIsolatedComponent  Component <Component[Upnp]> running in process pid=11890 timed out during shutdown. Sending SIGTERM and exiting:
    @classmethod
    async def _do_run(cls, boot_info: BootInfo) -> None:
        try:
            await cls._do_run2(boot_info)
        except BaseException as e:
            logger.exception("%s.do_run() got another exception", cls)
        else:
            logger.warning("%s.do_run() finished without any errors", cls)

    @classmethod
    async def _do_run2(cls, boot_info: BootInfo) -> None:
        with child_process_logging(boot_info):
            endpoint_name = cls.get_endpoint_name()
            event_bus_service = AsyncioEventBusService(
                boot_info.trinity_config,
                endpoint_name,
            )
            async with background_asyncio_service(event_bus_service):
                event_bus = await event_bus_service.get_event_bus()

                try:
                    if boot_info.profile:
                        with profiler(f'profile_{cls.get_endpoint_name()}'):
                            await cls.do_run(boot_info, event_bus)
                    else:
                        await cls.do_run(boot_info, event_bus)
                except KeyboardInterrupt:
                    logger.warning("%s got KeyboardInterrupt, returning", cls)
                    return
                except BaseException as e:
                    logger.exception("%s got another exception: %r", cls)
                else:
                    logger.warning("%s finished without any errors", cls)

    @classmethod
    @abstractmethod
    async def do_run(self, boot_info: BootInfo, event_bus: EndpointAPI) -> None:
        """
        Define the entry point of the component. Should be overwritten in subclasses.
        """
        ...
