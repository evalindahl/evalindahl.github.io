import re
import os

def replace_image_path(match):
    return ""
    # return f"![]({{{ match.group(0).split('/').pop() | relative_url }}})"

def replace_image_link(image_path):
    # Define the pattern to match
    pattern = r'\/assets\/img\/(.*?(?:\.jpg|$))'

    # ![]({{ '/assets/img/eva-portrait.jpg'  | relative_url }})
    replaced_string = re.sub(pattern, lambda match: "{{ '" + match.group() + "'  | relative_url }}", image_path)

    return replaced_string

def fix_file(filepath):
    try:
        lines = []
        
        file = open(filepath, 'r')
        lines = file.readlines()
        file.close()

        f = open(filepath, "w")
        for line in lines:
            if (line.rstrip().startswith("![](")):
                line = replace_image_link(line)
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