from collections import OrderedDict


def sort_file_alphabetically(in_file_path, out_file_path: str = None, unique_lines_fp: str = None):
    out_file_path = in_file_path if out_file_path is None else out_file_path

    with open(in_file_path, 'r') as file:
        lines = file.readlines()  # Read all lines from the file
    
    lines.sort()  # Sort the lines in alphabetical order

    if unique_lines_fp:
        unique_lines = list(OrderedDict.fromkeys(lines))
    
    with open(out_file_path, 'w') as file:
        file.writelines(lines)  # Write the sorted lines back to the file

    if unique_lines_fp:
        with open(unique_lines_fp, 'w') as file:
            file.writelines(unique_lines)  # Write the sorted lines back to the file

if __name__ == "__main__":
    # sort_file_alphabetically('players/players.csv', 'players/sorted_players.csv', 'players/unique_sorted_players.csv')
    sort_file_alphabetically('players/usp.csv', 'players/sorted_usp.csv', 'players/ususp.csv')