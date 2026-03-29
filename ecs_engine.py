#!/usr/bin/env python3
"""ecs_engine - Entity Component System with queries and system scheduling."""
import sys
from collections import defaultdict

class World:
    def __init__(self):
        self._next_id = 0
        self.components = defaultdict(dict)  # comp_type -> {entity_id: data}
        self.entities = set()
        self.systems = []
    def spawn(self, **components):
        eid = self._next_id; self._next_id += 1
        self.entities.add(eid)
        for comp, data in components.items():
            self.components[comp][eid] = data
        return eid
    def despawn(self, eid):
        self.entities.discard(eid)
        for store in self.components.values():
            store.pop(eid, None)
    def get(self, eid, comp):
        return self.components[comp].get(eid)
    def set(self, eid, comp, data):
        self.components[comp][eid] = data
    def query(self, *comp_types):
        if not comp_types: return []
        sets = [set(self.components[c].keys()) for c in comp_types]
        matching = sets[0]
        for s in sets[1:]: matching &= s
        return [(eid, tuple(self.components[c][eid] for c in comp_types)) for eid in matching]
    def add_system(self, system):
        self.systems.append(system)
    def tick(self, dt=1.0):
        for system in self.systems:
            system(self, dt)

def test():
    w = World()
    e1 = w.spawn(pos=[0,0], vel=[1,2], health=100)
    e2 = w.spawn(pos=[5,5], vel=[-1,0])
    e3 = w.spawn(pos=[3,3], health=50)
    q = w.query("pos", "vel")
    assert len(q) == 2
    def move_system(world, dt):
        for eid, (pos, vel) in world.query("pos", "vel"):
            world.set(eid, "pos", [pos[0]+vel[0]*dt, pos[1]+vel[1]*dt])
    w.add_system(move_system)
    w.tick(1.0)
    assert w.get(e1, "pos") == [1, 2]
    assert w.get(e2, "pos") == [4, 5]
    assert w.get(e3, "pos") == [3, 3]  # no vel, unchanged
    w.despawn(e2)
    assert len(w.query("pos", "vel")) == 1
    print("ecs_engine: all tests passed")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("Usage: ecs_engine.py --test")
