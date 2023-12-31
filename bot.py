import os, argparse, random, shutil, tweepy

attempts = 1
MAX_ATTEMPTS = 3
return_message = ""

# Create a parser to handle the command line arguments.
parser = argparse.ArgumentParser()

# Define all the command line arguments.
parser.add_argument('API_KEY', help = "name of the environment variable storing the API key")
parser.add_argument('API_SECRET', help = "name of the environment variable storing the API secret")
parser.add_argument('ACCESS_TOKEN', help = "name of the environment variable storing the access token")
parser.add_argument('ACCESS_TOKEN_SECRET', help = "name of the environment variable storing the access token secret")
parser.add_argument('image_folder_path', help = "path to the folder containing the images")
parser.add_argument('--append_name', dest = 'append_name', action = 'store_true', help = "append image name to the tweet")
parser.add_argument('--quotes', dest = 'add_quotes', action = 'store_true', help = "add quotes around the tweet text")
parser.add_argument('--exclude_text', dest = 'image_name_to_exclude', help = "images starting with this text will not have their name appended to the Tweet")
parser.add_argument('--old_text', metavar = 'old', dest = 'old_text', nargs = '+', help = "replace these strings with the corresponding --new_text strings in the image name")
parser.add_argument( '--new_text', metavar = 'new', dest = 'new_text', nargs = '+', help = "replace the corresponding --old_text strings in the image name")

# Get all the provided command line arguments.
args = parser.parse_args()

# Check the validity of the provided command line arguments.
API_KEY = os.getenv(args.API_KEY)
if API_KEY == None:
    raise Exception(
        args.API_KEY + " is not a valid environment variable."
    )
API_SECRET = os.getenv(args.API_SECRET)
if API_SECRET == None:
    raise Exception(
        args.API_SECRET + " is not a valid environment variable."
    )
ACCESS_TOKEN = os.getenv(args.ACCESS_TOKEN)
if ACCESS_TOKEN == None:
    raise Exception(
        args.ACCESS_TOKEN + " is not a valid environment variable."
    )
ACCESS_TOKEN_SECRET = os.getenv(args.ACCESS_TOKEN_SECRET)
if ACCESS_TOKEN_SECRET == None:
    raise Exception(
        args.ACCESS_TOKEN_SECRET + " is not a valid environment variable."
    )

if not os.path.isdir(args.image_folder_path):
    raise Exception(
        "Specified directory does not exist."
    )

if not args.old_text == None:
    if not args.new_text == None:
        if len(args.old_text) != len(args.new_text):
            raise Exception(
                "-old_text and -new_text do not contain corresponding elements."
            )


# Change the current working directory to the image folder.
os.chdir(args.image_folder_path)

# List the names of all the files (not including folders) in the current working directory.
images = [i for i in os.listdir() if os.path.isfile(os.path.join(os.getcwd(), i))]

if len(images) == 0:
    raise Exception(
        "No more images to post."
    )


while attempts <= MAX_ATTEMPTS:
    try:
        # Pick a random image from the list of all images.
        image = random.choice(images)


        # Authenticate for both v1.1 and v2 of the Twitter API as it is currently not possible to post a tweet with an image directly.
        # v1.1 of the API is used to upload an image. The id of this uploaded image is then appended to v2 to post a tweet with an image.
        auth = tweepy.OAuth1UserHandler(API_KEY, API_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api_v1 = tweepy.API(auth)
        api_v2 = tweepy.Client(consumer_key = API_KEY, consumer_secret = API_SECRET, access_token = ACCESS_TOKEN, access_token_secret = ACCESS_TOKEN_SECRET)


        # Upload the chosen image and retrieve its id.
        uploaded_image = api_v1.media_upload(filename = image)
        uploaded_image_id = uploaded_image.media_id


        # Format the image name to remove the file extension and apply the specified formatting.
        formatted_image_name = ""
        if args.append_name:
            if not image.startswith(args.image_name_to_exclude if args.image_name_to_exclude else "/"):
                formatted_image_name += os.path.splitext(image)[0]
                if args.add_quotes:
                    formatted_image_name = "".join(['"', formatted_image_name, '"'])
                if not args.old_text == None:
                    if not args.new_text == None:
                        for i in range(len(args.old_text)):
                            formatted_image_name = formatted_image_name.replace(args.old_text[i], args.new_text[i])


        # Post the tweet containing the image and the formatted name.
        api_v2.create_tweet(text = formatted_image_name, media_ids = [uploaded_image_id])

    except Exception as e:
        return_message += "Attempt " + str(attempts) + "\tFailed to post: " + os.getcwd() + "/" + image + "\t" + repr(e) + "\n"
        attempts += 1

    else:
        return_message += "Attempt " + str(attempts) + "\tSuccessfully posted: " + os.getcwd() + "/" + image
        # Move the successfully posted image into a new folder, excluding it from being posted again.
        if not os.path.isdir('posted'):
            os.mkdir('posted')
        shutil.move(os.getcwd() + "/" + image, os.getcwd() + '/posted/' + image)
        break

print(return_message)