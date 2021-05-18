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
        light_agent = None
        for addr, agent in self.agents.items():
            if not light_agent:
                light_agent = agent["object"]
            else:
                if agent["weight"] < light_agent["weight"]:
                    light_agent = agent["object"]
        return light_agent

    def _get_worker_weight(self, worker):
        if not isinstance(self.jobs[worker], list):


    def _register_job(self, agent, job_id):
        if not isinstance(self.jobs[agent], list):
            self.jobs[agent] = []
        self.jobs[agent].append(job_id)

    def worker(self):
        worker = self._find_agent()
        job_id = str(uuid.uuid4())
        worker["weight"] = (worker["weight"] + 1)
        return worker["object"].addr, job_id

    def done(self, addr):
        worker = self.agents[addr]
        if worker["weight"] > 0:
            worker["weight"] = (worker["weight"] - 1)
        else:
            self.log.warn("Agent [%s] already has weight of 0 somehow... not lowering." % addr)
