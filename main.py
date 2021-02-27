from typing import *
from dataclasses import dataclass
import random
import sys
from collections import defaultdict
import numpy as np


@dataclass
class Street:
    i_start: int
    i_end: int
    name: str
    time_for_a_car_to_travel: int

    cards_on_road: List['Car']

    def add_car(self, car: 'Car'):
        car.ttl = self.time_for_a_car_to_travel
        self.cards_on_road.append(car)

    def pop_waiting_car(self) -> Optional['Car']:
        if self.cards_on_road and self.cards_on_road[0].ttl == 0:
            return self.cards_on_road.pop(0)

    def update(self):
        for car in self.cards_on_road:
            car.ttl = max(0, car.ttl - 1)


@dataclass
class Car:
    street_schedule: List[str]
    ttl: int


@dataclass
class Intersection:
    id: int
    in_streets: Dict[str, Street]
    out_streets: Dict[str, Street]

    schedule: List[Tuple[str, int]]

    active: Optional[str] = None
    _possibilities: Set[str] = None

    def init(self):
        self._possibilities = set(self.in_streets.keys())

    def acquire(self, in_street, t):
        if in_street in self._possibilities:
            self.active = in_street
            self._possibilities.remove(in_street)
            self.schedule.append((in_street, t))

    def update(self, t: int, duration: int):
        # STRATEGY

        if self._possibilities:
            if random.random() < 30.0 / duration:
                street_with_max_cars = None
                max_cars = 1
                for street_name in self._possibilities:
                    street = self.in_streets[street_name]
                    cars_on_the_street = len(street.cards_on_road)
                    if cars_on_the_street >= max_cars:
                        max_cars = cars_on_the_street
                        street_with_max_cars = street_name

                if street_with_max_cars:
                    self.acquire(street_with_max_cars, t=t)

        # END STRATEGY

        for street in self.in_streets.values():
            street.update()

        if self.active:
            in_street = self.in_streets[self.active]
            if in_street.cards_on_road:
                car = in_street.pop_waiting_car()
                if car:
                    if car.street_schedule:
                        out_street = car.street_schedule.pop(0)
                        self.out_streets[out_street].add_car(car)

    def to_submission(self, duration) -> List[Tuple[str, int]]:
        if not self.schedule:
            # Fill not activated intersections
            for t, s in enumerate(self.in_streets.keys()):
                self.schedule.append((s, t))

        start_times = []
        for street, started_at in self.schedule:
            start_times.append(started_at)

        start_times.append(duration)

        fmt = []
        for (street, started_at), ended_at in zip(self.schedule, start_times[1:]):
            fmt.append((street, ended_at - started_at))

        return fmt

    def to_submission2(self, duration) -> List[Tuple[str, int]]:
        out = []
        input_streets = list(self.in_streets.values())

        random.shuffle(input_streets)

        total_used_times = 0
        for street in input_streets:
            used_times = STREETS_COUNTER[street.name]
            if used_times > 0:
                total_used_times += used_times

        for street in input_streets:
            used_times = STREETS_COUNTER[street.name]
            if used_times > 0:
                k = float(used_times / total_used_times)
                d = int(1.5 + used_times // 550)

                if d > 0:
                    out.append((street.name, d))

        """
        random.shuffle(input_streets)
        for street in input_streets:
            if street.name in USED_STREETS:
                street_duration = 1

                if random.random() < 0.1:
                    street_duration = 2

                if street_duration > 0:
                    out.append((street.name, street_duration))
        """

        if not out:
            out.append((input_streets[0].name, 1))

        return out


def solve(duration: int,
          n_cars: int,
          bonus_points: int,
          streets: Dict[str, Street],
          intersections: Dict[int, Intersection]):

    for intersection in intersections.values():
        intersection.init()

    print('Starting simulations')
    for t in range(duration):
        if t % 1000 == 0:
            print(f't={t}')
        for intersection in intersections.values():
            intersection.update(t, duration)


USED_STREETS = set()
STREETS_COUNTER = defaultdict(int)


def main(filename: str):
    print(f'Solving {filename}')
    with open(filename, encoding='utf-8') as f:
        duration, n_intersections, n_streets, n_cars, bonus_points = \
            list(map(int, f.readline().strip().split()))

        streets = {}
        intersections: Dict[int, Intersection] = {}

        for i in range(n_streets):
            i_start, i_end, name, time = f.readline().split()
            street = Street(
                int(i_start),
                int(i_end),
                name,
                int(time),
                cards_on_road=[]
            )

            streets[name] = street

            if street.i_start not in intersections:
                intersections[street.i_start] = Intersection(
                    id=street.i_start,
                    in_streets={},
                    out_streets={},
                    active=None,
                    schedule=[]
                )

            if street.i_end not in intersections:
                intersections[street.i_end] = Intersection(
                    id=street.i_end,
                    in_streets={},
                    out_streets={},
                    active=None,
                    schedule=[]
                )

            intersections[street.i_start].out_streets[street.name] = street
            intersections[street.i_end].in_streets[street.name] = street

        for i in range(n_cars):
            car = Car(f.readline().split()[1:], 0)

            # Place car at the end of the street
            streets[car.street_schedule.pop(0)].add_car(car)

            for scheduled_street in car.street_schedule:
                USED_STREETS.add(scheduled_street)
                STREETS_COUNTER[scheduled_street] += 1

        #solve(duration, n_cars, bonus_points, streets, intersections)

    run_name = sys.argv[1]
    with open(f'{run_name}.{filename}.out.txt', 'w', encoding='utf-8') as f:
        """
        submissions = []    
        for intersection in intersections.values():
            intersection_submission = intersection.to_submission2(duration=duration)
            if intersection_submission:
                submissions.append(intersection_submission)
        """

        f.write(str(len(intersections)))
        f.write('\n')
        for intersection in intersections.values():
            f.write(str(intersection.id))
            f.write('\n')

            intersection_submission = intersection.to_submission2(duration=duration)
            f.write(str(len(intersection_submission)))
            f.write('\n')
            for street_name, time in intersection_submission:
                f.write(f'{street_name} {time}')
                f.write('\n')


if __name__ == '__main__':
    main('a.txt')
    main('b.txt')
    main('c.txt')
    main('d.txt')
    main('e.txt')
    main('f.txt')
