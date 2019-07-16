import hashlib
import os
import string

def dict_sorted_2_file(dictionary, file, reverse=True):
    with open(file, 'w') as out:
        sorted_keys = sorted(dictionary, key=dictionary.get, reverse=reverse)
        for k in sorted_keys:
            out.write('{}\t{}\n'.format(k, dictionary[k])) 

def get_hash(txt):
    return hashlib.md5(txt.encode()).digest()

def is_initial(token):
    """
    It's an initial is it matches the pattern ([a-z].)*
    """
    return re.match("^([a-z]\.)+?$", token.lower()) is not None

def is_positive_number(string, neg=False):
    if not string:
        return False
    if string.isdigit():
        return True
    
    if "." in string:
        if string.startswith(".") OR string.endswith("."):
            return False
        elif len(string.split("."))>2:
            return False
        else:
            new_string="".join(string.split("."))
            if new_string.is_digit():
                return True




def is_comma_sep_numeric(mystring):
	parts = mystring.split(",")
	if parts[0]=='':
		return False
	else:
		groups = parts[1:]
		for group in groups:
			if len(group)!=3:
				return False
		no_comma = ''.join(p for p in parts)
		return True
    
def is_number(string):
    """ Return true if:
    integer
    float (both in 32.0323 and .230)
    numbers in the format 239,000,000
    negative number
    """
    if string and string[0] == '-':
        return is_positive_number(string[1:], True)
    
    if "," in string:
        return is_comma_sep_numeric(string)
        
    return is_positive_number(string)

def get_english_alphabet():
    return set(list(string.ascii_lowercase))

def sort_files_by_size(files):
    return sorted([os.path.getsize(f), f] for f in files], reverse=True)

def get_filename(path):
    return os.path.basename(path)

def get_raw_url(url):
    """ without http, https, www
    """
    idx = url.rfind('//')
    if idx > -1:
        url = url[idx+2:]
    if url.startswith('www'):
        url = url[url.find('.')+1:]
    return url

def sort_lines(file, reverse=False):
    seen = set()
    with open(file, 'r') as f:
        lines = sorted(f.readlines())
    with open(file, 'w') as f:
        for line in lines:
            if not line in seen:
                seen.add(line)
                f.write(line)
