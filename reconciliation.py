import argparse
from pathlib import Path


def main(filepath):
    with open(filepath, "r") as file1:
        positions = {}
        transactions = {}
        day = ""
        section = ""
        while True:
            line = file1.readline()
            if not line:
                break
            elif line.strip() == "":
                continue

            if "-POS" in line or "-TRN" in line:
                section = line.split("-")[1].strip()
                day = str(line.split("-")[0].split("D")[1])
            elif section == "POS":
                if day not in positions:
                    positions[day] = {}
                symbol = line.split()[0]
                shares = float(line.split()[1])
                positions[day][symbol] = shares
            elif section == "TRN":
                if day not in transactions:
                    transactions[day] = []
                transactions[day].append(line.split())

    update_activity(positions, transactions)


def update_activity(positions, transactions):
    positions_copy = {}
    for day in transactions:
        previous_day = str(int(day) - 1)
        positions_copy[day] = positions[previous_day].copy()

        for trans in transactions[day]:
            position_day = positions_copy[day]
            symbol = trans[0]
            action = trans[1]
            shares = float(trans[2])
            value = float(trans[3])

            if symbol != "Cash":
                if symbol not in position_day:
                    position_day[symbol] = 0

                if action == "SELL":
                    position_day[symbol] -= shares
                    position_day["Cash"] += value

                    if position_day[symbol] == 0:
                        del position_day[symbol]

                elif action == "BUY":
                    position_day[symbol] += shares
                    position_day["Cash"] -= value

                elif action == "DIVIDEND":
                    position_day["Cash"] += value

            else:
                if symbol not in position_day:
                    position_day["Cash"] = 0

                if action == "DEPOSIT":
                    position_day["Cash"] += value

                elif action == "FEE":
                    position_day["Cash"] -= value

    reconcile(positions, positions_copy)


def reconcile(positions, positions_copy):
    diff = {}
    for day in positions_copy:
        copy_day = positions_copy[day]

        for symbol in copy_day:
            original_day = positions[day]
            if symbol not in original_day:
                diff[symbol] = format_number(0 - copy_day[symbol])
            elif copy_day[symbol] != original_day[symbol]:
                difference = original_day[symbol] - copy_day[symbol]
                diff[symbol] = format_number(difference)

        for symbol in original_day:
            if symbol not in copy_day:
                diff[symbol] = format_number(original_day[symbol])
            elif copy_day[symbol] != original_day[symbol]:
                difference = format_number(original_day[symbol] - copy_day[symbol])
                diff[symbol] = format_number(difference)

    write_output(diff)


def write_output(diff):
    with open("recon.out", "w") as output_file:
        header = "---------\n"
        lines = ""
        for symbol in diff:
            lines += symbol + " " + str(diff[symbol]) + "\n"

        output_file.write(header + lines)


def format_number(num):
    return int(num) if float(num).is_integer() else num


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file_path", type=Path)
    p = parser.parse_args()
    if p.file_path.exists():
        main(p.file_path)
