from dataclasses import dataclass


@dataclass
class Street:
    i_start: int
    i_end: int
    name: str
    time: int


def solve(duration, n_intersections, n_cars, bonus_points, streets):
    print(duration, n_intersections, n_cars, bonus_points, streets)
    print(streets)


def main():
    filename = 'a.txt'
    print(f'Solving {filename}')
    with open(filename, encoding='utf-8') as f:
        duration, n_intersections, n_streets, n_cars, bonus_points = \
            list(map(int, f.readline().strip().split()))

        streets = []
        for i in range(n_streets):
            i_start, i_end, name, time = f.readline().split()
            streets.append(Street(
                int(i_start),
                int(i_end),
                name,
                time
            ))
        solve(duration, n_intersections, n_cars, bonus_points, streets)


if __name__ == '__main__':
    main()
