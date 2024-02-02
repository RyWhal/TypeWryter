import os
from datetime import date
import requests
import subprocess
import socket
import random
import re

def get_random_name():
    adjectives = [
        "quick", "lazy", "sleepy", "noisy", "hungry", "bright", "brave", "calm", "dainty", "eager",
        "fancy", "gentle", "happy", "jolly", "kind", "lively", "merry", "nice", "proud", "silly",
        "tall", "short", "long", "small", "large", "tiny", "huge", "fat", "thin", "round",
        "flat", "sharp", "soft", "hard", "smooth", "rough", "cold", "hot", "warm", "cool",
        "wet", "dry", "heavy", "light", "dark", "bright", "loud", "quiet", "weak", "strong",
        "sad", "joyful", "angry", "peaceful", "excited", "bored", "busy", "lazy", "careful", "careless",
        "cheap", "expensive", "rich", "poor", "clean", "dirty", "deep", "shallow", "early", "late",
        "easy", "difficult", "empty", "full", "good", "bad", "hard", "soft", "high", "low",
        "important", "trivial", "interesting", "boring", "kind", "cruel", "loose", "tight", "major", "minor",
        "new", "old", "open", "closed", "public", "private", "quiet", "loud", "rare", "common",
        "safe", "dangerous", "shy", "outgoing", "single", "married", "slow", "fast", "small", "big",
        "smooth", "rough", "soft", "hard", "solid", "liquid", "sour", "sweet", "spicy", "bland",
        "spring", "autumn", "summer", "winter", "tall", "short", "thick", "thin", "tight", "loose",
        "warm", "cool", "wet", "dry", "young", "old", "happy", "sad", "beautiful", "ugly",
        "rich", "poor", "smart", "stupid", "funny", "serious", "healthy", "sick", "strong", "weak",
        "friendly", "hostile", "generous", "stingy", "honest", "deceitful", "loyal", "treacherous", "brave", "cowardly",
        "calm", "anxious", "content", "dissatisfied", "eager", "reluctant", "excited", "apathetic", "fearful", "bold",
        "grateful", "ungrateful", "hopeful", "pessimistic", "innocent", "guilty", "joyful", "mournful", "keen", "indifferent",
        "lively", "lethargic", "motivated", "unmotivated", "optimistic", "cynical", "passionate", "dispassionate", "quiet", "boisterous",
        "rational", "irrational", "sensible", "foolish", "thoughtful", "thoughtless", "understanding", "unreasonable", "vibrant", "dull",
        "spunky"
    ]

    animals = [
        "aardvark", "albatross", "alligator", "alpaca", "ant", "anteater", "antelope", "ape", "armadillo", "donkey",
        "baboon", "badger", "barracuda", "bat", "bear", "beaver", "bee", "bison", "boar", "buffalo",
        "butterfly", "camel", "capybara", "caribou", "cassowary", "cat", "caterpillar", "cattle", "chamois", "cheetah",
        "chicken", "chimpanzee", "chinchilla", "clam", "cobra", "cockroach", "cod", "coyote", "crab", "crane",
        "crocodile", "crow", "deer", "dinosaur", "dog", "dolphin", "dove", "dragonfly", "duck", "eagle",
        "echidna", "eel", "elephant", "elk", "emu", "falcon", "ferret", "finch", "fish", "flamingo",
        "fly", "fox", "frog", "gazelle", "gerbil", "giraffe", "gnat", "gnu", "goat", "goose",
        "goldfish", "gorilla", "grasshopper", "grouse", "guineapig", "gull", "hamster", "hare", "hawk", "hedgehog",
        "heron", "herring", "hippopotamus", "hornet", "horse", "hummingbird", "hyena", "ibex", "iguana", "jackal",
        "jaguar", "jay", "jellyfish", "kangaroo", "koala", "komododragon", "kookaburra", "lemur", "leopard", "lion",
        "llama", "lobster", "locust", "loris", "louse", "lyrebird", "magpie", "mallard", "manatee", "mandrill",
        "marmoset", "marten", "meerkat", "mink", "mole", "mongoose", "monkey", "moose", "mosquito", "mouse",
        "mule", "narwhal", "newt", "nightingale", "octopus", "okapi", "opossum", "oryx", "ostrich", "otter",
        "owl", "ox", "oyster", "panda", "panther", "parrot", "partridge", "peafowl", "pelican", "penguin",
        "pheasant", "pig", "pigeon", "platypus", "pony", "porcupine", "porpoise", "prairie dog", "quail", "quelea",
        "quokka", "quoll", "rabbit", "raccoon", "rat", "rattlesnake", "reindeer", "rhinoceros", "rook", "salamander",
        "salmon", "sand dollar", "sandpiper", "sardine", "scorpion", "seahorse", "seal", "shark", "sheep", "shrew",
        "skunk", "snail"
    ]
    animal = animals[random.randint(0, 171)]
    adjective = adjectives[random.randint(0, 199)]
    today = date.today().isoformat()
    short_name = adjective + "_" + animal
    filename_string = today + "_" + adjective + "_" + animal 
    print(filename_string)
    return filename_string,short_name


def ensure_freewrites_directory():
    freewrites_dir = os.path.join(os.getcwd(), "TypeWrytes")
    if not os.path.exists(freewrites_dir):
        os.makedirs(freewrites_dir)
    return freewrites_dir


# Function to shorten URL using TinyURL
def shorten_url(long_url):
    # First, verify that the URL contains the redirect_uri parameter
    if "redirect_uri=" not in long_url:
        print("Error: redirect_uri parameter is missing in the URL.")
        return None

    api_url = f"http://tinyurl.com/api-create.php?url={long_url}"
    response = requests.get(api_url)
    return response.text

def generate_qr_code(url):
    try:
        # Shell out to bash to run qrencode
        command = ['bash', '-c', f'echo "{url}" | qrencode -t UTF8']

        # Execute the command and capture the output
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, text=True)
        return result.stdout.splitlines()  # Split the output into lines
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")
        return None

def get_local_ip_address():
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        # Connect to an external server (does not actually create a connection)
        s.connect(("8.8.8.8", 80))  # Google DNS as an example
        local_ip = s.getsockname()[0] # Get the local IP address
    return local_ip

def clean_empty_files():
    dir = os.path.join(os.path.dirname(__file__), 'TypeWrytes')
    files = [f for f in os.listdir(dir) if f.endswith('.txt')]
    # for all files check if size is zero and delete if so
    for filename in files:
        filepath = os.path.join(dir, filename)
        if os.path.getsize(filepath) == 0:
            os.remove(filepath)