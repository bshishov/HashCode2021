from typing import *
from dataclasses import dataclass
import random


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

    def pop_car(self) -> Optional['Car']:
        if self.cards_on_road:
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

    def update(self, t):
        if self._possibilities:
            self.acquire(random.choice(list(self._possibilities)), t)

        for street in self.in_streets.values():
            street.update()

    def to_submission(self, duration) -> List[Tuple[str, int]]:
        start_times = []
        for street, started_at in self.schedule:
            start_times.append(started_at)

        start_times.append(duration)

        fmt = []
        for (street, started_at), ended_at in zip(self.schedule, start_times[1:]):
            fmt.append((street, ended_at - started_at))

        return fmt


def solve(duration: int,
          n_cars: int,
          bonus_points: int,
          streets: Dict[str, Street],
          intersections: Dict[int, Intersection]):

    for intersection in intersections.values():
        intersection.init()

    print('Starting simulations')
    for t in range(duration):
        for intersection in intersections.values():
            intersection.update(t)


def main():
    filename = 'b.txt'
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
            streets[car.street_schedule[0]].add_car(car)

        solve(duration, n_cars, bonus_points, streets, intersections)

    with open(f'{filename}.out.txt', 'w', encoding='utf-8') as f:
        f.write(str(len(intersections)))
        f.write('\n')
        for intersection in intersections.values():
            f.write(str(intersection.id))
            f.write('\n')

            intersection_submission = intersection.to_submission(duration=duration)
            f.write(str(len(intersection_submission)))
            f.write('\n')
            for street_name, time in intersection_submission:
                f.write(f'{street_name} {time}')
                f.write('\n')


if __name__ == '__main__':
    main()
