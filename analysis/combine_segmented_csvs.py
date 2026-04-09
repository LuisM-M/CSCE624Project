import os
import csv

INPUT_FOLDER = "analysis/data/processed"
OUTPUT_FILE = "analysis/data/processed/all_segmented_trials.csv"


def get_segmented_files(folder):
    files = []

    for filename in os.listdir(folder):
        full_path = os.path.join(folder, filename)

        if not os.path.isfile(full_path):
            continue

        if not filename.endswith(".csv"):
            continue

        if filename == os.path.basename(OUTPUT_FILE):
            continue

        if filename.endswith("_segmented_trials.csv"):
            files.append(full_path)

    return sorted(files)


def combine_csvs(input_files, output_file):
    if not input_files:
        print("No segmented CSV files found.")
        return

    header_written = False

    with open(output_file, "w", newline="", encoding="utf-8") as outfile:
        writer = None

        for file in input_files:
            print(f"Adding: {file}")

            with open(file, "r", newline="", encoding="utf-8") as infile:
                reader = csv.reader(infile)

                try:
                    header = next(reader)
                except StopIteration:
                    print(f"Skipping empty file: {file}")
                    continue

                if not header_written:
                    writer = csv.writer(outfile)
                    writer.writerow(header)
                    header_written = True

                for row in reader:
                    if row:
                        writer.writerow(row)

    print(f"\nCombined CSV saved to:\n{output_file}")
    print(f"Total files combined: {len(input_files)}")


def main():
    if not os.path.exists(INPUT_FOLDER):
        print(f"Processed folder not found: {INPUT_FOLDER}")
        return

    input_files = get_segmented_files(INPUT_FOLDER)

    if len(input_files) == 0:
        print("No participant CSVs found in processed folder.")
        return

    combine_csvs(input_files, OUTPUT_FILE)


if __name__ == "__main__":
    main()