import re
import os

def fix_file(filepath):
    try:
        lines = []
        
        file = open(filepath, 'r')
        lines = file.readlines()
        file.close()

        year = os.path.basename(filepath)[:4]

        f = open(filepath, "w")
        for line in lines:
            if (line.rstrip() == f"tags: [{year}]"):
                line = f'tags: ["{year}"]\n'
            f.write(line)
        f.close()

    except Exception as e:
        print(f"Error reading file {filepath}: {str(e)}")

def fix_dir(directory):
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)

        # Check if it is a file or a directory
        if os.path.isfile(filepath):
            fix_file(filepath)
        elif os.path.isdir(filepath):
            fix_dir(filepath)

def main():
    fix_dir("_posts")

if __name__ == "__main__":
    main()