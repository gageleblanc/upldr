from clilib.util.util import Util
from .agent_object import AgentObject
import uuid


class Scheduling:
    def __init__(self):
        self.agents = {}
        self.jobs = {}
        self.log = Util.configure_logging(name=__name__)

    def add_agent(self, agent: AgentObject):
        self.log.info("Adding [%s] to scheduling" % agent.addr)
        self.agents[agent.addr] = {
            "weight": 0,
            "object": agent
        }

    def del_agent(self, addr):
        self.log.warn("Removing agent [%s] from scheduling" % addr)
        del self.agents[addr]

    def _find_agent(self):
        return min(self.jobs, key=self.jobs.get)

    def _get_worker_weight(self, worker):
        if not isinstance(self.jobs[worker], list):
            self.jobs[worker] = []
        return len(self.jobs[worker])

    def _register_job(self, agent, job_id):
        if not isinstance(self.jobs[agent], list):
            self.jobs[agent] = []
        self.jobs[agent].append(job_id)

    def worker(self):
        worker = self._find_agent()
        job_id = str(uuid.uuid4())
        self._register_job(worker, job_id)
        worker["weight"] = (worker["weight"] + 1)
        return worker["object"].addr, job_id

    def done(self, addr, job_id):
        worker = self.agents[addr]
        self.jobs[worker].remove(job_id)
        if worker["weight"] > 0:
            worker["weight"] = (worker["weight"] - 1)
        else:
            self.log.warn("Agent [%s] already has weight of 0 somehow... not lowering." % addr)
